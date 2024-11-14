import pytz
from odoo import models, fields

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones,
                                  key=lambda tz: tz if not tz.startswith(
                                      'Etc/') else '_')]


def _tz_get(self):
    return _tzs


class CaAnagRegistroAccesso(models.Model):
    _inherit = 'ca.anag_registro_accesso'

    codice_lettore_grum = fields.Integer(
        string='Codice Lettore GRUM',
    )
    work_id_number = fields.Char(string='ID Number')
    state = fields.Selection([
        ('to_sync', 'To Sync'),
        ('sync_done', 'Sync Done'),
        ('sync_error', 'Sync Error'),
    ], string="Sync State", readonly=True)

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
            if winfo.ca_work_info_type_id.structured:
                todo['work_id_number'] = winfo.work_id_number
                todo['state'] = 'to_sync'
            res.write(todo)
        return res
