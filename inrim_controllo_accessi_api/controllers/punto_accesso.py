import logging

from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest

logger = logging.getLogger(__name__)

class InrimApiPuntoAccesso(InrimApiController):

        
    @http.route('/api/punto_accesso/add_persona_tag', auth="none", type='http', methods=['POST'],
                csrf=False, readonly=False)
    def api_post_ca_exc_add_persona_tag(self):
        self.check_token('ca.punto_accesso', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.execute_method('add_persona_tag', data))
        except Exception as e:
            logger.error(e, exc_info=True)
            raise BadRequest(str(e))