from odoo import models, fields, api

class CaTipoSpazio(models.Model):
    _name = 'ca.tipo_spazio'
    _description = 'Tipo Spazio'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

class CaSpazio(models.Model):
    _name = 'ca.spazio'
    _description = 'Spazio'

    name = fields.Char(required=True, string="Space Name")
    tipo_spazio_id = fields.Many2one('ca.tipo_spazio', required=True)
    ente_azienda_id = fields.Many2one('ca.ente_azienda', required=True)
    codice_locale_id = fields.Many2one('ca.codice_locale')
    lettore_id = fields.Many2one('ca.lettore')
    date_start = fields.Date()
    date_end = fields.Date()
    righe_persona_ids = fields.One2many('ca.righe_persona', 'spazio_id')
    active = fields.Boolean(default=True)