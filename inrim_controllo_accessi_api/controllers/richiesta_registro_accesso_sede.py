from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiRichiestaRegistroAccessoSede(http.Controller):

    @http.route('/api/richiesta_registro_accesso_sede', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_richiesta_registro_accesso_sede(self):
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
            env['ca.richiesta_riga_accesso_sede'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.richiesta_riga_accesso_sede"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        user_tz = env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz)
        ca_richiesta_riga_accesso_sede_ids = env['ca.richiesta_riga_accesso_sede'].search([])
        for richiesta in ca_richiesta_riga_accesso_sede_ids:
            datetime_event_user_tz = pytz.utc.localize(richiesta.datetime_event).astimezone(user_tz)
            vals = {
                'id': richiesta.id,
                'persona_id': richiesta.persona_id.token,
                'ente_azienda_id': richiesta.ente_azienda_id.display_name,
                'punto_accesso_id': richiesta.punto_accesso_id.display_name,
                'direction': richiesta.direction,
                'datetime_event': datetime_event_user_tz.strftime("%Y-%m-%dT%H:%M:%S")
            }
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/richiesta_registro_accesso_sede', auth="none", type='http', methods=['DELETE'],
           csrf=False)
    def api_delete_ca_richiesta_registro_accesso_sede(self):
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
                        'MissingBody': "Per poter eliminare un record, é necessario che nel body venga specificato l'id del record da eliminare"
                    }
                }, ensure_ascii=False, indent=4), status=400)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        if not id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'MissingBody': "Per poter eliminare un record, é necessario che nel body venga specificato l'id del record da eliminare"
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.richiesta_riga_accesso_sede'].with_user(env.user).check_access_rights('unlink')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di cancellare i record di ca.richiesta_riga_accesso_sede"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        try:
            user_tz = env.user.tz or 'UTC'
            user_tz = pytz.timezone(user_tz)
            ca_richiesta_riga_accesso_sede_id = env['ca.richiesta_riga_accesso_sede'].browse(int(id))
            if ca_richiesta_riga_accesso_sede_id:
                datetime_event_user_tz = pytz.utc.localize(ca_richiesta_riga_accesso_sede_id.datetime_event).astimezone(user_tz)
                vals = {
                    'id': ca_richiesta_riga_accesso_sede_id.id,
                    'persona_id': ca_richiesta_riga_accesso_sede_id.persona_id.token,
                    'ente_azienda_id': ca_richiesta_riga_accesso_sede_id.ente_azienda_id.display_name,
                    'punto_accesso_id': ca_richiesta_riga_accesso_sede_id.punto_accesso_id.display_name,
                    'direction': ca_richiesta_riga_accesso_sede_id.direction,
                    'datetime_event': datetime_event_user_tz.strftime("%Y-%m-%dT%H:%M:%S")
                }
                ca_richiesta_riga_accesso_sede_id.unlink()
                return Response(json.dumps({
                    "header": {
                        'response': 200
                    },
                    "body": vals
                }, ensure_ascii=False, indent=4), status=200)
        except:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Non é stato trovato nessun record con id {id}"
            }, ensure_ascii=False, indent=4), status=400)
        
    @http.route('/api/richiesta_registro_accesso_sede', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_ca_richiesta_registro_accesso_sede(self):
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
                            'persona_id': '6xERuNlgy3',
                            'ente_azienda_id': 'Campus',
                            'punto_accesso_id': '1p001 Lettore 1',
                            'datetime_event': '2024-12-31 00:00:00'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.richiesta_riga_accesso_sede'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.richiesta_riga_accesso_sede"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        persona_id = data.get('persona_id')
        ente_azienda_id = data.get('ente_azienda_id')
        punto_accesso_id = data.get('punto_accesso_id')
        datetime_event = data.get('datetime_event')
        if (
            not persona_id or not ente_azienda_id or
            not punto_accesso_id or not datetime_event
        ):
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            'persona_id': '6xERuNlgy3',
                            'ente_azienda_id': 'Campus',
                            'punto_accesso_id': '1p001 Lettore 1',
                            'datetime_event': '2024-12-31 00:00:00'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if type(persona_id) == str:
            persona = env['ca.persona'].search([('token', '=', persona_id)])
            if not persona:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con token '{persona_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            persona_id = persona.id
        elif type(persona_id) == int:
            try:
                env['ca.persona'].browse(persona_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con id '{persona_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if type(ente_azienda_id) == str:
            ente_azienda = env['ca.ente_azienda'].search([('name', '=', ente_azienda_id)])
            if not ente_azienda:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"L'ente azienda '{ente_azienda_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            ente_azienda_id = ente_azienda.id
        elif type(ente_azienda_id) == int:
            try:
                env['ca.ente_azienda'].browse(persona_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con id '{persona_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if type(punto_accesso_id) == str:
            punto_accesso = env['ca.punto_accesso'].search([('name', '=', punto_accesso_id)])
            if not punto_accesso:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il punto accesso '{punto_accesso_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            punto_accesso_id = punto_accesso.id
        elif type(punto_accesso_id) == int:
            try:
                env['ca.punto_accesso'].browse(punto_accesso_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il punto accesso con id '{punto_accesso_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        user_tz = env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz)
        try:
            dt_naive = datetime.strptime(datetime_event, "%Y-%m-%d %H:%M:%S")
            utc_offset = user_tz.utcoffset(dt_naive)
            dt_utc_naive = dt_naive - utc_offset
            create_vals = {
                'persona_id': persona_id,
                'ente_azienda_id': ente_azienda_id,
                'punto_accesso_id': punto_accesso_id,
                'datetime_event': dt_utc_naive
            }
            richiesta_riga_accesso_sede_id = env['ca.richiesta_riga_accesso_sede'].create(create_vals)
            datetime_event_user_tz = pytz.utc.localize(richiesta_riga_accesso_sede_id.datetime_event).astimezone(user_tz)
            vals = {
                'id': richiesta_riga_accesso_sede_id.id,
                'persona_id': richiesta_riga_accesso_sede_id.persona_id.token,
                'ente_azienda_id': richiesta_riga_accesso_sede_id.ente_azienda_id.name,
                'punto_accesso_id': richiesta_riga_accesso_sede_id.punto_accesso_id.name,
                'datetime_event': datetime_event_user_tz.strftime("%Y/-%m-%dT%H:%M:%S")
            }
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": vals
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            env.cr.rollback()
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        
    @http.route('/api/richiesta_registro_accesso_sede', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_ca_richiesta_registro_accesso_sede(self):
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
                            'persona_id': '6xERuNlgy3',
                            'ente_azienda_id': 'Campus',
                            'punto_accesso_id': '1p001 Lettore 1',
                            'datetime_event': '2024-12-31 00:00:00'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.richiesta_riga_accesso_sede'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.richiesta_riga_accesso_sede"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        persona_id = data.get('persona_id')
        ente_azienda_id = data.get('ente_azienda_id')
        punto_accesso_id = data.get('punto_accesso_id')
        datetime_event = data.get('datetime_event')
        if not id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'id'",
                        'BodyHint': {
                            'id': 1,
                            'persona_id': "",
                            'ente_azienda_id': "",
                            'punto_accesso_id': "",
                            'datetime_event': ""
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if id:
            try:
                env['ca.richiesta_riga_accesso_sede'].browse(int(id)).display_name
            except:
                return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        "body": f"Non é stato trovato nessun record con id {id} nel model ca.richiesta_riga_accesso_sede"
                    }, ensure_ascii=False, indent=4), status=400)
        if persona_id and type(persona_id) == str:
            persona = env['ca.persona'].search([('token', '=', persona_id)])
            if not persona:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con token '{persona_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            persona_id = persona.id
        elif persona_id and type(persona_id) == int:
            try:
                env['ca.persona'].browse(int(persona_id)).display_name
            except:
                return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        "body": f"La persona con id {persona_id} non esiste"
                    }, ensure_ascii=False, indent=4), status=400)
        if ente_azienda_id and type(ente_azienda_id) == str:
            ente_azienda = env['ca.ente_azienda'].search([('name', '=', ente_azienda_id)])
            if not ente_azienda:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"L'ente azienda '{ente_azienda_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            ente_azienda_id = ente_azienda.id
        elif ente_azienda_id and type(ente_azienda_id) == int:
            try:
                env['ca.ente_azienda'].browse(persona_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con id '{persona_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if punto_accesso_id and type(punto_accesso_id) == str:
            punto_accesso = env['ca.punto_accesso'].search([('name', '=', punto_accesso_id)])
            if not punto_accesso:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il punto accesso '{punto_accesso_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            punto_accesso_id = punto_accesso.id
        elif punto_accesso_id and type(punto_accesso_id) == int:
            try:
                env['ca.punto_accesso'].browse(punto_accesso_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il punto accesso con id '{punto_accesso_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        vals = {}
        user_tz = env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz)
        try:
            richiesta_riga_accesso_sede_id = env[
                'ca.richiesta_riga_accesso_sede'
            ].browse(int(id))
            if persona_id:
                vals['persona_id'] = persona_id
            if ente_azienda_id:
                vals['ente_azienda_id'] = ente_azienda_id
            if punto_accesso_id:
                vals['punto_accesso_id'] = punto_accesso_id
            if datetime_event:
                dt_naive = datetime.strptime(datetime_event, "%Y-%m-%d %H:%M:%S")
                utc_offset = user_tz.utcoffset(dt_naive)
                dt_utc_naive = dt_naive - utc_offset
                vals['datetime_event'] = dt_utc_naive
            if vals:
                richiesta_riga_accesso_sede_id.write(vals)
            datetime_event_user_tz = pytz.utc.localize(richiesta_riga_accesso_sede_id.datetime_event).astimezone(user_tz)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': richiesta_riga_accesso_sede_id.id,
                    'persona_id': richiesta_riga_accesso_sede_id.persona_id.token,
                    'ente_azienda_id': richiesta_riga_accesso_sede_id.ente_azienda_id.name,
                    'punto_accesso_id': richiesta_riga_accesso_sede_id.punto_accesso_id.name,
                    'datetime_event': datetime_event_user_tz.strftime("%Y-%m-%dT%H:%M:%S")
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)