from odoo import http

from .api_controller_inrim import InrimApiController, BadRequest


class InrimApiDocumento(InrimApiController):

    @http.route('/api/documento', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_gest_documento(self, **params):
        self.check_token('ca.documento', 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/documento', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_gest_documento(self):
        self.check_token('ca.documento', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            # self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/documento', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_gest_documento(self):
        self.check_token('ca.documento', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/documento', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_documento(self):
        self.check_token('ca.documento', 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(
                *self.model.rest_delete(data), delete=True)
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))


class InrimApiImgDocumento(InrimApiController):

    @http.route('/api/immaginedoc', auth="none", type='http', methods=['GET'],
                csrf=False)
    def api_get_gest_immagine_doc(self, **params):
        self.check_token('ca.img_documento', 'read')

        return self.handle_response(
            *self.model.rest_get(params), is_list=True)

    @http.route('/api/immaginedoc', auth="none", type='http', methods=['POST'],
                csrf=False)
    def api_post_gest_immagine_doc(self):
        self.check_token('ca.img_documento', 'create')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_post(data))
        except Exception as e:
            # self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/immaginedoc', auth="none", type='http', methods=['PUT'],
                csrf=False)
    def api_put_gest_immagine_doc(self):
        self.check_token('ca.img_documento', 'write')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(*self.model.rest_put(data))
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))

    @http.route('/api/immaginedoc', auth="none", type='http', methods=['DELETE'],
                csrf=False)
    def api_delete_ca_immagine_doc(self):
        self.check_token('ca.img_documento', 'unlink')
        data = self.check_and_decode_body()
        try:
            return self.handle_response(
                *self.model.rest_delete(data), delete=True)
        except Exception as e:
            self.env.cr.rollback()
            raise BadRequest(str(e))
