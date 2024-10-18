from odoo import http

from .auth import InrimApiController, BadRequest


class InrimApiDocumento(InrimApiController):

    @http.route('/api/documento', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_gest_documento(self):
        self.check_token('ca.documento', 'read')

        return self.handle_response(
            *self.model.rest_get(self.get_query_params()), is_list=True)

    @http.route('/api/documento', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_gest_documento(self):
        self.check_token('ca.documento', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/documento', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_gest_documento(self):
        self.check_token('ca.documento', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/documento', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_documento(self):
        self.check_token('ca.documento', 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_delete(data), delete=True)
        except Exception as e:
            env.cr.rollback()
            raise BadRequest(str(e))
