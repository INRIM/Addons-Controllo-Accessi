from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from datetime import datetime
import pytz
import json

class InrimApiController(http.Controller):

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
                "error": "Invalid Username or Password.",
                'BodyHint': {
                    "username": "admin",
                    "password": "admin"
                }
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
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.persona"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        vals = {}
        ca_persona_ids = env['ca.persona'].search([])
        for persona in ca_persona_ids:
            persona = persona.with_context(lang=env.user.lang)
            if env.user.has_group('inrim_controllo_accessi_base.ca_gdpr'):
                vals.update({
                    'fiscalcode': persona.fiscalcode,
                    'freshman': persona.freshman or "",
                    'nationality': persona.nationality.name or "",
                    'birth_date': persona.birth_date.strftime("%Y/%m/%d") if persona.birth_date else "",
                    'birth_place': persona.birth_place or "",
                    'istat_code': persona.istat_code or "",
                })
            vals.update({
                'id': persona.id,
                'name': persona.name,
                'lastname': persona.lastname,
                'parent_id': persona.parent_id.display_name or "",
                'associated_user_id': persona.associated_user_id.display_name or "",
                'domicile_street': persona.domicile_street or "",
                'domicile_street2': persona.domicile_street2 or "",
                'domicile_city': persona.domicile_city or "",
                'domicile_state_id': persona.domicile_state_id.name or "",
                'domicile_zip': persona.domicile_zip or "",
                'domicile_country_id': persona.domicile_country_id.name or "",
                'vat': persona.vat or "",
                'type_ids': ",".join(p.name for p in persona.type_ids),
                'freshman': persona.freshman or "",
                'ca_ente_azienda_ids': ",".join(p.name for p in persona.ca_ente_azienda_ids),
                'present': persona.present or "",
                'token': persona.token or "",
                'residence_street': persona.residence_street or "",
                'residence_street2': persona.residence_street2 or "",
                'residence_city': persona.residence_city or "",
                'residence_state_id': persona.residence_state_id.name or "",
                'residence_zip': persona.residence_zip or "",
                'residence_country_id': persona.residence_country_id.name or "",
                'ca_documento_ids': []
            })
            if env.user.has_group('inrim_controllo_accessi_base.ca_gdpr'):
                for doc in persona.ca_documento_ids:
                    vals['ca_documento_ids'].append({
                        'tipo_documento_id': doc.tipo_documento_id.display_name or "",
                        'validity_start_date': doc.validity_start_date.strftime("%Y/%m/%d") if doc.validity_start_date else "",
                        'validity_end_date': doc.validity_end_date.strftime("%Y/%m/%d") if doc.validity_end_date else "",
                        'issued_by': doc.issued_by or "",
                        'document_code': doc.document_code or "",
                        'image_ids': [],
                        'ca_stato_documento_id': doc.ca_stato_documento_id.display_name or ""
                    })
                    for img in doc.image_ids:
                        vals['ca_documento_ids'][-1]['image_ids'].append({
                            'name': img.name,
                            'description': img.description or "",
                            'ca_tipo_documento_id': img.ca_tipo_documento_id.display_name or "",
                            'side': img.side or "",
                            'image': img.image.decode("utf-8"),
                            'filename': img.filename or "",
                        })
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/richiesta_registro_accesso_sede', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_richiesta_registro_accesso_sede(self):
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
                'persona_id': richiesta.persona_id.display_name,
                'ente_azienda_id': richiesta.ente_azienda_id.display_name,
                'punto_accesso_id': richiesta.punto_accesso_id.display_name,
                'direction': richiesta.direction,
                'datetime_event': datetime_event_user_tz.strftime("%Y/%m/%dT%H:%M:%S")
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
                    'persona_id': ca_richiesta_riga_accesso_sede_id.persona_id.display_name,
                    'ente_azienda_id': ca_richiesta_riga_accesso_sede_id.ente_azienda_id.display_name,
                    'punto_accesso_id': ca_richiesta_riga_accesso_sede_id.punto_accesso_id.display_name,
                    'direction': ca_richiesta_riga_accesso_sede_id.direction,
                    'datetime_event': datetime_event_user_tz.strftime("%Y/%m/%dT%H:%M:%S")
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            'persona_id': 'Persona 1',
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
                            'persona_id': 'Persona 1',
                            'ente_azienda_id': 'Campus',
                            'punto_accesso_id': '1p001 Lettore 1',
                            'datetime_event': '2024-12-31 00:00:00'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if type(persona_id) == str:
            persona = env['ca.persona'].search([('display_name', '=', persona_id)])
            if not persona:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona '{persona_id}' inserita non esiste",
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
                'persona_id': richiesta_riga_accesso_sede_id.persona_id.display_name,
                'ente_azienda_id': richiesta_riga_accesso_sede_id.ente_azienda_id.name,
                'punto_accesso_id': richiesta_riga_accesso_sede_id.punto_accesso_id.name,
                'datetime_event': datetime_event_user_tz.strftime("%Y/%m/%dT%H:%M:%S")
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            'id': 1,
                            'persona_id': 'Persona 1',
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
            persona = env['ca.persona'].search([('display_name', '=', persona_id)])
            if not persona:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona '{persona_id}' inserita non esiste",
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
                    'persona_id': richiesta_riga_accesso_sede_id.persona_id.display_name,
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
        
    @http.route('/api/tipo_ente_azienda', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_tipo_ente_azienda(self):
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
        
    @http.route('/api/ente_azienda', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_ente_azienda(self):
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
            env['ca.ente_azienda'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_ente_azienda_ids = env['ca.ente_azienda'].search([])
        for ente_azienda in ca_ente_azienda_ids:
            vals = {
                'id': ente_azienda.id,
                'name': ente_azienda.name,
                'parent_id': ente_azienda.parent_id.name or "",
                'all_child_ids': ",".join(c.name for c in ente_azienda.all_child_ids),
                'parent_path': ente_azienda.parent_path or "",
                'street': ente_azienda.street or "",
                'street2': ente_azienda.street2 or "",
                'city': ente_azienda.city or "",
                'state_id': ente_azienda.state_id.name or "",
                'zip': ente_azienda.zip or "",
                'country_id': ente_azienda.country_id.name or "",
                'vat': ente_azienda.vat or "",
                'note': ente_azienda.note or "",
                'email': ente_azienda.email or "",
                'phone': ente_azienda.phone or "",
                'mobile': ente_azienda.mobile or "",
                'website': ente_azienda.website or "",
                'pec': ente_azienda.pec or "",
                'company_id': ente_azienda.company_id.name,
                'tipo_ente_azienda_id': ente_azienda.tipo_ente_azienda_id.name,
                'ca_persona_ids': ",".join(p.display_name for p in ente_azienda.ca_persona_ids),
                'ref': ente_azienda.ref,
                'lock': ente_azienda.lock,

            }
            if env.user.has_group('inrim_controllo_accessi_base.ca_tech'):
                ca_tech_vals = {
                    'url_gateway_lettori': ente_azienda.url_gateway_lettori,
                    'nome_chiave_header': ente_azienda.nome_chiave_header,
                    'jwt': ente_azienda.jwt
                }
                vals.update(ca_tech_vals)
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/ente_azienda', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_ca_ente_azienda(self):
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'BodyHint': {
                        "name": "Test Put",
                        "parent_id": "Sede 1",
                        "parent_path": "",
                        "street": "Street",
                        "street2": "Street2",
                        "city": "City",
                        "state_id": "Taranto",
                        "zip": "Zip",
                        "country_id": "Italia",
                        "vat": "Vat",
                        "note": "Ente Azienda 1",
                        "email": "Email",
                        "phone": "Phone",
                        "mobile": "Mobile",
                        "website": "Website",
                        "pec": "Pec Test",
                        "company_id": "Istituto Nazionale di Ricerca Metrologica",
                        "tipo_ente_azienda_id": "Sede Distaccata",
                        "ca_persona_ids": ["Persona 1, Persona 2"],
                        "ref": True,
                        "lock": False,
                        "url_gateway_lettori": "In base al sistema",
                        "nome_chiave_header": "In base al sistema",
                        "jwt": "In base al sistema"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.ente_azienda'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        name = data.get('name')
        pec = data.get('pec')
        tipo_ente_azienda_id = data.get('tipo_ente_azienda_id')
        if not name:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'name'",
                    'BodyHint': {
                        "name": "Test Put",
                        "parent_id": "Sede 1",
                        "parent_path": "",
                        "street": "Street",
                        "street2": "Street2",
                        "city": "City",
                        "state_id": "Taranto",
                        "zip": "Zip",
                        "country_id": "Italia",
                        "vat": "Vat",
                        "note": "Ente Azienda 1",
                        "email": "Email",
                        "phone": "Phone",
                        "mobile": "Mobile",
                        "website": "Website",
                        "pec": "Pec Test",
                        "company_id": "Istituto Nazionale di Ricerca Metrologica",
                        "tipo_ente_azienda_id": "Sede Distaccata",
                        "ca_persona_ids": ["Persona 1, Persona 2"],
                        "ref": True,
                        "lock": False,
                        "url_gateway_lettori": "In base al sistema",
                        "nome_chiave_header": "In base al sistema",
                        "jwt": "In base al sistema"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not pec:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'pec'",
                    'BodyHint': {
                        "name": "Test Put",
                        "parent_id": "Sede 1",
                        "parent_path": "",
                        "street": "Street",
                        "street2": "Street2",
                        "city": "City",
                        "state_id": "Taranto",
                        "zip": "Zip",
                        "country_id": "Italia",
                        "vat": "Vat",
                        "note": "Ente Azienda 1",
                        "email": "Email",
                        "phone": "Phone",
                        "mobile": "Mobile",
                        "website": "Website",
                        "pec": "Pec Test",
                        "company_id": "Istituto Nazionale di Ricerca Metrologica",
                        "tipo_ente_azienda_id": "Sede Distaccata",
                        "ca_persona_ids": ["Persona 1, Persona 2"],
                        "ref": True,
                        "lock": False,
                        "url_gateway_lettori": "In base al sistema",
                        "nome_chiave_header": "In base al sistema",
                        "jwt": "In base al sistema"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not tipo_ente_azienda_id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'tipo_ente_azienda_id'",
                    'BodyHint': {
                        "name": "Test Put",
                        "parent_id": "Sede 1",
                        "parent_path": "",
                        "street": "Street",
                        "street2": "Street2",
                        "city": "City",
                        "state_id": "Taranto",
                        "zip": "Zip",
                        "country_id": "Italia",
                        "vat": "Vat",
                        "note": "Ente Azienda 1",
                        "email": "Email",
                        "phone": "Phone",
                        "mobile": "Mobile",
                        "website": "Website",
                        "pec": "Pec Test",
                        "company_id": "Istituto Nazionale di Ricerca Metrologica",
                        "tipo_ente_azienda_id": "Sede Distaccata",
                        "ca_persona_ids": ["Persona 1, Persona 2"],
                        "ref": True,
                        "lock": False,
                        "url_gateway_lettori": "In base al sistema",
                        "nome_chiave_header": "In base al sistema",
                        "jwt": "In base al sistema"
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        parent_id = data.get('parent_id')
        parent_path = data.get('parent_path')
        street = data.get('street')
        street2 = data.get('street2')
        city = data.get('city')
        state_id = data.get('state_id')
        zip = data.get('zip')
        country_id = data.get('country_id')
        vat = data.get('vat')
        note = data.get('note')
        email = data.get('email')
        phone = data.get('phone')
        mobile = data.get('mobile')
        website = data.get('website')
        company_id = data.get('company_id')
        ca_persona_ids = data.get('ca_persona_ids')
        ref = data.get('ref')
        lock = data.get('lock')
        url_gateway_lettori = data.get('url_gateway_lettori')
        nome_chiave_header = data.get('nome_chiave_header')
        jwt = data.get('jwt')
        if tipo_ente_azienda_id and type(tipo_ente_azienda_id) == str:
            tipo_ente_azienda = env['ca.tipo_ente_azienda'].search([('name', '=', tipo_ente_azienda_id)])
            if not tipo_ente_azienda:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il tipo ente azienda '{tipo_ente_azienda_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            tipo_ente_azienda_id = tipo_ente_azienda.id
        if parent_id and type(parent_id) == str:
            parent = env['ca.ente_azienda'].search([('name', '=', parent_id)])
            if not parent:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il parent_id '{parent_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            parent_id = parent.id
        if country_id and type(country_id) == str:
            country = env['res.country'].with_context(lang=env.user.lang).search([('name', '=', country_id)])
            if not country:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La provincia '{country_id}' inserita non esiste in odoo",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            country_id = country.id
        if state_id and type(state_id) == str:
            state = env['res.country.state'].with_context(lang=env.user.lang).search([('name', '=', state_id)])
            if not state:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La città '{state_id}' inserita non esiste in odoo",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            state_id = state.id
        if company_id and type(company_id) == str:
            company = env['res.company'].search([('name', '=', company_id)])
            if not company:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La company '{company_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            company_id = company.id
            ca_persona_vals = []
            for persona in ca_persona_ids:
                if persona and type(persona) == str:
                    ca_persona = env['ca.persona'].search([('display_name', '=', persona)])
                    if not ca_persona:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': f"La persona '{persona}' inserita non esiste",
                            }
                        }, ensure_ascii=False, indent=4), status=400)
                    ca_persona_vals.append(ca_persona.id)
                elif persona and type(persona) == int:
                    ca_persona = env['ca.persona'].browse(persona)
                    if not ca_persona:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': f"La persona con id '{persona}' non esiste",
                            }
                        }, ensure_ascii=False, indent=4), status=400)
                    ca_persona_vals.append(persona)
            ca_persona_ids = ca_persona_vals
        try:
            vals = {
                'name': name,
                'pec': pec,
                'tipo_ente_azienda_id': tipo_ente_azienda_id,
                'parent_id': parent_id if parent_id else False,
                'parent_path': parent_path if parent_path else False,
                'street': street if street else False,
                'street2': street2 if street2 else False,
                'city': city if city else False,
                'state_id': state_id if state_id else False,
                'zip': zip if zip else False,
                'country_id': country_id if country_id else False,
                'vat': vat if vat else False,
                'note': note if note else False,
                'email': email if email else False,
                'phone': phone if phone else False,
                'mobile': mobile if mobile else False,
                'website': website if website else False,
                'company_id': company_id if company_id else False,
                'ca_persona_ids': ca_persona_ids if ca_persona_ids else False,
                'ref': eval(ref) if ref else False,
                'lock': eval(lock) if lock else False,
                'url_gateway_lettori': url_gateway_lettori if url_gateway_lettori else False,
                'nome_chiave_header': nome_chiave_header if nome_chiave_header else False,
                'jwt': jwt if jwt else False
            }
            ente_azienda_id = env['ca.ente_azienda'].with_context(lang=env.user.lang).create(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    "id": ente_azienda_id.id,
                    "name": ente_azienda_id.name,
                    "parent_id": ente_azienda_id.parent_id.name,
                    "all_child_ids": ",".join(c.name for c in ente_azienda_id.all_child_ids),
                    "parent_path": ente_azienda_id.parent_path,
                    "street": ente_azienda_id.street,
                    "street2": ente_azienda_id.street2,
                    "city": ente_azienda_id.city,
                    "state_id": ente_azienda_id.state_id.name,
                    "zip": ente_azienda_id.zip,
                    "country_id": ente_azienda_id.country_id.name,
                    "vat": ente_azienda_id.vat,
                    "note": ente_azienda_id.note,
                    "email": ente_azienda_id.email,
                    "phone": ente_azienda_id.phone,
                    "mobile": ente_azienda_id.mobile,
                    "website": ente_azienda_id.website,
                    "pec": ente_azienda_id.pec,
                    "company_id": ente_azienda_id.company_id.name,
                    "tipo_ente_azienda_id": ente_azienda_id.tipo_ente_azienda_id.name,
                    "ca_persona_ids": ",".join(p.display_name for p in ente_azienda_id.ca_persona_ids),
                    "ref": ente_azienda_id.ref,
                    "lock": ente_azienda_id.lock,
                    "url_gateway_lettori": ente_azienda_id.url_gateway_lettori,
                    "nome_chiave_header": ente_azienda_id.nome_chiave_header,
                    "jwt": ente_azienda_id.jwt
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
        
    @http.route('/api/ente_azienda', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_ca_ente_azienda(self):
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
        byte_string = request.httprequest.data
        if not byte_string:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'BodyHint': {
                            "id": 1,
                            "name": "Test Put",
                            "parent_id": "Sede 1",
                            "parent_path": "",
                            "street": "Street",
                            "street2": "Street2",
                            "city": "City",
                            "state_id": "Taranto",
                            "zip": "Zip",
                            "country_id": "Italia",
                            "vat": "Vat",
                            "note": "Ente Azienda 1",
                            "email": "Email",
                            "phone": "Phone",
                            "mobile": "Mobile",
                            "website": "Website",
                            "pec": "Pec Test",
                            "company_id": "Istituto Nazionale di Ricerca Metrologica",
                            "tipo_ente_azienda_id": "Sede Distaccata",
                            "ca_persona_ids": ["Persona 1, Persona 2"],
                            "ref": True,
                            "lock": False,
                            "url_gateway_lettori": "In base al sistema",
                            "nome_chiave_header": "In base al sistema",
                            "jwt": "In base al sistema"
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.ente_azienda'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.ente_azienda"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        parent_id = data.get('parent_id')
        parent_path = data.get('parent_path')
        street = data.get('street')
        street2 = data.get('street2')
        city = data.get('city')
        state_id = data.get('state_id')
        zip = data.get('zip')
        country_id = data.get('country_id')
        vat = data.get('vat')
        note = data.get('note')
        email = data.get('email')
        phone = data.get('phone')
        mobile = data.get('mobile')
        website = data.get('website')
        pec = data.get('pec')
        company_id = data.get('company_id')
        tipo_ente_azienda_id = data.get('tipo_ente_azienda_id')
        ca_persona_ids = data.get('ca_persona_ids')
        ref = data.get('ref')
        lock = data.get('lock')
        url_gateway_lettori = data.get('url_gateway_lettori')
        nome_chiave_header = data.get('nome_chiave_header')
        jwt = data.get('jwt')
        if not id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'id'",
                        'BodyHint': {
                            "id": 1,
                            "name": "Test Put",
                            "parent_id": "Sede 1",
                            "parent_path": "",
                            "street": "Street",
                            "street2": "Street2",
                            "city": "City",
                            "state_id": "Taranto",
                            "zip": "Zip",
                            "country_id": "Italia",
                            "vat": "Vat",
                            "note": "Ente Azienda 1",
                            "email": "Email",
                            "phone": "Phone",
                            "mobile": "Mobile",
                            "website": "Website",
                            "pec": "Pec Test",
                            "company_id": "Istituto Nazionale di Ricerca Metrologica",
                            "tipo_ente_azienda_id": "Sede Distaccata",
                            "ca_persona_ids": ["Persona 1, Persona 2"],
                            "ref": True,
                            "lock": False,
                            "url_gateway_lettori": "In base al sistema",
                            "nome_chiave_header": "In base al sistema",
                            "jwt": "In base al sistema"
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.ente_azienda'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Non é stato trovato nessun record con id {id} nel model ca.ente_azienda"
            }, ensure_ascii=False, indent=4), status=400)
        try:
            ente_azienda_id = env[
                'ca.ente_azienda'
            ].browse(int(id))
            vals = {
                'name': name,
            }
            # parent_id
            if parent_id and type(parent_id) == str and parent_id != "":
                parent = env['ca.ente_azienda'].search([('name', '=', parent_id)])
                if not parent:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"L' ente azienda '{parent_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['parent_id'] = parent.id
            elif parent_id and type(parent_id) == int and parent_id != "":
                try:
                    env['ca.ente_azienda'].browse(parent_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"L' ente azienda con id '{parent_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['parent_id'] = parent_id
            elif parent_id == "":
                vals['parent_id'] = parent_id
            # parent_path
            if 'parent_path' in data:
                vals['parent_path'] = parent_path
            # street
            if 'street' in data:
                vals['street'] = street
            # street2
            if 'street2' in data:
                vals['street2'] = street2
            # city
            if 'city' in data:
                vals['city'] = city
            # country_id
            if country_id and type(country_id) == str and country_id != "":
                country = env['res.country'].with_context(lang=env.user.lang).search([('name', '=', country_id)])
                if not country:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La provincia '{country_id}' inserita non esiste in odoo",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['country_id'] = country.id
            elif country_id and type(country_id) == int and country_id != "":
                try:
                    env['res.country'].browse(country_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La provincia con id '{country_id}' inserita non esiste in odoo",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['country_id'] = country_id
            elif country_id == "":
                vals['country_id'] = country_id
            # state_id
            if state_id and type(state_id) == str and state_id != "":
                state = env['res.country.state'].with_context(lang=env.user.lang).search([('name', '=', state_id)])
                if not state:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La città '{state_id}' inserita non esiste in odoo",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['state_id'] = state.id
            elif state_id and type(state_id) == int and state_id != "":
                try:
                    env['res.country.state'].browse(state_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La città con id '{state_id}' inserita non esiste in odoo",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['state_id'] = state_id
            elif country_id == "":
                vals['country_id'] = country_id
            # zip
            if 'zip' in data:
                vals['zip'] = zip
            # vat
            if 'vat' in data:
                vals['vat'] = vat
            # note
            if 'note' in data:
                vals['note'] = note
            # email
            if 'email' in data:
                vals['email'] = email
            # phone
            if 'phone' in data:
                vals['phone'] = phone
            # mobile
            if 'mobile' in data:
                vals['mobile'] = mobile
            # website
            if 'website' in data:
                vals['website'] = website
            # pec
            if pec:
                vals['pec'] = pec
            # company_id
            if company_id and type(company_id) == str and company_id != "":
                company = env['res.company'].search([('name', '=', company_id)])
                if not company:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La company '{company_id}' inserita non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['company_id'] = company.id
            elif company_id and type(company_id) == int and company_id != "":
                try:
                    env['res.company'].browse(company_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La company con id '{company_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['company_id'] = company_id
            elif company_id == "":
                vals['company_id'] = company_id
            # tipo_ente_azienda_id
            if tipo_ente_azienda_id and type(tipo_ente_azienda_id) == str and tipo_ente_azienda_id != "":
                tipo_ente_azienda = env['ca.tipo_ente_azienda'].search([('name', '=', tipo_ente_azienda_id)])
                if not tipo_ente_azienda:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo ente azienda '{tipo_ente_azienda_id}' inserito non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_ente_azienda_id'] = tipo_ente_azienda.id
            elif tipo_ente_azienda_id and type(tipo_ente_azienda_id) == int and tipo_ente_azienda_id != "":
                try:
                    env['ca.tipo_ente_azienda'].browse(tipo_ente_azienda_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo ente azienda con id '{tipo_ente_azienda_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_ente_azienda_id'] = tipo_ente_azienda_id
            elif tipo_ente_azienda_id == "":
                vals['tipo_ente_azienda_id'] = tipo_ente_azienda_id
            # ca_persona_ids
            ca_persona_vals = []
            if ca_persona_ids:
                for persona in ca_persona_ids:
                    if persona and type(persona) == str:
                        ca_persona = env['ca.persona'].search([('display_name', '=', persona)])
                        if not ca_persona:
                            return Response(json.dumps({
                                "header": {
                                    'response': 400
                                },
                                'body': {
                                    'message': f"La persona '{persona}' inserita non esiste",
                                }
                            }, ensure_ascii=False, indent=4), status=400)
                        ca_persona_vals.append(ca_persona.id)
                    elif persona and type(persona) == int:
                        ca_persona = env['ca.persona'].browse(persona)
                        if not ca_persona:
                            return Response(json.dumps({
                                "header": {
                                    'response': 400
                                },
                                'body': {
                                    'message': f"La persona con id '{persona}' non esiste",
                                }
                            }, ensure_ascii=False, indent=4), status=400)
                        ca_persona_vals.append(persona)
            if ca_persona_vals:
                vals['ca_persona_ids'] = ca_persona_vals
            # ref
            if ref:
                vals['ref'] = eval(ref)
            # lock
            if lock:
                vals['lock'] = eval(lock)
            # url_gateway_lettori
            if 'url_gateway_lettori' in data:
                vals['url_gateway_lettori'] = url_gateway_lettori
            # nome_chiave_header
            if 'nome_chiave_header' in data:
                vals['nome_chiave_header'] = nome_chiave_header
            # jwt
            if 'jwt' in data:
                vals['jwt'] = jwt
            ente_azienda_id.write(vals)
            ente_azienda_id = ente_azienda_id.with_context(lang=env.user.lang)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': ente_azienda_id.id,
                    'name': ente_azienda_id.name,
                    'parent_id': ente_azienda_id.parent_id.name if ente_azienda_id.parent_id else '',
                    'parent_path': ente_azienda_id.parent_path or '',
                    'street': ente_azienda_id.street or '',
                    'street2': ente_azienda_id.street2 or '',
                    'city': ente_azienda_id.city or '',
                    'state_id': ente_azienda_id.state_id.name if ente_azienda_id.state_id else '',
                    'zip': ente_azienda_id.zip or '',
                    'country_id': ente_azienda_id.country_id.name if ente_azienda_id.country_id else '',
                    'vat': ente_azienda_id.vat or '',
                    'note': ente_azienda_id.note or '',
                    'email': ente_azienda_id.email or '',
                    'phone': ente_azienda_id.phone or '',
                    'mobile': ente_azienda_id.mobile or '',
                    'website': ente_azienda_id.website or '',
                    'pec': ente_azienda_id.pec,
                    'company_id': ente_azienda_id.company_id.name if ente_azienda_id.company_id else '',
                    'tipo_ente_azienda_id': ente_azienda_id.tipo_ente_azienda_id.name,
                    'ca_persona_ids': ",".join(p.display_name for p in ente_azienda_id.ca_persona_ids),
                    'ref': ente_azienda_id.ref,
                    'lock': ente_azienda_id.lock,
                    'url_gateway_lettori': ente_azienda_id.url_gateway_lettori or '',
                    'nome_chiave_header': ente_azienda_id.nome_chiave_header or '',
                    'jwt': ente_azienda_id.jwt or '',
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)