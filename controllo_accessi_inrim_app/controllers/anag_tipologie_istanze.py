from odoo import http

from ...inrim_controllo_accessi_api.controllers.api_controller_inrim import InrimApiController, BadRequest

class InrimApiAnagTipologieIstanze(InrimApiController):

    @http.route('/api/anag_tipologie_istanze', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_anag_tipologie_istanze(self, **params):
        self.check_token('ca.anag_tipologie_istanze', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)