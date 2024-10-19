import json
import random
import string
import datetime

import werkzeug
from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from odoo.tools import date_utils
from werkzeug.exceptions import Unauthorized, Forbidden, NotAcceptable, BadRequest


class InrimApiController(http.Controller):

    def __init__(self):
        super(InrimApiController, self).__init__()
        self.model = None
        self.env = None

    @staticmethod
    def authenticate_token(env, token):
        try:
            return env['auth.api.key'].sudo()._retrieve_api_key(token).user_id.id
        except Exception as e:
            return False

    def generate_token(self, env):
        characters = string.ascii_letters + string.digits
        uniquepart =  str(datetime.datetime.now().timestamp()).replace(".","")
        rndpart = ''.join(random.choice(characters) for i in range(40))
        token = f"{rndpart}{uniquepart}"
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