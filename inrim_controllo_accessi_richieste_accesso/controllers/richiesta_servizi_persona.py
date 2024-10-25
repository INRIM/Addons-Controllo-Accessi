from odoo import http

from ...inrim_controllo_accessi_api.controllers.api_controller_inrim import InrimApiController, BadRequest

class InrimApiRichiestaServiziPersona(InrimApiController):

    @http.route('/api/richiesta_servizi_persona', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_ca_richiesta_servizi_persona(self, **params):
        self.check_token('ca.richiesta_servizi_persona', 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)
    
    @http.route('/api/get_by_name_richiesta_servizi_persona', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_by_name_ca_richiesta_servizi_persona(self, **params):
        self.check_token('ca.richiesta_servizi_persona', 'read')
        if params:
            key, value = list(params.items())[0]
            richiesta_servizi_persona_id = self.model.get_by_key(key, value)
            if richiesta_servizi_persona_id:
                return self.handle_response(
                    richiesta_servizi_persona_id.rest_get_record(), is_list=True)
            else:
                raise BadRequest(f"Nessun record trovato con chiave '{key}' e valore '{value}'")
        else:
            raise BadRequest(f"No Params")

    @http.route('/api/richiesta_servizi_persona', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_ca_richiesta_servizi_persona(self):
        self.check_token('ca.richiesta_servizi_persona', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            raise BadRequest(str(e))

    @http.route('/api/richiesta_servizi_persona', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_ca_richiesta_servizi_persona(self):
        self.check_token('ca.richiesta_servizi_persona', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            raise BadRequest(str(e))