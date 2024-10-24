from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaAnagRegistroAccesso(models.Model):
    _name = 'ca.anag_avanzamento_rich'
    _inherit = "ca.model.base.mixin"
    _description = 'Anagrafica Avanzamento Richiesta'
    _rec_name = 'code'

    name = fields.Char(required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled')
    ], required=True)
    code = fields.Char(compute="_compute_code", store=True)
    active = fields.Boolean(default=True)

    def rest_boby_hint(self):
        return {
            "name": "",
            "state": ""
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'state': self.f_selection('state', self.state),
            'code': self.code
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'state'
            ])
        return body, msg

    @api.depends('name', 'state')
    def _compute_code(self):
        for record in self:
            record.code = False
            if record.name and record.state:
                record.code = (record.name + ' ' + record.state).lower().replace(' ', '_')

    @api.constrains('name', 'state', 'active')
    def _check_unique(self):
        for record in self:
            anag_avanzamento_rich_id = self.env[
                'ca.anag_avanzamento_rich'
            ].search([
                ('id', '!=', record.id),
                ('name', '=', record.name),
                ('state', '=', record.state)
            ])
            if anag_avanzamento_rich_id:
                raise UserError(_('Esiste già un altro record con stesso nome e stato'))