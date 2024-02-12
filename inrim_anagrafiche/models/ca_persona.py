from odoo import models, fields, api
import random
import string

class CaPersona(models.Model):
    _name = 'ca.persona'
    _description = 'Persona'
    _rec_name = "display_name"
    _rec_names_search = ['display_name', 'token']
   
    name = fields.Char(required=True) 
    lastname = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    associated_user_id = fields.Many2one('res.users')
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]")
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    fiscalcode = fields.Char(required=True)
    vat = fields.Char()
    type_ids = fields.Many2many('ca.tipo_persona')
    freshman = fields.Char()
    nationality = fields.Many2one('res.country')
    birth_date = fields.Date()
    birth_place = fields.Char()
    istat_code = fields.Char()
    parent_id = fields.Many2one('ca.persona', string='Related Company', index=True)
    child_ids = fields.One2many('ca.persona', 'parent_id', string='Contact', domain=[('active', '=', True)])
    residence_street = fields.Char()
    residence_street2 = fields.Char()
    residence_city = fields.Char()
    residence_state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]")
    residence_zip = fields.Char()
    residence_country_id = fields.Many2one('res.country')
    domicile_street = fields.Char()
    domicile_street2 = fields.Char()
    domicile_city = fields.Char()
    domicile_state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]")
    domicile_zip = fields.Char()
    domicile_country_id = fields.Many2one('res.country')
    domicile_other_than_residence = fields.Boolean()
    ca_documento_ids = fields.One2many('ca.documento', 'ca_persona_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('documents', 'Waiting for documents'),
        ('completed', 'Completed')
    ], required=True, default='draft')
    ca_ente_azienda_ids = fields.Many2many('ca.ente_azienda')
    token = fields.Char(required=True, readonly=True, default=lambda self:self.get_token())
    ca_tag_persona_ids = fields.One2many('ca.tag_persona', 'ca_persona_id')
    is_external = fields.Boolean(compute="_compute_bool")
    is_internal = fields.Boolean(compute="_compute_bool")
    active = fields.Boolean(default=True)

    @api.onchange('type_ids')
    def _compute_bool(self):
        for record in self:
            record.is_external = False
            record.is_internal = False
            for tag in record.type_ids:
                if tag.name == 'Esterno' or tag.name == 'esterno':
                    record.is_external = True
                if tag.name == 'Interno' or tag.name == 'interno':
                    record.is_internal = True

    @api.depends('name', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = False
            if record.name and record.lastname:
                record.display_name = record.name + ' ' + record.lastname

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_documents(self):
        for record in self:
            record.state = 'documents'

    def action_completed(self):
        for record in self:
            record.state = 'completed'

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        persona_id = self.env['ca.persona'].search([('token', '=', token)])
        if persona_id:
            self.get_token()
        return token