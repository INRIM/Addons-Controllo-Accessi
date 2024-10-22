from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

class InrimApiTag(InrimApiController):

    @http.route('/api/tag', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_tag(self, **params):
        self.check_token('ca.tag', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)
    
    @http.route('/api/tag', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_ca_tag(self):
        self.check_token('ca.tag', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            raise BadRequest(str(e))

    @http.route('/api/tag', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_ca_tag(self):
        self.check_token('ca.tag', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            raise BadRequest(str(e))

class InrimApiProprietaTag(InrimApiController):

    @http.route('/api/proprieta_tag', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_proprieta_tag(self, **params):
        self.check_token('ca.proprieta_tag', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)