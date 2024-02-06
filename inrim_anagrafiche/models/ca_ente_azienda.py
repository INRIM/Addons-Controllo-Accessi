from odoo import models, fields, api

class CaEnteAzienda(models.Model):
    _name = 'ca.ente_azienda'
    _description = 'Ente Azienda'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one('ca.ente_azienda', string='Parent Company', index=True)
    child_ids = fields.One2many('ca.ente_azienda', 'parent_id', string='Branches')
    all_child_ids = fields.One2many('ca.ente_azienda', 'parent_id', context={'active_test': False})
    parent_path = fields.Char(index=True, unaccent=False)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        'res.country.state', domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one('res.country')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    website = fields.Char()
    vat = fields.Char()
    pec = fields.Char(required=True)
    tipo_ente_azienda_id = fields.Many2one('ca.tipo_ente_azienda', required=True)
    note = fields.Text(required=True)
    company_id = fields.Many2one('res.company')
    ca_persona_ids = fields.Many2many('ca.persona', string='People')

class CaTipoEnteAzienda(models.Model):
    _name = 'ca.tipo_ente_azienda'
    _description = 'Tipo Ente Azienda'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)