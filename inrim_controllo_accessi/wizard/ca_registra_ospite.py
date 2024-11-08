from odoo import models, fields, api


class CaRegistraOspite(models.TransientModel):
    _name = 'ca.registra_ospite'
    _description = 'Registra Ospite'

    vat = fields.Char()
    ca_ente_name = fields.Char("Company Name", required=True)
    tipo_ente_azienda_id = fields.Many2one(
        'ca.tipo_ente_azienda', required=True,
        domain=lambda self: self.ente_azienda_domain())
    ca_ente_id = fields.Many2one("ca.ente_azienda")
    fiscalcode = fields.Char(string="Fiscalcode", required=True)
    lastname = fields.Char(required=True)
    name = fields.Char(required=True)
    freshman = fields.Char(groups="controllo_accessi.ca_gdpr")
    email = fields.Char(String="Email")
    persona_id = fields.Many2one("ca.persona")
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(required=True)
    parent_id = fields.Many2one(
        'ca.persona', string='Reference person', index=True,
        domain=[('is_internal', '=', True), ('is_structured', '=', True)]
    )
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    available_tags_ids = fields.Many2many('ca.tag', compute="_compute_available_tags")

    def ente_azienda_domain(self):
        return [
            ('id', 'not in',
             [
                 self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
                 self.env.ref(
                     'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
             ])
        ]

    @api.onchange('vat')
    def _compute_available_tags(self):
        for record in self:
            ente_az_found = self.env['ca.ente_azienda'].search([
                ('vat', '=', record.vat)], limit=1)
            if ente_az_found:
                record.ca_ente_name = ente_az_found.name
                record.tipo_ente_azienda_id = ente_az_found.tipo_ente_azienda_id
                record.ca_ente_id = ente_az_found.id

    def populate_person(self, rec):
        self.ensure_one()
        self.name = rec.name
        self.lastname = rec.lastname
        self.freshman = rec.freshman
        self.email = rec.email
        self.persona_id = rec.id
        self.compute_available_tags()

    def compute_available_tags(self):
        self.ensure_one()
        self.available_tags_ids = self.env['ca.tag'].search([
            ('in_use', '=', False),
            ('revoked', '=', False),
            ('temp', '=', True)
        ])

    @api.onchange('fiscalcode')
    def _compute_available_tags(self):
        for record in self:
            persona_id = self.env['ca.persona'].search([
                ('fiscalcode', '=', record.fiscalcode)], limit=1)
            if persona_id:
                self.populate_person(persona_id)

    @api.onchange('email')
    def _compute_available_email(self):
        for record in self:
            persona_ids = self.env['ca.persona'].search([
                ('email', '=', record.email)])
            if len(persona_ids) == 1:
                self.populate_person(persona_ids[0])

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))
                record.compute_available_tags()

    def action_confirm(self):
        if not self.ca_ente_id:
            self.persona_id = self.env['ca.ente_azienda'].ceate(
                {
                    "name": self.ca_ente_name,
                    "vat": self.vat,
                    "tipo_ente_azienda_id": self.tipo_ente_azienda_id
                }
            )
        if not self.persona_id:
            self.persona_id = self.env['ca.persona'].ceate(
                {
                    "name": self.name,
                    "lastname": self.lastname,
                    "fiscalcode": self.fiscalcode,
                    "freshman": self.freshman,
                    "parent_id": self.parent_id.id
                }
            )

        res = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_id.id,
            'ca_tag_id': self.ca_tag_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
        })
        self.env['ca.punto_accessp'].stamping_attach()
        return res
