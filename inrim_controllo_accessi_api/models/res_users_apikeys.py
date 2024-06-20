from odoo import models, fields
from datetime import datetime, timedelta
import pytz

class ResUsersApikeys(models.Model):
    _inherit = 'res.users.apikeys'

    def _cron_clear_users_apikeys(self):
        ten_min_ago = datetime.now() - timedelta(minutes=10)
        expired_keys = self.search([('create_date', '<', ten_min_ago)])
        expired_keys.unlink()