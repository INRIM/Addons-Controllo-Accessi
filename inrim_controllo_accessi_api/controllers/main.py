from odoo import http, api, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request, Response
import json

class TokenController(http.Controller):
    
    @http.route('/Token/authenticate', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self, **kwargs):
        byte_string = request.httprequest.data
        data = json.loads(byte_string.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        try:
            user_id = request.session.authenticate(request.session.db, username, password)
        except Exception as e:
            return json.dumps({"error": "Invalid Username or Password."})
        if not user_id:
            return json.dumps({"error": "Invalid Username or Password."})
        env = request.env(user=user_id)
        env['res.users.apikeys.description'].check_access_make_key()
        token = env['res.users.apikeys']._generate("INRiM", username)
        payload = {
            'user_id': user_id,
            'username': username,
            'password': password,
            'token': token
        }
        return json.dumps({
            "data": payload,
            "responsedetail": {
                "messages": "UserValidated",
                "messagestype": 1,
                "responsecode": 200
            }
        })
    
    def authenticate_token(self, env, token):
        return env['res.users.apikeys']._check_credentials(scope="INRiM", key=token)

    @http.route('/api/employee', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_employee(self, model='res.users'):
        res = []
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            if not self.authenticate_token(env, token):
                raise UserError('Token non valido')
        #     partners = env[model].search([])
        #     for partner in partners:
        #         partner_vals = {
        #             'name': partner.name,
        #             'login': partner.login,
        #         }
        #         res.append(partner_vals)
        #     return Response(json.dumps(res,
        #                                 sort_keys=True, indent=4),
        #                     content_type='application/json;charset=utf-8',
        #                     status=200)
        # except Exception as e:
        #     return Response(
        #         json.dumps({'error': e.__str__(), 'status_code': 500},
        #                     sort_keys=True, indent=4),
        #         content_type='application/json;charset=utf-8', status=200)