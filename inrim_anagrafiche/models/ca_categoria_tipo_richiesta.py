from odoo import models, fields, api

class CaCategoriaTipoRichiesta(models.Model):
    _name = 'ca.categoria_tipo_richiesta'
    _description = 'Categoria Tipo Richiesta'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    ca_categoria_richiesta = fields.Many2one('ca.categoria_richiesta')
    is_activity = fields.Boolean(compute="_compute_is_activity", store=True)
    active = fields.Boolean(default=True)

    @api.depends('ca_categoria_richiesta')
    def _compute_is_activity(self):
        for record in self:
            record.is_activity = False
            if (
                record.ca_categoria_richiesta == self.env.ref(
                    'inrim_anagrafiche.ca_categoria_richiesta_attivita')
            ):
                record.is_activity = True