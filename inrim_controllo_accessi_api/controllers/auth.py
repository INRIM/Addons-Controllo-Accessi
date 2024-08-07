from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from datetime import datetime
import pytz
import json

class InrimApiController(http.Controller):

    @staticmethod
    def authenticate_token(env, token):
        return env['res.users.apikeys']._check_credentials(scope="INRiM", key=token)
    
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
        env['res.users.apikeys.description'].check_access_make_key()
        token = env['res.users.apikeys']._generate("INRiM", username)
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