import json
from datetime import timedelta

import httpx
import respx
from odoo import fields

GATEWAY = "http://gw.provisioning.test"

INFO_ONLINE = {
    "status": True,
    "diagnostic": {"event_tab_size": 0, "event_cnt": 0},
    "info": {
        "deviceId": "29335616",
        "readerType": "ID MAX50.xx",
        "mode": "Access Mode",
        "modeCode": "0x20",
    },
}
OFFLINE = {"status": False, "diagnostic": {}, "info": {}}
EVENTS_EMPTY = {
    "status": 146, "statusStr": "OK", "layoutIdd": True, "layoutTimeStamp": True,
    "layoutEventStatus": True, "layoutInput": True, "dataSetsLenght": 0,
    "hasMore": False, "layout": [True] * 4 + [False] * 4, "eventRecords": [],
}
ADD_TAGS_OK = {
    "status": True, "diagnostic": {"event_tab_size": 0, "event_cnt": 0}, "result": True,
}


class GatewayMixin:
    """Gateway lettori simulato: risponde online solo per gli IP in
    self.online_ips."""

    def setup_gateway(self, env):
        params = env['ir.config_parameter'].sudo()
        params.set_param('service_reader.url', GATEWAY)
        params.set_param('service_reader.jwt', 'test-key')
        params.set_param('provisioning_lettore.stamping_wait_minutes', '10')
        for ente in env['ca.ente_azienda'].sudo().search([]):
            ente.url_gateway_lettori = GATEWAY
        self.online_ips = set()
        self.router = respx.mock(assert_all_called=False)
        self.router.start()
        self.addCleanup(self.router.stop)
        self.router.post(f"{GATEWAY}/info").mock(side_effect=self._info)
        self.router.post(f"{GATEWAY}/status").mock(side_effect=self._status)
        self.router.post(f"{GATEWAY}/add-tags").mock(
            return_value=httpx.Response(200, json=ADD_TAGS_OK))
        self.router.post(f"{GATEWAY}/read-events").mock(
            return_value=httpx.Response(200, json=EVENTS_EMPTY))

    def _device(self, request):
        return json.loads(request.content or b"{}").get("device")

    def _info(self, request):
        if self._device(request) in self.online_ips:
            return httpx.Response(200, json=INFO_ONLINE)
        return httpx.Response(200, json=OFFLINE)

    def _status(self, request):
        if self._device(request) in self.online_ips:
            now = fields.Datetime.now() + timedelta(hours=1)  # Europe/Rome, circa
            return httpx.Response(200, json={
                "status": True,
                "diagnostic": {
                    "event_tab_size": 3268,
                    "event_cnt": 0,
                    "systemClock": now.strftime("%Y-%m-%dT%H:%M:%S.000"),
                },
            })
        return httpx.Response(200, json=OFFLINE)
