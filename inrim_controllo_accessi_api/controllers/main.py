from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from datetime import datetime
from ast import literal_eval
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
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.persona"
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
                'birth_date': persona.birth_date.strftime("%Y/%m/%d") if persona.birth_date else "",
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
                    'validity_start_date': doc.validity_start_date.strftime("%Y/%m/%d") if doc.validity_start_date else "",
                    'validity_end_date': doc.validity_end_date.strftime("%Y/%m/%d") if doc.validity_end_date else "",
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
                            'persona_id': 1,
                            'ente_azienda_id': 2,
                            'punto_accesso_id': 3,
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
                            'persona_id': 1,
                            'ente_azienda_id': 2,
                            'punto_accesso_id': 3,
                            'datetime_event': '2024-12-31 00:00:00'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.persona'].browse(int(persona_id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {persona_id} nel model ca.persona"
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.ente_azienda'].browse(int(ente_azienda_id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {ente_azienda_id} nel model ca.ente_azienda"
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.punto_accesso'].browse(int(punto_accesso_id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {punto_accesso_id} nel model ca.punto_accesso"
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
                'persona_id': richiesta_riga_accesso_sede_id.persona_id.id,
                'ente_azienda_id': richiesta_riga_accesso_sede_id.ente_azienda_id.id,
                'punto_accesso_id': richiesta_riga_accesso_sede_id.punto_accesso_id.id,
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
                            'persona_id': 2,
                            'ente_azienda_id': 3,
                            'punto_accesso_id': 4,
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
        if persona_id:
            try:
                env['ca.persona'].browse(int(persona_id)).display_name
            except:
                return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        "body": f"Non é stato trovato nessun record con id {persona_id} nel model ca.persona"
                    }, ensure_ascii=False, indent=4), status=400)
        if ente_azienda_id:
            try:
                env['ca.ente_azienda'].browse(int(ente_azienda_id)).display_name
            except:
                return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        "body": f"Non é stato trovato nessun record con id {ente_azienda_id} nel model ca.ente_azienda"
                    }, ensure_ascii=False, indent=4), status=400)
        if punto_accesso_id:
            try:
                env['ca.punto_accesso'].browse(int(punto_accesso_id)).display_name
            except:
                return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        "body": f"Non é stato trovato nessun record con id {punto_accesso_id} nel model ca.punto_accesso"
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
                    'persona_id': richiesta_riga_accesso_sede_id.persona_id.id,
                    'ente_azienda_id': richiesta_riga_accesso_sede_id.ente_azienda_id.id,
                    'punto_accesso_id': richiesta_riga_accesso_sede_id.punto_accesso_id.id,
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
                vals['is_internal'] = literal_eval(is_internal)
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