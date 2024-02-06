from odoo import models, fields, api

class CaTipoPersona(models.Model):
    _name = 'ca.tipo_persona'
    _description = 'Tipo Persona'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)