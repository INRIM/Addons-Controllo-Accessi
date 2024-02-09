from odoo import models, fields

class CaCodiceLocale(models.Model):
    _name = 'ca.codice_locale'
    _description = 'Codice Locale'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)