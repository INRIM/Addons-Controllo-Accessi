from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest


class InrimApiWorkInfo(InrimApiController):

    @http.route('/api/work_info', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_work_ifo(self, **params):
        model = 'ca.work_info'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/work_info', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_work_info(self):
        self.check_token('ca.work_info', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            raise BadRequest(str(e))


class InrimApiWorkInfoType(InrimApiController):

    @http.route('/api/work_info_type', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_work_info_type(self, **params):
        model = 'ca.work_info_type'
        self.check_token(model, 'read')
        return self.handle_response(
            *self.model.rest_get(params), is_list=True)
