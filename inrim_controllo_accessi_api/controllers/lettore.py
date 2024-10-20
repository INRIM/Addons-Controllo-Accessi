from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

model = "ca.lettore"


class InrimApiLettore(InrimApiController):

    @http.route('/api/lettore', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_ca_lettore(self, **params):
        self.check_token(model, 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/lettore', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_ca_lettore(self):
        self.check_token(model, 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/lettore', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_ca_lettore(self):
        self.check_token(model, 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/lettore', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_lettore(self):
        self.check_token(model, 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(
                *self.model.rest_delete(data), delete=True)
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))
