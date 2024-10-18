from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from datetime import datetime
import string
import random
import pytz
import json

class InrimApiController(http.Controller):

    @staticmethod
    def authenticate_token(env, token):
        try:
            return env['auth.api.key']._retrieve_api_key(token).user_id.id
        except Exception as e:
            return False

    def generate_token(self, env):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(40))
        auth_api_key_id = env['auth.api.key'].search([('key', '=', token)])
        if auth_api_key_id:
            self.generate_token(env)
        return token
    
    @http.route('/token/authenticate', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self, **kwargs):
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                "error": "Invalid Body",
                'BodyHint': {
                    "username": "admin",
                    "password": "admin"
                }
            }, ensure_ascii=False, indent=4), status=400)
        data = json.loads(byte_string.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        try:
            user_id = request.session.authenticate(request.session.db, username, password)
        except Exception as e:
            return Response(json.dumps({
                "error": "Invalid Username or Password",
                'BodyHint': {
                    "username": "admin",
                    "password": "admin"
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not user_id:
            return Response(json.dumps({
                "error": "Invalid Username or Password"
            }, ensure_ascii=False, indent=4), status=400)
        env = request.env(user=user_id)
        if not env['res.users'].browse(user_id).api_enabled:
            return Response(json.dumps({
                "error": "Unauthorized user"
            }, ensure_ascii=False, indent=4), status=401)
        auth_api_key_id = env['auth.api.key'].search([
            ('user_id', '=', user_id)
        ], limit=1)
        if auth_api_key_id:
            token = auth_api_key_id.key
        else:
            user = env['res.users'].browse(user_id)
            auth_api_key_id = env['auth.api.key'].create({
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
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": payload,
        }, ensure_ascii=False, indent=4), status=200)