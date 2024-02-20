from odoo import models, fields

class CaCategoriaTipoRichiesta(models.Model):
    _name = 'ca.categoria_tipo_richiesta'
    _description = 'Categoria Tipo Richiesta'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    ca_categoria_richiesta = fields.Many2one('ca.categoria_richiesta')
    active = fields.Boolean(default=True)