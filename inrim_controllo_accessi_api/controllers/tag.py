from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

class InrimApiProprietaTag(InrimApiController):

    @http.route('/api/proprieta_tag', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_proprieta_tag(self, **params):
        model = 'ca.proprieta_tag'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)