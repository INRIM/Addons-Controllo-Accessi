import ipaddress
import logging
from datetime import datetime

import pytz
from odoo import models, fields
from odoo.addons.inrim_controllo_accessi_rfidglobal.models.Max5010_rfid_lib import (
    Max5010RfidClient,
)

logger = logging.getLogger(__name__)

DEFAULT_TZ = "Europe/Rome"


class CaReaderCheck(models.AbstractModel):
    """
    Check generico di un lettore: chiama /info e /status del gateway lettori
    e restituisce un report leggibile, utile sia per i punti accesso in
    esercizio sia durante l'installazione (lettore non ancora in anagrafica).
    """
    _name = 'ca.reader_check'
    _description = 'Check lettore badge (/info + /status)'

    @staticmethod
    def valid_ip(ip):
        try:
            ipaddress.ip_address((ip or "").strip())
            return True
        except ValueError:
            return False

    def _gateway(self, ente_azienda=None):
        """URL e credenziali del gateway: della sede se valorizzati, altrimenti
        quelli di sistema (service_reader.*)."""
        params = self.env['ir.config_parameter'].sudo()
        ente = ente_azienda.sudo() if ente_azienda else None
        url = (ente and ente.url_gateway_lettori) or params.get_param(
            'service_reader.url') or ""
        header = (ente and ente.nome_chiave_header) or "authtoken"
        token = (ente and ente.jwt) or params.get_param('service_reader.jwt') or ""
        return url.strip(), header, token

    def find_ip_owners(self, ip, exclude_lettore_ids=None):
        """Lettori (anche archiviati) che usano gia' questo IP, con i loro
        punti accesso."""
        domain = [('reader_ip', '=', (ip or "").strip())]
        if exclude_lettore_ids:
            domain.append(('id', 'not in', list(exclude_lettore_ids)))
        lettori = self.env['ca.lettore'].with_context(active_test=False).search(domain)
        owners = []
        for lettore in lettori:
            punti = self.env['ca.punto_accesso'].with_context(
                active_test=False).search([('ca_lettore_id', '=', lettore.id)])
            owners.append({
                'lettore_id': lettore.id,
                'lettore': lettore.name,
                'active': lettore.active,
                'punti_accesso': [{
                    'id': p.id,
                    'name': p.name,
                    'active': p.active,
                    'enable_sync': p.enable_sync,
                } for p in punti],
            })
        return owners

    def _call(self, client, endpoint):
        res, msg = client.post_request(client._build_url(endpoint), {})
        return res or {}, msg

    def _clock_drift(self, system_clock, tz_name):
        if not system_clock:
            return None
        try:
            device_dt = datetime.fromisoformat(system_clock)
        except ValueError:
            return None
        now = datetime.now(pytz.timezone(tz_name)).replace(tzinfo=None)
        return int((device_dt - now).total_seconds())

    def run(self, ip, ente_azienda=None, tz=None):
        """
        Esegue /info e /status sul lettore all'IP dato.

        :return: dict con ok, info, status, messages. ok e' True solo se il
            lettore risponde a entrambe le chiamate con status True.
        """
        ip = (ip or "").strip()
        tz_name = tz or (ente_azienda and ente_azienda.tz) or DEFAULT_TZ
        url, header, token = self._gateway(ente_azienda)
        report = {
            'ok': False,
            'ip': ip,
            'gateway': url,
            'checked_at': fields.Datetime.to_string(fields.Datetime.now()),
            'info': {'reachable': False},
            'status': {'reachable': False},
            'warnings': [],
            'messages': [],
        }
        if not self.valid_ip(ip):
            report['messages'].append(f"IP non valido: '{ip}'")
            return report
        if not url.startswith(('http://', 'https://')):
            report['messages'].append(
                f"Gateway lettori non configurato (url: '{url}'): impostare "
                "url_gateway_lettori sulla sede o il parametro service_reader.url")
            return report

        client = Max5010RfidClient(ip, url, header, token, tz_name)

        info, msg = self._call(client, "info")
        device_info = info.get('info') or {}
        report['info'] = {
            'reachable': bool(info),
            'status': bool(info.get('status')),
            'device_id': device_info.get('deviceId', ""),
            'reader_type': device_info.get('readerType', ""),
            'mode': device_info.get('mode', ""),
            'mode_code': device_info.get('modeCode', ""),
        }
        if not info:
            report['info']['error'] = msg
            report['messages'].append(f"/info: gateway o lettore non raggiungibile: {msg}")
            return report
        if not info.get('status'):
            report['messages'].append("/info: il lettore non risponde (status False)")
            return report

        status, msg = self._call(client, "status")
        diagnostic = status.get('diagnostic') or {}
        drift = self._clock_drift(diagnostic.get('systemClock'), tz_name)
        report['status'] = {
            'reachable': bool(status),
            'status': bool(status.get('status')),
            'event_tab_size': diagnostic.get('event_tab_size', 0),
            'event_cnt': diagnostic.get('event_cnt', 0),
            'system_clock': diagnostic.get('systemClock'),
            'clock_drift_seconds': drift,
        }
        if not status:
            report['status']['error'] = msg
            report['messages'].append(f"/status: nessuna risposta: {msg}")
            return report
        if not status.get('status'):
            report['messages'].append("/status: il lettore non risponde (status False)")
            return report

        max_drift = int(self.env['ir.config_parameter'].sudo().get_param(
            'provisioning_lettore.max_clock_drift_seconds', 120))
        if drift is not None and abs(drift) > max_drift:
            report['warnings'].append(
                f"Orologio del lettore spostato di {drift} secondi: verra' "
                "riallineato dal cron 'Update Readers Clock'")
        if report['status']['event_cnt']:
            report['warnings'].append(
                f"{report['status']['event_cnt']} eventi da scaricare sul lettore: "
                "i tag vengono scritti solo dopo lo scarico")
        report['ok'] = True
        report['messages'].append(
            f"Lettore {report['info']['device_id']} ({report['info']['reader_type']}) "
            f"online su {ip}")
        return report

    def run_for_punto_accesso(self, punto_accesso):
        """Check di un punto accesso esistente: IP del suo lettore e gateway
        della sua sede."""
        punto_accesso.ensure_one()
        report = self.run(
            punto_accesso.ca_lettore_id.reader_ip,
            ente_azienda=punto_accesso.ente_azienda_id,
            tz=punto_accesso.tz,
        )
        report['punto_accesso'] = {
            'id': punto_accesso.id,
            'name': punto_accesso.name,
            'typology': punto_accesso.typology,
            'enable_sync': punto_accesso.enable_sync,
            'remote_update': punto_accesso.remote_update,
            'system_error': punto_accesso.system_error,
            'lettore_id': punto_accesso.ca_lettore_id.id,
            'tag_count': len(punto_accesso.ca_tag_lettore_ids.filtered(
                lambda t: t.state != 'expired')),
        }
        return report
