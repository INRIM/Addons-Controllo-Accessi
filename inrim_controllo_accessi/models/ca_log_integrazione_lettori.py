from odoo import models, fields, api

class CaLogIntegrazioneLettori(models.Model):
    _name = 'ca.log_integrazione_lettori'
    _inherit = "ca.model.base.mixin"
    _description = 'Log Integrazione Lettori'
    _rec_name = 'activity_code'

    activity_code = fields.Char(readonly=True)
    datetime = fields.Datetime(readonly=True)
    ca_lettore_id = fields.Many2one('ca.lettore', readonly=True,
                                    string="Reader")
    expected_events_num = fields.Integer(readonly=True, default=0)
    events_read_num = fields.Integer(readonly=True, default=0)
    operation_status = fields.Selection([
        ('ok', 'Ok'),
        ('ko', 'Ko')
    ], readonly=True)
    error_code = fields.Char(readonly=True)
    log_error = fields.Text(readonly=True)
    file_name = fields.Char(readonly=True)
    file_path = fields.Char(readonly=True)


    def rest_boby_hint(self):
        return {
            "activity_code": "AP12345",
            "datetime": "2020-01-01 00:00:00",
            "ca_lettore_id": 1,
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            "ca_punto_accesso_id": self.activity_code,
            "datetime": self.f_datetime(self.datetime),
            "ca_lettore_id": self.ca_lettore_id.rest_get_record(),
            "expected_events_num": self.expected_events_num,
            "events_read_num": self.events_read_num,
            "operation_status": self.f_selection('operation_status', self.operation_status),
            "error_code": self.error_code,
            "log_error": self.log_error,
            "file_name": self.file_name,
            "file_path": self.file_path,
        }
        return vals



    def rest_post(self, body: dict):
        if body.get('state') and body.get('.id'):
            newbody = {}
            newbody['.id'] = body.get('.id')
            newbody['state'] = body.get('state')
            return super().rest_post(newbody)
        else:
            return False, f"Non consentito"