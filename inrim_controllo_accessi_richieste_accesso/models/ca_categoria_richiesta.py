from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaCategoriaRichiesta(models.Model):
    _name = 'ca.categoria_richiesta'
    _inherit = "ca.model.base.mixin"
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


    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end)
        }

    def rest_boby_hint(self):
        return {
            'name': "name",
            'description': "description",
            'date_start': '2024-01-01',
            'date_end': '2024-01-02'
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'date_start', 'date_end'
            ])
        if not res:
            return res, msg