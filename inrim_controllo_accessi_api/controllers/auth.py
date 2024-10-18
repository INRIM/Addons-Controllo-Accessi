import json
import random
import string

import werkzeug
from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from odoo.tools import date_utils
from werkzeug.exceptions import Unauthorized, Forbidden, NotAcceptable, BadRequest


class InrimApiController(http.Controller):

    def __init__(self):
        super(InrimApiController, self).__init__()
        self.model = None

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

    def check_token(self, model, access_type):
        env = api.Environment(
            request.cr, SUPERUSER_ID,
            {'active_test': False}
        )
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            user_token = self.authenticate_token(env, token)
            user_id = env['res.users'].browse(user_token)
            request.update_env(user=user_id)
            env.user = user_id
            if not user_token:
                raise Unauthorized(description='Token non valido')
        else:
            raise Unauthorized(description='Token non valido')
        try:
            env[model].with_user(env.user).check_access_rights(access_type)
            self.model = env[model]
        except Exception as e:
            raise Forbidden(
                description=f"L'utente {user_id.name} non ha accesso ai record di ca.documento"
            )

    @staticmethod
    def check_and_decode_body():
        byte_string = request.httprequest.data
        if not byte_string:
            raise NotAcceptable(description="No body in request")
        return json.loads(request.httprequest.get_data(as_text=True))

    @staticmethod
    def success_response(body, headers=None):
        data = json.dumps(body, ensure_ascii=False, default=date_utils.json_default)
        headers = werkzeug.datastructures.Headers(headers)
        headers['Content-Length'] = len(data)
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        return Response(data, status=200, headers=headers.to_wsgi_list())

    def handle_response(self, record, msg="", delete=False, is_list=False):
        if not record:
            raise BadRequest(description=msg)
        if delete:
            return self.success_response({})
        elif is_list:
            return self.success_response(record)
        else:
            return self.success_response(record.rest_get_record())

    def get_query_params(self):
        return {**request.httprequest.args}

    @http.route('/token/authenticate', type='http', auth="none", methods=['POST'],
                csrf=False, save_session=False, cors="*")
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
            user_id = request.session.authenticate(request.session.db, username,
                                                   password)
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
