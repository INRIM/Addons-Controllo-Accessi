from odoo import models, fields
from datetime import datetime, timedelta
import pytz

class ResUsersApikeys(models.Model):
    _inherit = 'res.users.apikeys'

    def _cron_clear_users_apikeys(self):
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        local_now = datetime.now(tz=user_tz)
        one_hour_ago = local_now - timedelta(hours=1)
        expired_keys = self.search([('create_date', '<', one_hour_ago)])
        expired_keys.unlink()