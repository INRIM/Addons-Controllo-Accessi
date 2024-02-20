from odoo import models, fields

class CaCategoriaRichiesta(models.Model):
    _name = 'ca.categoria_richiesta'
    _description = 'Categoria Richiesta'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)