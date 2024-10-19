from odoo import models, fields


class CaLettore(models.Model):
    _name = 'ca.lettore'
    _inherit = "ca.model.base.mixin"
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
    system_error = fields.Boolean(readonly=True)
    error_code = fields.Char(readonly=True)
    active = fields.Boolean(default=True)

    def rest_boby_hint(self):
        return {
            "name": "Test",
            "reader_ip": "127.0.0.1",
            "direction": "in, out",
        }

    def rest_get_record(self):
        vals = {
            "id": self.id,
            "name": self.name,
            "reader_ip": self.reader_ip,
            "direction": self.f_selection('direction', self.direction),
            "device_id": self.device_id,
            "type": self.type,
            "mode": self.mode,
            "mode_type": self.mode_type,
            "reader_status": self.reader_status,
            "available_events": self.available_events,
            "system_error": self.system_error,
            "error_code": self.error_code
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'reader_ip'
            ])
        return body, msg
