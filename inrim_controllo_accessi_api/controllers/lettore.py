from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiLettore(http.Controller):

    @http.route('/api/lettore', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_lettore(self):
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
            env['ca.lettore'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.lettore"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        res = []
        lettore_ids = env['ca.lettore'].search([])
        for lettore in lettore_ids:
            vals = {
                'id': lettore.id,
                'name': lettore.name,
                'reader_ip': lettore.reader_ip,
                'direction': dict(lettore._fields['direction'].selection).get(lettore.direction),
                'device_id': lettore.device_id or "",
                'type': lettore.type or "",
                'mode': lettore.mode or "",
                'mode_type': lettore.mode_type or "",
                'reader_status': lettore.reader_status or "",
                'available_events': lettore.available_events,
                'system_error': lettore.system_error,
                'error_code': lettore.error_code or ""
            }
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/lettore', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_ca_lettore(self):
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
                'BodyHint': {
                    "name": "Test",
                    "reader_ip": "127.0.0.1",
                    "direction": "In",
                    "device_id": "Device ID",
                    "type": "Type",
                    "mode": "Mode",
                    "mode_type": "Mode Type",
                    "reader_status": "Reader Status",
                    "available_events": 3,
                    "error_code": "0000"
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.lettore'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.lettore"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        name = data.get('name')
        reader_ip = data.get('reader_ip')
        direction = data.get('direction')
        if not name:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'name'",
                    'BodyHint': {
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not reader_ip:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'reader_ip'",
                    'BodyHint': {
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not direction:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'direction'",
                    'BodyHint': {
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            lettore = env['ca.lettore']
            selection_items = dict(lettore._fields['direction'].selection)
            for key, value in selection_items.items():
                if direction == value:
                    direction = key
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        device_id = data.get('device_id')
        type = data.get('type')
        mode = data.get('mode')
        mode_type = data.get('mode_type')
        reader_status = data.get('reader_status')
        available_events = data.get('available_events')
        error_code = data.get('error_code')
        try:
            vals = {
                'name': name,
                'reader_ip': reader_ip,
                'direction': direction,
                'device_id': device_id,
                'type': type,
                'mode': mode,
                'mode_type': mode_type,
                'reader_status': reader_status,
                'available_events': available_events,
                'error_code': error_code
            }
            lettore_id = env['ca.lettore'].create(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    "id": lettore_id.id,
                    "name": lettore_id.name,
                    "reader_ip": lettore_id.reader_ip,
                    "direction": dict(lettore_id._fields['direction'].selection).get(lettore_id.direction),
                    "device_id": lettore_id.device_id or "",
                    "type": lettore_id.type or "",
                    "mode": lettore_id.mode or "",
                    "mode_type": lettore_id.mode_type or "",
                    "reader_status": lettore_id.reader_status or "",
                    "available_events": lettore_id.available_events,
                    "system_error": lettore_id.system_error,
                    "error_code": lettore_id.error_code or ""
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
        
    @http.route('/api/lettore', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_ca_lettore(self):
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
                        "id": 1,
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.lettore'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.lettore"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        reader_ip = data.get('reader_ip')
        direction = data.get('direction')
        if not id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'id'",
                    'BodyHint': {
                        "id": 1,
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not name:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'name'",
                    'BodyHint': {
                        "id": 1,
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not reader_ip:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'reader_ip'",
                    'BodyHint': {
                        "id": 1,
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not direction:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'direction'",
                    'BodyHint': {
                        "id": 1,
                        "name": "Test",
                        "reader_ip": "127.0.0.1",
                        "direction": "In",
                        "device_id": "Device ID",
                        "type": "Type",
                        "mode": "Mode",
                        "mode_type": "Mode Type",
                        "reader_status": "Reader Status",
                        "available_events": 3,
                        "error_code": "0000"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            lettore = env['ca.lettore']
            selection_items = dict(lettore._fields['direction'].selection)
            for key, value in selection_items.items():
                if direction == value:
                    direction = key
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.lettore'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {id} nel model ca.lettore"
                }, ensure_ascii=False, indent=4), status=400)
        try:
            lettore_id = env[
                'ca.lettore'
            ].browse(int(id))
            vals = {
                'name': name,
                'reader_ip': reader_ip,
                'direction': direction,
            }
            if 'device_id' in data:
                vals['device_id'] = data.get('device_id')
            if 'type' in data:
                vals['type'] = data.get('type')
            if 'mode' in data:
                vals['mode'] = data.get('mode')
            if 'mode_type' in data:
                vals['mode_type'] = data.get('mode_type')
            if 'reader_status' in data:
                vals['reader_status'] = data.get('reader_status')
            if 'available_events' in data:
                vals['available_events'] = data.get('available_events')
            if 'error_code' in data:
                vals['error_code'] = data.get('error_code')
            lettore_id.write(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    "id": lettore_id.id,
                    "name": lettore_id.name,
                    "reader_ip": lettore_id.reader_ip,
                    "direction": dict(lettore_id._fields['direction'].selection).get(lettore_id.direction),
                    "device_id": lettore_id.device_id,
                    "type": lettore_id.type,
                    "mode": lettore_id.mode,
                    "mode_type": lettore_id.mode_type,
                    "reader_status": lettore_id.reader_status,
                    "available_events": lettore_id.available_events,
                    "system_error": lettore_id.system_error,
                    "error_code": lettore_id.error_code
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)