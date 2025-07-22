import logging

import httpx
import pytz
from odoo import models, fields

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones,
                                  key=lambda tz: tz if not tz.startswith(
                                      'Etc/') else '_')]

logger = logging.getLogger(__name__)


def _tz_get(self):
    return _tzs


class CaAnagRegistroAccesso(models.Model):
    _inherit = 'ca.anag_registro_accesso'

    codice_lettore_grum = fields.Integer(
        string='GRUM Reader Code',
    )
    work_id_number = fields.Char(string='ID Number')
    state = fields.Selection([
        ('no_sync', 'No Sync'),
        ('to_sync', 'To Sync'),
        ('sent', 'Sent'),
        ('sync_done', 'Sync Done'),
        ('sync_error', 'Sync Error'),
    ], string="Sync State", readonly=True, default='no_sync')

    def aggiungi_riga_accesso(
            self, ca_punto_accesso_id,
            ca_tag_persona_id, datetime_event, type='manual', access_allowed=True,
            tz=""
    ):
        res = super().aggiungi_riga_accesso(
            ca_punto_accesso_id, ca_tag_persona_id, datetime_event, type=type,
            access_allowed=access_allowed, tz=tz)
        todo = {}
        if res and ca_punto_accesso_id.typology == 'stamping' and res.access_allowed:
            todo['codice_lettore_grum'] = ca_punto_accesso_id.codice_lettore_grum
            winfo = ca_tag_persona_id.ca_persona_id.get_current_winfo()
            todo['work_id_number'] = winfo.work_id_number
            if ca_tag_persona_id.ca_persona_id.send_to_payroll_system:
                todo['state'] = 'to_sync'
            res.write(todo)
        return res

    def rest_get_record_labinf(self):
        vals = {
            "id": self.id,
            "codice_lettore_grum": self.codice_lettore_grum,
            "datetime_event": self.f_datetime(self.datetime_event, self.tz),
            "direction": self.f_selection('direction', self.direction),
            "work_id_number": self.work_id_number,
            "state": self.f_selection("state", self.state)
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'ca_punto_accesso_id', 'ca_tag_persona_id', 'datetime_event',
                'access_allowed', 'type', 'state'
            ])
        return body, msg

    def rest_put(self, body: dict):
        if body.get('state'):
            new_body = {}
            for item in body.keys():
                if item in ('id', 'state'):
                    new_body[item] = body[item]
            return super().rest_put(new_body)
        else:
            return False, "Not Allowed"

    def run_labinf_sync(self):
        url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('labinf_sync_service')
        try:
            with httpx.Client(timeout=40) as client:
                response = client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(
                    f"{url}, Status Code: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"{url}, Error: {e}", exc_info=True)
            return {}
