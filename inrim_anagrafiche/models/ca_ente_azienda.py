from odoo import models, fields, api

class CaTipoDocumento(models.Model):
    _name = 'ca.ente_azienda'
    _description = 'Ente Azienda'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)