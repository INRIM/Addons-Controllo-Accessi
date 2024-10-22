from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaTipoPersona(models.Model):
    _name = 'ca.tipo_persona'
    _inherit = "ca.model.base.mixin"
    _description = 'Tipo Persona'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)
    structured = fields.Boolean(help='Integration U-Gov/Esse3')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))
                
    def rest_boby_hint(self):
        return {
            "name": "Interno"
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end),
            'structured': self.structured
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name'
            ])
        return body, msg