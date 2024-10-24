from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

class InrimApiAnagServizi(InrimApiController):

    @http.route('/api/anag_servizi', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_anag_servizi(self, **params):
        self.check_token('ca.anag_servizi', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)