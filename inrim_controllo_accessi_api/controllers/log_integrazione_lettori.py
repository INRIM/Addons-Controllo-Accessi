from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest


class InrimApiLogIntegrazioneLettori(InrimApiController):

    @http.route('/api/log_integrazione_lettori', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_ca_log_integrazione_lettori(self, **params):
        model = 'ca.log_integrazione_lettori'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)