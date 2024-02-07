from odoo import models, fields, api

class CaLettore(models.Model):
    _name = 'ca.lettore'
    _description = 'Lettore'

    name = fields.Char(required=True)
    reader_ip = fields.Char(required=True)
    direction = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], required=True)
    device_id = fields.Char(readonly=True)
    type = fields.Char(readonly=True)
    mode = fields.Char(readonly=True)
    mode_type = fields.Char(readonly=True)
    reader_status = fields.Char(readonly=True)
    available_events = fields.Integer(readonly=True)
    system_error = fields.Boolean(compute="_compute_system_error")
    error_code = fields.Char(readonly=True)
    active = fields.Boolean(default=True)

    @api.onchange('error_code')
    def _compute_system_error(self):
        for record in self:
            record.system_error = False
            if record.error_code != "0000":
                record.system_error = True