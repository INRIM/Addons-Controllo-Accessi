from odoo import http
from odoo.http import request
from werkzeug.exceptions import Unauthorized

from .api_controller_inrim import InrimApiController


class AuthController(InrimApiController):

    @http.route('/token/authenticate', type='http', auth="none", methods=['POST'],
                csrf=False, save_session=False, cors="*")
    def get_token(self, **kwargs):
        data = self.check_and_decode_body()
        username = data.get('username')
        password = data.get('password')
        try:
            user_id = request.session.authenticate(
                request.session.db, username, password)
        except Exception as e:
            raise Unauthorized(description='Invalid Credential')

        if not user_id:
            return Unauthorized(description='Invalid Credential')
        env = request.env(user=user_id)
        user = env['res.users'].browse(user_id)
        if not user.api_enabled:
            return Unauthorized(description='No Auth for Api')

        auth_api_key_id = env['auth.api.key'].sudo().search([
            ('user_id', '=', user_id)
        ], limit=1)
        if auth_api_key_id:
            token = auth_api_key_id.key
        else:
            user = env['res.users'].browse(user_id)
            auth_api_key_id = env['auth.api.key'].sudo().create({
                'name': f'{user.display_name} - INRiM',
                'user_id': user_id,
                'key': self.generate_token(env)
            })
            token = auth_api_key_id.key
        payload = {
            'messages': 'UserValidated',
            'user_id': user_id,
            'username': username,
            'password': password,
            'token': token
        }
        return self.success_response(payload)
