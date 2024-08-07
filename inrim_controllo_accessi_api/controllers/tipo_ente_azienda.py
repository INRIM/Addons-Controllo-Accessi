from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiTipoEnteAzienda(http.Controller):

    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_tipo_ente_azienda(self):
        res = []
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            user_token = InrimApiController.authenticate_token(env, token)
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
            env['ca.tipo_ente_azienda'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.tipo_ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_tipo_ente_azienda_ids = env['ca.tipo_ente_azienda'].search([
            ('is_internal', '=', False)
        ])
        for tipo_ente_azienda in ca_tipo_ente_azienda_ids:
            vals = {
                'id': tipo_ente_azienda.id,
                'name': tipo_ente_azienda.name,
                'description': tipo_ente_azienda.description or '',
                'is_internal': tipo_ente_azienda.is_internal,
                'date_start': tipo_ente_azienda.date_start.strftime('%Y-%m-%d') if tipo_ente_azienda.date_start else '',
                'date_end': tipo_ente_azienda.date_end.strftime('%Y-%m-%d') if tipo_ente_azienda.date_end else ''
            }
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_ca_tipo_ente_azienda(self):
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            user_token = InrimApiController.authenticate_token(env, token)
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            'name': 'Name',
                            'description': 'Description',
                            'is_internal': 'False',
                            'date_start': '2024-01-01',
                            'date_end': '2024-12-31'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.tipo_ente_azienda'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.tipo_ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        name = data.get('name')
        description = data.get('description')
        is_internal = data.get('is_internal')
        date_start = data.get('date_start')
        date_end = data.get('date_end')
        if not name:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'name'",
                        'BodyHint': {
                            'name': 'Name',
                            'description': 'Description',
                            'is_internal': 'False',
                            'date_start': '2024-01-01',
                            'date_end': '2024-12-31'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            vals = {
                'name': name,
                'description': description or '',
                'is_internal': eval(is_internal) if is_internal else False,
                'date_start': date_start if date_start else False,
                'date_end': date_end if date_end else False
            }
            tipo_ente_azienda_id = env['ca.tipo_ente_azienda'].create(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': tipo_ente_azienda_id.id,
                    'name': tipo_ente_azienda_id.name,
                    'description': tipo_ente_azienda_id.description,
                    'is_internal': tipo_ente_azienda_id.is_internal,
                    'date_start': tipo_ente_azienda_id.date_start.strftime('%Y-%m-%d') if tipo_ente_azienda_id.date_start else '',
                    'date_end': tipo_ente_azienda_id.date_end.strftime('%Y-%m-%d') if tipo_ente_azienda_id.date_end else ''
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            env.cr.rollback()
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        
    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_ca_tipo_ente_azienda(self):
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        if 'token' in request.httprequest.headers:
            token = request.httprequest.headers.get('token')
            user_token = InrimApiController.authenticate_token(env, token)
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            'id': 1,
                            'name': 'Name',
                            'description': 'Description',
                            'is_internal': 'False',
                            'date_start': '2024-01-01',
                            'date_end': '2024-12-31'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.tipo_ente_azienda'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.tipo_ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        description = False
        if 'description' in data:
            description = data.get('description')
        is_internal = data.get('is_internal')
        date_start = False
        if 'date_start' in data:
            date_start = data.get('date_start')
        date_end = False
        if 'date_end' in data:
            date_end = data.get('date_end')
        if not id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'id'",
                        'BodyHint': {
                            'id': 1,
                            'name': 'Name',
                            'description': 'Description',
                            'is_internal': 'False',
                            'date_start': '2024-01-01',
                            'date_end': '2024-12-31'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.tipo_ente_azienda'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {id} nel model ca.tipo_ente_azienda"
                }, ensure_ascii=False, indent=4), status=400)
        vals = {}
        try:
            tipo_ente_azienda_id = env[
                'ca.tipo_ente_azienda'
            ].browse(int(id))
            if name:
                vals['name'] = name
            if description != False:
                vals['description'] = description
            if is_internal:
                vals['is_internal'] = eval(is_internal)
            if date_start != False:
                vals['date_start'] = date_start
            if date_end != False:
                vals['date_end'] = date_end
            if vals:
                tipo_ente_azienda_id.write(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': tipo_ente_azienda_id.id,
                    'name': tipo_ente_azienda_id.name,
                    'description': tipo_ente_azienda_id.description,
                    'is_internal': tipo_ente_azienda_id.is_internal,
                    'date_start': tipo_ente_azienda_id.date_start.strftime('%Y-%m-%d') if tipo_ente_azienda_id.date_start else '',
                    'date_end': tipo_ente_azienda_id.date_end.strftime('%Y-%m-%d') if tipo_ente_azienda_id.date_end else ''
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)