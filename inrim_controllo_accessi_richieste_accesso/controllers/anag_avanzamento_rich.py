from odoo import http

from ...inrim_controllo_accessi_api.controllers.api_controller_inrim import InrimApiController, BadRequest

class InrimApiAnagAvanzamentoRich(InrimApiController):

    @http.route('/api/anag_avanzamento_rich', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_anag_avanzamento_rich(self, **params):
        self.check_token('ca.anag_avanzamento_rich', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)