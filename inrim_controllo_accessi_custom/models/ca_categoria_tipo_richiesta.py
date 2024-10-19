from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaCategoriaTipoRichiesta(models.Model):
    _name = 'ca.categoria_tipo_richiesta'
    _inherit = "ca.model.base.mixin"
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
                'inrim_controllo_accessi_custom.ca_categoria_richiesta_attivita')
            ):
                record.is_activity = True

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
            'ca_categoria_richiesta': self.f_m2o(self.ca_categoria_richiesta),
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end)
        }

    def rest_boby_hint(self):
        return {
            'name': "name",
            'description': "description",
            'ca_categoria_richiesta': "ca_categoria_richiesta_id",
            'date_start': '2024-01-01',
            'date_end': '2024-01-02'
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'ca_categoria_richiesta', 'date_start', 'date_end'
            ])
        if not res:
            return res, msg
