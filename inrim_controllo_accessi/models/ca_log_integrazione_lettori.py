from odoo import models, fields, api

class CaLogIntegrazioneLettori(models.Model):
    _name = 'ca.log_integrazione_lettori'
    _inherit = "ca.model.base.mixin"
    _description = 'Log Integrazione Lettori'
    _rec_name = 'activity_code'

    activity_code = fields.Char(readonly=True)
    datetime = fields.Datetime(readonly=True)
    ca_lettore_id = fields.Many2one('ca.lettore', readonly=True)
    expected_events_num = fields.Integer(readonly=True)
    events_read_num = fields.Integer(readonly=True)
    operation_status = fields.Selection([
        ('ok', 'Ok'),
        ('ko', 'Ko')
    ], readonly=True)
    error_code = fields.Char(readonly=True)
    log_error = fields.Text(readonly=True)