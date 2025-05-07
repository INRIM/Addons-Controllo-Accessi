import logging

import pytz
from odoo import models, fields

logger = logging.getLogger(__name__)

_tzs = [(tz, tz) for tz in sorted(
    pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


class CaAnagRegistroAccesso(models.Model):
    _name = 'ca.anag_registro_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Anagrafica Registro Accesso'
    _rec_name = 'ca_punto_accesso_id'

    ca_punto_accesso_id = fields.Many2one(
        'ca.punto_accesso', string="Access Point", required=True, ondelete='cascade')
    ca_punto_accesso_category_id = fields.Many2one(related="ca_punto_accesso_id.ca_category")
    ca_tag_persona_id = fields.Many2one(
        'ca.tag_persona', string="Tag", required=True, ondelete='cascade')
    ca_persona_id = fields.Many2one(
        related="ca_tag_persona_id.ca_persona_id", string="Person", store=True,
        readonly=True)
    person_display_name = fields.Char(
        related="ca_persona_id.display_name", store=True,
        string="Person Name", readonly=True)

    person_freshman = fields.Char(
        related="ca_persona_id.freshman", store=True, string="Person Freshman",
        readonly=True)
    ca_lettore_id = fields.Many2one(
        related="ca_punto_accesso_id.ca_lettore_id", store=True, readonly=True,
        string="Reader")
    ca_spazio_id = fields.Many2one(
        related="ca_punto_accesso_id.ca_spazio_id", store=True, string="Space",
        readonly=True)
    ca_tipo_spazio_id = fields.Many2one(
        related="ca_spazio_id.tipo_spazio_id", store=True, string="Space Type",
        readonly=True)
    ca_ente_azienda_id = fields.Many2one(
        related="ca_spazio_id.ente_azienda_id", store=True, string="Space Office",
        readonly=True)
    datetime_event = fields.Datetime(default=fields.datetime.now(), required=True)
    typology = fields.Selection(
        related="ca_punto_accesso_id.typology", store=True, string="Ap Type",
        readonly=True)
    direction = fields.Selection(
        related="ca_lettore_id.direction", store=True, readonly=True)
    access_allowed = fields.Boolean()
    system_error = fields.Boolean(
        related="ca_lettore_id.system_error", store=True,
        readonly=True)
    access_conflict = fields.Boolean(
        default=False,
        help="Access Conflict Tag Access realted to a person that is not present")
    type = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Auto')
    ], string="Insertion Type")
    tz = fields.Selection(
        _tz_get, string='Timezone',
        default=lambda self: self._context.get('tz'),
        help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
             "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
             "Anywhere else, time values are computed according to the time offset of your web client."
    )
    active = fields.Boolean(default=True)

    def aggiungi_riga_accesso(
            self, ca_punto_accesso_id,
            ca_tag_persona_id, datetime_event, type='manual', access_allowed=True,
            tz=""
    ):
        if not tz:
            tz = self._context.get('tz')
        access_conflict = False
        if self.ca_punto_accesso_id.typology == 'local_access':
            access_conflict = ca_tag_persona_id.ca_persona_id.present == 'no'
        vals = {
            'ca_punto_accesso_id': ca_punto_accesso_id.id,
            'ca_tag_persona_id': ca_tag_persona_id.id,
            'datetime_event': datetime_event,
            'type': type,
            'access_allowed': access_allowed,
            'access_conflict': access_conflict,
            'tz': tz
        }
        res = self.create(vals)
        if res.ca_punto_accesso_id.typology == "stamping":
            if res.direction == "out" and res.access_allowed:
                res.ca_persona_id.present = "no"
            if res.direction == "in" and res.access_allowed:
                res.ca_persona_id.present = "yes"
        return res

    def rest_boby_hint(self):
        return {
            "ca_punto_accesso_id": 0,
            "ca_tag_persona_id": 0,
            "datetime_event": "2020-01-01 00:00:00",
            "access_allowed": True,
            "type": "manual",
            "tz": "Europe/Rome",
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            "ca_punto_accesso_id": self.f_m2o(self.ca_punto_accesso_id),
            "ca_tag_persona_id": self.f_m2o(self.ca_tag_persona_id),
            "ca_persona_id": self.f_m2o(self.ca_persona_id),
            "person_display_name": self.person_display_name,
            "person_freshman": self.person_freshman,
            "ca_lettore_id": self.f_m2o(self.ca_lettore_id),
            "ca_spazio_id": self.f_m2o(self.ca_spazio_id),
            "ca_tipo_spazio_id": self.f_m2o(self.ca_tipo_spazio_id),
            "ca_ente_azienda_id": self.f_m2o(self.ca_ente_azienda_id),
            "datetime_event": self.f_datetime(self.datetime_event),
            "typology": self.f_selection('typology', self.typology),
            "direction": self.f_selection('direction', self.direction),
            "type": self.f_selection('type', self.type),
            "tz": self.f_selection('tz', self.tz),
            "system_error": self.system_error,
            "access_allowed": self.access_allowed,
            "error_code": self.error_code
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'ca_punto_accesso_id', 'ca_tag_persona_id', 'datetime_event',
                'access_allowed', 'type'
            ])
        return body, msg

    def rest_post(self, body: dict):
        return False, f"Non consentito"


