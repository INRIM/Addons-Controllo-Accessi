from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

class InrimApiPersona(InrimApiController):

    @http.route('/api/persona', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_persona(self, **params):
        model = 'ca.persona'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)
    
class InrimApiTipoPersona(InrimApiController):

    @http.route('/api/tipo_persona', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_tipo_persona(self, **params):
        model = 'ca.tipo_persona'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)