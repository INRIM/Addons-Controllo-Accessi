from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    api_enabled = fields.Boolean(help='Enabled for integration via API')