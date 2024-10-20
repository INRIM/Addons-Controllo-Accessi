from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest


class InrimApiEnteAzienda(InrimApiController):

    @http.route('/api/ente_azienda', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_ca_ente_azienda(self, **params):
        self.check_token('ca.ente_azienda', 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/ente_azienda', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_ca_ente_azienda(self):
        self.check_token('ca.ente_azienda', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/ente_azienda', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_ca_ente_azienda(self):
        self.check_token('ca.ente_azienda', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/ente_azienda', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_ente_azienda(self):
        self.check_token('ca.ente_azienda', 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(
                *self.model.rest_delete(data), delete=True)
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))


class InrimApiTipoEnteAzienda(InrimApiController):

    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_ca_tipo_ente_azienda(self, **params):
        self.check_token('ca.tipo_ente_azienda', 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_ca_tipo_ente_azienda(self):
        self.check_token('ca.tipo_ente_azienda', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_ca_tipo_ente_azienda(self):
        self.check_token('ca.tipo_ente_azienda', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_tipo_ente_azienda(self):
        self.check_token('ca.tipo_ente_azienda', 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(
                *self.model.rest_delete(data), delete=True)
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))
