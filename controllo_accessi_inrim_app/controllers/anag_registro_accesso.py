from odoo import http

from ...inrim_controllo_accessi_api.controllers.api_controller_inrim import \
    InrimApiController, BadRequest


class InrimApiAnagRegistroAccesso(InrimApiController):

    @http.route('/api/registroaccesso', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_registro_accesso(self, **params):
        self.check_token('ca.anag_registro_accesso', 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/registroaccesso', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_registro_accesso(self):
        self.check_token('ca.anag_registro_accesso', 'write')
        data = self.check_and_decode_body()
        try:
            with self.env.cr.savepoint():
                return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            raise BadRequest(str(e))