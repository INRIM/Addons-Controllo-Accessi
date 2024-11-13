from odoo import models, fields, api, _


class CaRegistraOspite(models.TransientModel):
    _name = 'ca.registra_ospite'
    _description = 'Registra Ospite'

    vat = fields.Char()
    ca_ente_name = fields.Char("Company Name", required=True)
    tipo_ente_azienda_id = fields.Many2one(
        'ca.tipo_ente_azienda', required=True,
        domain=lambda self: self.ente_azienda_domain())
    ente_azienda = fields.Many2one("ca.ente_azienda")
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
        'ca.persona', string='Reference person', index=True,
        domain=[('is_internal', '=', True), ('is_structured', '=', True)]
    )
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    available_tags_ids = fields.Many2many('ca.tag', compute="_compute_available_tags")
    ente_interno = fields.Boolean(string="Interno")
    work_id_number = fields.Char(
        string="A.C. ID Numeber", groups="controllo_accessi.ca_gdpr")

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
        ente_az_found = self.env['ca.ente_azienda'].browse(ente_az_id)
        self.ente_azienda = ente_az_found
        self.ca_ente_name = ente_az_found.name
        self.tipo_ente_azienda_id = ente_az_found.tipo_ente_azienda_id
        self.ente_azienda = ente_az_found.id
        self.ente_interno = ente_az_found.tipo_ente_azienda_id.id in [
            self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id,
        ]

    def reset_ente_azienda_id(self, ):
        self.ente_azienda = False
        self.ca_ente_name = ""
        self.tipo_ente_azienda_id = False
        self.ente_azienda = False
        self.ente_interno = False

    @api.onchange('vat')
    def _compute_eval_vat(self):
        for record in self:
            if not record.vat:
                return
            ente_az_found = self.env['ca.ente_azienda'].search([
                ('vat', 'ilike', record.vat)], limit=1)
            if ente_az_found:
                self.eval_ente_azienda_id(ente_az_found)
            else:
                self.reset_ente_azienda_id()

    def populate_person(self, rec):
        self.ensure_one()
        self.name = rec.name
        self.lastname = rec.lastname
        self.freshman = rec.freshman
        self.email = rec.email
        self.persona_id = rec.id
        self.compute_available_tags()
        self.eval_ente_azienda_id(
            rec.ca_ente_azienda_ids.ids[0] if rec.ca_ente_azienda_ids else []
        )

    def reset_person(self):
        self.ensure_one()
        self.name = ""
        self.lastname = ""
        self.freshman = ""
        self.email = ""
        self.persona_id = False

    def _compute_available_tags(self):
        self.compute_available_tags()

    def compute_available_tags(self):
        self.ensure_one()
        if not self.persona_id or self.persona_id.is_external:
            self.available_tags_ids = self.env['ca.tag'].search([
                ('in_use', '=', False),
                ('revoked', '=', False),
                ('temp', '=', True),
                ('ca_proprieta_tag_ids', 'not in', [
                    self.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id,
                ])
            ])
        elif self.persona_id.is_internal:
            self.available_tags_ids = self.env['ca.tag'].search([
                ('in_use', '=', False),
                ('revoked', '=', False),
                ('temp', '=', True),
                ('ca_proprieta_tag_ids', 'in', [
                    self.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id,
                ])
            ])

    @api.onchange('fiscalcode')
    def _compute_eval_fiscalcode(self):
        for record in self:
            if not record.fiscalcode:
                return
            persona_id = self.env['ca.persona'].search([
                ('fiscalcode', 'ilike', record.fiscalcode)], limit=1)
            if persona_id:
                self.populate_person(persona_id)
            else:
                self.reset_person()

    @api.onchange('ca_tag_id')
    def _compute_tag_id_number(self):
        for record in self:
            record.work_id_number = record.ca_tag_id.default_id_number

    @api.onchange('email')
    def _compute_available_email(self):
        for record in self:
            if not record.email:
                return
            persona_ids = self.env['ca.persona'].search([
                ('email', 'ilike', record.email)])
            if len(persona_ids) == 1:
                self.populate_person(persona_ids[0])
            else:
                self.reset_person()

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))
                record.compute_available_tags()

    def action_confirm(self):
        if not self.ente_azienda:
            self.ente_azienda = self.env['ca.ente_azienda'].create(
                {
                    "name": self.ca_ente_name,
                    "vat": self.vat,
                    "tipo_ente_azienda_id": self.tipo_ente_azienda_id
                }
            )
        if not self.persona_id:
            self.persona_id = self.env['ca.persona'].create(
                {
                    "name": self.name,
                    "lastname": self.lastname,
                    "fiscalcode": self.fiscalcode,
                    "freshman": self.freshman,
                    "mobile": self.mobile,
                    "email": self.email,
                    "parent_id": self.parent_id.id,
                    "ca_ente_azienda_ids": self.ente_azienda.ids
                }
            )
        else:
            vals = {
                "freshman": self.freshman,
                "mobile": self.mobile,
                "email": self.email,
                "parent_id": self.parent_id.id
            }
            if self.ente_azienda.id not in self.persona_id.ca_ente_azienda_ids.ids:
                self.persona_id.ca_ente_azienda_ids.append(self.ente_azienda.id)
            self.persona_id.write(vals)

        res = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_id.id,
            'ca_tag_id': self.ca_tag_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
        })
        for access_point_group in self.env['ca.punto_accesso_category'].search([]):
            for access_point in access_point_group.ca_access_point_ids:
                access_point.stamping_attach()
        return res
