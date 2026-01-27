import logging
from datetime import datetime, time

import httpx
from odoo import models, fields, _, api, Command
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ModificaMatricolaRegAccesso(models.TransientModel):
    _name = 'ca.modifica_matricola_registro_accesso'
    _description = 'Modifica Matricola Registro Accesso'

    # _transient_max_count = 0 # Do not delete record when vacuum
    # _transient_max_hours = 0 # Do not delete record when vacuum

    tipo_periodo = fields.Selection(string="Period Type", selection=[("period", "Period (from)"), ("day", "Day")], required=True)
    data_riferimento = fields.Date(string="Reference Date", required=True)
    ca_persona_id = fields.Many2one("ca.persona", required=True,
                                    domain="[('person_access_ids', '!=', False)]")
    work_id_number = fields.Char(string='ID Number')

    line_ids = fields.One2many("ca.modifica_matricola_registro_accesso_line",
                               "ca_modifica_matricola_registro_accesso_id", string="Lines")

    aggiornamento_work_id_number = fields.Many2one("ca.work_info", string="Update ID Number",
                                                   domain="[('ca_persona_id', '=', ca_persona_id), ('state', '=', 'active')]")

    is_confirmed = fields.Boolean(string="Is Confirmed", default=False)
    success_msg = fields.Char(string="Success Message", readonly=True)
    error_msg = fields.Char(string="Error Message", readonly=True)
    is_success = fields.Boolean(compute="_compute_is_success", readonly=True, store=True)
    is_error = fields.Boolean(compute="_compute_is_success", readonly=True, store=True)

    @api.depends('ca_persona_id')
    def _compute_aggiornamento_work_id_number(self):
        for record in self:
            CaWorkInfo = self.env['ca.work_info']
            active_winfo = CaWorkInfo.search([
                ("ca_persona_id", "=", record.ca_persona_id.id),
                ("state", "=", "active"),
            ])
            if active_winfo:
                record.aggiornamento_work_id_number = active_winfo
            else:
                record.aggiornamento_work_id_number = False

    @api.depends('is_confirmed', 'error_msg')
    def _compute_is_success(self):
        for record in self:
            record.is_success = record.is_confirmed and not record.error_msg
            record.is_error = record.is_confirmed and record.error_msg

    @api.onchange("tipo_periodo", "data_riferimento", "ca_persona_id", "aggiornamento_work_id_number")
    def onchange_filtri(self):
        # Does nothing if the wizard has succeded
        if self.is_success:
            return

        if not self.tipo_periodo or not self.data_riferimento or not self.ca_persona_id:
            self.line_ids = [Command.clear()]
            return

        CaAnagRegistroAccesso = self.env['ca.anag_registro_accesso']
        search_registro_domain = [
            ("ca_persona_id", "=", self.ca_persona_id.id)
        ]
        if self.tipo_periodo == "periodo":
            start = datetime.combine(self.data_riferimento, time.min)
            search_registro_domain.extend([
                ("datetime_event", ">=", start)
            ])
        else:
            start = datetime.combine(self.data_riferimento, time.min)
            end = datetime.combine(self.data_riferimento, time.max)
            search_registro_domain.extend([
                ("datetime_event", ">=", start),
                ("datetime_event", "<=", end),
            ])

        if self.aggiornamento_work_id_number:
            search_registro_domain.append(
                ("work_id_number", "!=", self.aggiornamento_work_id_number.work_id_number)
            )

        registri_accesso_ids = CaAnagRegistroAccesso.search(search_registro_domain)
        self.line_ids = [Command.clear()]
        self.line_ids = [Command.create({"ca_anag_registro_accesso_id": r.id}) for r in registri_accesso_ids]

    def action_confirm(self):
        self.ensure_one()

        url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('labinf_update_sync_service')

        if not self.line_ids:
            raise ValidationError(
                _('No access registers selected'))

        try:

            payload = {
                "uid": self.env.user.login,
                "update_work_id_number": self.aggiornamento_work_id_number.work_id_number,
                "ids": [r.ca_anag_registro_accesso_id.id for r in self.line_ids]
            }


            with httpx.Client(timeout=40) as client:
                logger.info(f"Calling {url} with body:\n{payload}")
                response = client.post(url, json=payload)

            if response.is_success:
                resp = response.json()
                self.success_msg = resp.get("message")
            else:
                logger.error(
                    f"{url}, Status Code: {response.status_code}\n{response.content}")
                self.error_msg = response.text
                resp = {}
        except Exception as e:
            logger.error(f"{url}, Error: {e}", exc_info=True)
            self.error_msg = str(e)
        finally:
            self.is_confirmed = True

            # Redirect to wizard form for response message success or error
            action = self.env["ir.actions.actions"]._for_xml_id(
                "controllo_accessi_inrim_app.ca_modifica_matricola_registro_accesso_action")
            action['res_id'] = self.id
            return action


class ModificaMatricolaRegAccessoLine(models.TransientModel):
    _name = 'ca.modifica_matricola_registro_accesso_line'
    _description = 'Linea Modifica Matricola Registro Accesso'

    # _transient_max_count = 0  # Do not delete record when vacuum
    # _transient_max_hours = 0  # Do not delete record when vacuum

    ca_modifica_matricola_registro_accesso_id = fields.Many2one("ca.modifica_matricola_registro_accesso",
                                                                required=True, ondelete="cascade")
    ca_anag_registro_accesso_id = fields.Many2one("ca.anag_registro_accesso", required=True)

    ca_punto_accesso_id = fields.Many2one(related="ca_anag_registro_accesso_id.ca_punto_accesso_id")
    ca_ente_azienda_id = fields.Many2one(related="ca_anag_registro_accesso_id.ca_ente_azienda_id")
    person_display_name = fields.Char(related="ca_anag_registro_accesso_id.person_display_name")
    datetime_event = fields.Datetime(related="ca_anag_registro_accesso_id.datetime_event")
    typology = fields.Selection(related="ca_anag_registro_accesso_id.typology")
    direction = fields.Selection(related="ca_anag_registro_accesso_id.direction")
    access_allowed = fields.Boolean(related="ca_anag_registro_accesso_id.access_allowed")
    system_error = fields.Boolean(related="ca_anag_registro_accesso_id.system_error")
    access_conflict = fields.Boolean(related="ca_anag_registro_accesso_id.access_conflict")
    codice_lettore_grum = fields.Integer(related="ca_anag_registro_accesso_id.codice_lettore_grum")
    work_id_number = fields.Char(related="ca_anag_registro_accesso_id.work_id_number")
    state = fields.Selection(related="ca_anag_registro_accesso_id.state")
