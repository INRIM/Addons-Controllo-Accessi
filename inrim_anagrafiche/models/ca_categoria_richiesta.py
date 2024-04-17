from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaCategoriaRichiesta(models.Model):
    _name = 'ca.categoria_richiesta'
    _description = 'Categoria Richiesta'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))