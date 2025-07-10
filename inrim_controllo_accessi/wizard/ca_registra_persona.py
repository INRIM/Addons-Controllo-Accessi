import logging
from datetime import datetime
from datetime import time

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CaRegistraPersona(models.TransientModel):
    _name = 'ca.registra_persona'
    _description = 'Register Person'

    vat = fields.Char()
    ca_ente_name = fields.Char("Company Name", required=True)
    tipo_ente_azienda_id = fields.Many2one(
        'ca.tipo_ente_azienda', required=True,
        domain=lambda self: self.ente_azienda_domain(),
        string="Company Type")
    ente_azienda = fields.Many2one("ca.ente_azienda", string="Company")
    fiscalcode = fields.Char(string="Fiscalcode", required=True)
    lastname = fields.Char(required=True)
    name = fields.Char(required=True)
    freshman = fields.Char(groups="controllo_accessi.ca_gdpr")
    email = fields.Char(String="Email")
    mobile = fields.Char()
    ca_work_info_type_id = fields.Many2one(
        'ca.work_info_type', required=True)
    ca_title_id = fields.Many2one(
        'ca.titolo_persona', required=True)
    persona_id = fields.Many2one("ca.persona")
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(required=True)
    parent_id = fields.Many2one(
        'ca.persona', string='Reference person', index=True
    )
    ref_domain = fields.Selection(
        [("present", "Present"), ("all", "All")], default="present", required=True)
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    available_tags_ids = fields.Many2many('ca.tag', compute="_compute_available_tags")
    ente_interno = fields.Boolean(string="Internal")
    work_id_number = fields.Char(
        string="ID Number", groups="controllo_accessi.ca_gdpr")

    parent_id_domain = fields.Binary(
        string="parent id domain",
        help="Dynamic domain used for the tag that can be set on person",
        compute="_compute_parent_domain")

    @api.depends('ref_domain')
    def _compute_parent_domain(self):
        for rec in self:
            if rec.ref_domain == 'present':
                rec.parent_id_domain = [
                    ('is_internal', '=', True), ('present', '=', 'yes')]
            else:
                rec.parent_id_domain = [('is_internal', '=', True)]

    def ente_azienda_domain(self):
        return [
            ('id', 'not in',
             [
                 self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
                 self.env.ref(
                     'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
             ])
        ]

    def eval_ente_azienda_id(self, ente_az_id):
        self.ensure_one()
        ente_az_found = self.env['ca.ente_azienda'].browse(ente_az_id)
        self.ente_azienda = ente_az_found.id
        self.ca_ente_name = ente_az_found.name
        self.tipo_ente_azienda_id = ente_az_found.tipo_ente_azienda_id
        self.vat = ente_az_found.vat
        self.ente_interno = ente_az_found.tipo_ente_azienda_id.id in [
            self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id,
        ]

    def reset_ente_azienda_id(self, ):
        self.ente_azienda = False
        self.ca_ente_name = ""
        self.vat = ""
        self.tipo_ente_azienda_id = False
        self.ente_azienda = False
        self.ente_interno = False

    @api.onchange('vat')
    def _compute_eval_vat(self):
        if self._context.get("no_change_vat"):
            return
        for record in self:
            if not record.vat:
                return
            ente_az_found = self.env['ca.ente_azienda'].search([
                ('vat', 'ilike', record.vat)], limit=1)
            if ente_az_found:
                if record.ente_azienda.id != ente_az_found.id:
                    self.with_context(
                        no_change_vat=True).eval_ente_azienda_id(ente_az_found.id)

    def populate_person(self, rec):
        self.ensure_one()
        self.name = rec.name
        self.lastname = rec.lastname
        self.freshman = rec.freshman
        self.fiscalcode = rec.fiscalcode
        self.email = rec.email
        self.persona_id = rec.id
        ent_az_id = rec.ca_ente_azienda_ids.ids[0] if rec.ca_ente_azienda_ids else []
        self.eval_ente_azienda_id(ent_az_id)
        current_winfo = self.persona_id.get_current_winfo()
        if current_winfo:
            self.ca_work_info_type_id = current_winfo.ca_work_info_type_id.id
            self.ca_title_id = current_winfo.ca_title_id.id
            self.date_start = datetime.combine(current_winfo.date_start, time(8, 0, 0))
            self.date_end = datetime.combine(current_winfo.date_end, time(18, 0, 0))
        self.compute_available_tags()

    def reset_person(self):
        self.ensure_one()
        self.name = ""
        self.lastname = ""
        self.freshman = ""
        self.email = ""
        self.persona_id = False

    def _compute_available_tags(self):

        self.compute_available_tags()

    @api.onchange("persona_id", "ca_title_id")
    def _compunte_change_penson_tile(self):
        for record in self:
            record.compute_available_tags()

    def compute_available_tags(self):
        self.ensure_one()
        logger.info(f"seacrh tag external {self.ca_title_id.structured}")
        if not self.ca_title_id.structured:
            logger.info("seacrh tag external")
            self.available_tags_ids = self.env['ca.tag'].search([
                ('in_use', '=', False),
                ('revoked', '=', False),
                ('temp', '=', True),
                ('ca_proprieta_tag_ids', 'in', [
                    self.env.ref('inrim_anagrafiche.proprieta_tag_visitatore').id,
                    self.env.ref('inrim_anagrafiche.proprieta_tag_servizio').id
                ])
            ])
            logger.info(self.available_tags_ids)
        elif self.persona_id.is_internal:
            self.available_tags_ids = self.env['ca.tag'].search([
                ('in_use', '=', False),
                ('revoked', '=', False),
                ('ca_proprieta_tag_ids', 'in', [
                    self.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id,
                    self.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
                ])
            ])


    @api.onchange('fiscalcode')
    def _compute_eval_fiscalcode(self):
        if self._context.get("no_change_person"):
            return
        for record in self:
            if not record.fiscalcode:
                return
            persona_id = self.env['ca.persona'].search([
                ('fiscalcode', '=', record.fiscalcode)], limit=1)
            if persona_id:
                if record.persona_id.id != persona_id.id:
                    self.with_context(
                        no_change_person=True,
                        no_change_vat=True).populate_person(persona_id)

    @api.onchange('ca_tag_id')
    def _compute_tag_id_number(self):
        for record in self:
            record.work_id_number = record.ca_tag_id.default_id_number
            if record.ca_tag_id.temp and not record.date_start and not record.date_end:
                now = fields.Datetime.now()
                # Costruisce oggi alle 19:30
                today_1930 = datetime.combine(now.date(), time(19, 30))
                record.date_start = now
                record.date_end = today_1930

    @api.onchange('persona_id')
    def _compute_tag_id_persona_id(self):
        if self._context.get("no_change_person"):
            return
        for record in self:
            if record.persona_id:
                self.with_context(
                    no_change_person=True,
                    no_change_vat=True).populate_person(record.persona_id)

    @api.onchange('email')
    def _compute_available_email(self):
        if self._context.get("no_change_person"):
            return
        for record in self:
            if not record.email:
                return
            persona_ids = self.env['ca.persona'].search([
                ('email', 'ilike', record.email)], limit=1)
            if len(persona_ids) == 1:
                if record.persona_id.id != persona_ids[0].id:
                    self.with_context(
                        no_change_person=True,
                        no_change_vat=True).populate_person(persona_ids[0])
            else:
                self.reset_person()

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Date end must be after date start'))
                record.compute_available_tags()

    def action_confirm(self):
        add_doc = True
        if not self.ente_azienda:
            self.ente_azienda = self.env['ca.ente_azienda'].create(
                {
                    "name": self.ca_ente_name,
                    "vat": self.vat,
                    "tipo_ente_azienda_id": self.tipo_ente_azienda_id.id
                }
            )
        if not self.persona_id:
            self.persona_id = self.env['ca.persona'].with_context(wizard_create=True).create(
                {
                    "name": self.name,
                    "lastname": self.lastname,
                    "fiscalcode": self.fiscalcode,
                    "freshman": self.freshman,
                    "mobile": self.mobile,
                    "email": self.email,
                    "parent_id": self.parent_id.id,
                    "type_ids": [self.env.ref('inrim_anagrafiche.tipo_persona_esterno').id],
                    "ca_ente_azienda_ids": self.ente_azienda.ids
                }
            )
        else:
            add_doc = False
            vals = {
                "freshman": self.freshman,
                "mobile": self.mobile,
                "email": self.email,
                "parent_id": self.parent_id.id
            }
            if self.ente_azienda.id not in self.persona_id.ca_ente_azienda_ids.ids:
                self.persona_id.ca_ente_azienda_ids = [(6, 0, self.ente_azienda.ids)]
            self.persona_id.write(vals)
        current_winfo = self.persona_id.get_current_winfo()
        if not current_winfo:
            self.env['ca.work_info'].create(
                {
                    'ca_persona_id': self.persona_id.id,
                    'work_id_number': self.freshman,
                    'ca_work_info_type_id': self.ca_work_info_type_id.id,
                    'ca_title_id': self.ca_title_id.id,
                    'date_start': self.date_start.date(),
                    'date_end': self.date_end.date()
                }
            )


        res = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_id.id,
            'ca_tag_id': self.ca_tag_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
        })
        for access_point_group in self.env['ca.punto_accesso_category'].search([]):
            for access_point in access_point_group.ca_access_point_ids:
                logger.info(f"wizard eval attach {access_point}")
                access_point.check_and_attach()
        if add_doc:
            add_doc_w = self.env['ca.registra_doc_persona'].create({
                'persona_id': self.persona_id.id,
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ca.registra_doc_persona',
                'view_mode': 'form',
                'res_id': add_doc_w.id,
                'target': 'new',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}
