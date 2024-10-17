from odoo import models, fields

class CaTag(models.Model):
    _inherit = 'ca.tag'

    timezone_config = fields.Text()