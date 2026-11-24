import json
import logging

from odoo import http
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.http import request
from odoo.addons.inrim_controllo_accessi_api.controllers.api_controller_inrim import (
    InrimApiController,
)

logger = logging.getLogger(__name__)

MODEL = 'ca.provisioning_lettore'
BASE = '/api/provisioning_lettore'


class InrimApiProvisioningLettore(InrimApiController):
    """
    API della procedura di installazione/sostituzione lettori.

    Le risposte sono sempre JSON: 200 con il risultato del passo (campo ok),
    400 con {"error": ...} per input o stato non validi, 404 se la procedura
    non esiste.
    """

    @staticmethod
    def _json(body, status=200):
        return request.make_response(
            json.dumps(body, ensure_ascii=False, default=str),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
            status=status,
        )

    def _model(self, access_type):
        self.check_token(MODEL, access_type)
        # check_token usa un env con active_test=False: qui i record
        # archiviati non devono comparire nelle ricerche
        return self.model.with_context(active_test=True)

    def _body(self):
        data = request.httprequest.get_data(as_text=True)
        if not data:
            return {}
        try:
            body = json.loads(data)
        except ValueError:
            raise UserError("Body JSON non valido")
        if not isinstance(body, dict):
            raise UserError("Il body deve essere un oggetto JSON")
        return body

    def _run(self, fn):
        try:
            with request.env.cr.savepoint():
                return self._json(fn())
        except (UserError, ValidationError, AccessError) as e:
            return self._json({'error': str(e.args[0] if e.args else e)}, status=400)

    @http.route(f'{BASE}/check', auth="none", type='http', methods=['POST'],
                csrf=False, readonly=False)
    def api_check(self):
        """Check generico: body {ip} oppure {punto_accesso_id} oppure
        {lettore_id}; ente_azienda_id opzionale per il gateway."""
        model = self._model('read')

        def fn():
            body = self._body()
            checker = model.env['ca.reader_check']
            if body.get('punto_accesso_id'):
                punto = model.env['ca.punto_accesso'].with_context(
                    active_test=False).browse(int(body['punto_accesso_id'])).exists()
                if not punto:
                    raise UserError("Punto accesso non trovato")
                report = checker.run_for_punto_accesso(punto)
            else:
                ip = body.get('ip')
                if body.get('lettore_id'):
                    lettore = model.env['ca.lettore'].with_context(
                        active_test=False).browse(int(body['lettore_id'])).exists()
                    if not lettore:
                        raise UserError("Lettore non trovato")
                    ip = lettore.reader_ip
                if not ip:
                    raise UserError("passare ip, lettore_id o punto_accesso_id")
                ente = False
                if body.get('ente_azienda_id'):
                    ente = model.env['ca.ente_azienda'].browse(
                        int(body['ente_azienda_id'])).exists()
                report = checker.run(ip, ente_azienda=ente or None)
                report['ip_owners'] = checker.find_ip_owners(ip)
            return report

        return self._run(fn)

    @http.route(BASE, auth="none", type='http', methods=['GET'], csrf=False)
    def api_list(self, **params):
        model = self._model('read')
        return self._run(lambda: model.rest_get(params)[0])

    @http.route(BASE, auth="none", type='http', methods=['POST'],
                csrf=False, readonly=False)
    def api_start(self):
        """1 - Avvia una procedura: body {operation, typology}."""
        model = self._model('create')
        return self._run(lambda: model.start(self._body()).rest_get_record())

    @http.route(f'{BASE}/<int:rec_id>', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get(self, rec_id, **params):
        model = self._model('read')
        record = model.browse(rec_id).exists()
        if not record:
            return self._json({'error': f"Procedura {rec_id} non trovata"}, status=404)
        return self._run(record.rest_get_record)

    @http.route(f'{BASE}/<int:rec_id>/options', auth="none", type='http',
                methods=['GET'], csrf=False)
    def api_options(self, rec_id, **params):
        model = self._model('read')
        record = model.browse(rec_id).exists()
        if not record:
            return self._json({'error': f"Procedura {rec_id} non trovata"}, status=404)
        return self._run(record.get_options)

    @http.route(f'{BASE}/<int:rec_id>/<string:step>', auth="none", type='http',
                methods=['POST'], csrf=False, readonly=False)
    def api_step(self, rec_id, step):
        model = self._model('write')
        record = model.browse(rec_id).exists()
        if not record:
            return self._json({'error': f"Procedura {rec_id} non trovata"}, status=404)
        return self._run(lambda: record.run_step(step, self._body()))
