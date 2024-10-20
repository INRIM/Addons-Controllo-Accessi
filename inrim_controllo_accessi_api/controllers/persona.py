from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

model = "ca.persona"

class InrimApiPersona(InrimApiController):

    @http.route('/api/persona', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_persona(self, **params):
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)