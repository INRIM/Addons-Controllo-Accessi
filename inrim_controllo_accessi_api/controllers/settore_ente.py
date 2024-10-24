from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

class InrimApiSettoreEnte(InrimApiController):

    @http.route('/api/settore_ente', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_settore_ente(self, **params):
        self.check_token('ca.settore_ente', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)