from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
import json

class TokenController(http.Controller):

    def authenticate_token(self, env, token):
        return env['res.users.apikeys']._check_credentials(scope="INRiM", key=token)
    
    @http.route('/token/authenticate', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self, **kwargs):
        byte_string = request.httprequest.data
        data = json.loads(byte_string.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        try:
            user_id = request.session.authenticate(request.session.db, username, password)
        except Exception as e:
            return Response(json.dumps({
                "error": "Invalid Username or Password."
            }, ensure_ascii=False, indent=4), status=400)
        if not user_id:
            return Response(json.dumps({
                "error": "Invalid Username or Password."
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

    @http.route('/api/persona', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_persona(self):
        res = []
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            user_token = self.authenticate_token(env, token)
            user_id = env['res.users'].browse(user_token)
            request.update_env(user=user_id)
            env.user = user_id
            if not user_token:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'token': 'Token non valido'
                    }
                }, ensure_ascii=False, indent=4), status=400)
        else:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'token': 'Token non presente'
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.persona'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso al record ca.persona"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_persona_ids = env['ca.persona'].search([])
        for persona in ca_persona_ids:
            vals = {
                'id': persona.id,
                'name': persona.name,
                'lastname': persona.lastname,
                'fiscalcode': persona.fiscalcode,
                'parent_id': persona.parent_id.display_name or "",
                'associated_user_id': persona.associated_user_id.display_name or "",
                'domicile_street': persona.domicile_street,
                'domicile_street2': persona.domicile_street2,
                'domicile_city': persona.domicile_city,
                'domicile_state_id': persona.domicile_state_id.name or "",
                'domicile_zip': persona.domicile_zip,
                'domicile_country_id': persona.domicile_country_id.name or "",
                'vat': persona.vat,
                'type_ids': ",".join(p.name for p in persona.type_ids),
                'freshman': persona.freshman,
                'ca_ente_azienda_ids': ",".join(p.name for p in persona.ca_ente_azienda_ids),
                'nationality': persona.nationality.name or "",
                'birth_date': persona.birth_date.strftime("%d/%m/%Y") if persona.birth_date else "",
                'birth_place': persona.birth_place,
                'istat_code': persona.istat_code,
                'present': persona.present,
                'token': persona.token,
                'residence_street': persona.residence_street,
                'residence_street2': persona.residence_street2,
                'residence_city': persona.residence_city,
                'residence_state_id': persona.residence_state_id.name or "",
                'residence_zip': persona.residence_zip,
                'residence_country_id': persona.residence_country_id.name or "",
                'ca_documento_ids': []
            }
            for doc in persona.ca_documento_ids:
                vals['ca_documento_ids'].append({
                    'tipo_documento_id': doc.tipo_documento_id.display_name or "",
                    'validity_start_date': doc.validity_start_date.strftime("%d/%m/%Y") if doc.validity_start_date else "",
                    'validity_end_date': doc.validity_end_date.strftime("%d/%m/%Y") if doc.validity_end_date else "",
                    'issued_by': doc.issued_by,
                    'document_code': doc.document_code,
                    'image_ids': [],
                    'ca_stato_documento_id': doc.ca_stato_documento_id.display_name or ""
                })
                for img in doc.image_ids:
                    vals['ca_documento_ids'][-1]['image_ids'].append({
                        'name': img.name,
                        'description': img.description,
                        'ca_tipo_documento_id': img.ca_tipo_documento_id.display_name or "",
                        'side': img.side,
                        'image': img.image.decode("utf-8"),
                        'filename': img.filename,
                    })
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)