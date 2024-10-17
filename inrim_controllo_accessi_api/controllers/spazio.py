from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiSpazio(http.Controller):

    @http.route('/api/spazio', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_spazio(self):
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
            env['ca.spazio'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.spazio"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_spazio_ids = env['ca.spazio'].search([])
        for spazio in ca_spazio_ids:
            vals = {
                'id': spazio.id,
                'name': spazio.name,
                'tipo_spazio_id': spazio.tipo_spazio_id.display_name,
                'ente_azienda_id': spazio.ente_azienda_id.display_name,
                'codice_locale_id': spazio.codice_locale_id.display_name or "",
                'lettore_id': spazio.lettore_id.display_name or "",
                'date_start': spazio.date_start.strftime('%Y-%m-%d') if spazio.date_start else "",
                'date_end': spazio.date_end.strftime('%Y-%m-%d') if spazio.date_end else "",
                'righe_persona_ids': []
            }
            for righe in spazio.righe_persona_ids:
                vals['righe_persona_ids'].append({
                    'id': righe.id,
                    'spazio_id': righe.spazio_id.display_name or "",
                    'tag_persona_id': righe.tag_persona_id.token or "",
                    'date_start': righe.date_start.strftime('%Y-%m-%d') if righe.date_start else "",
                    'date_end': righe.date_end.strftime('%Y-%m-%d') if righe.date_end else "",
                    'suspended': righe.suspended
                })
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)
    
    @http.route('/api/spazio', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_ca_spazio(self):
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
                            
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.spazio'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.spazio"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        tipo_spazio_id = data.get('tipo_spazio_id')
        ente_azienda_id = data.get('ente_azienda_id')
        codice_locale_id = data.get('codice_locale_id')
        lettore_id = data.get('lettore_id')
        date_start = data.get('date_start')
        date_end = data.get('date_end')
        righe_persona_ids = data.get('righe_persona_ids')
        if not id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'id'",
                    'BodyHint': {
                        "id": 1,
                        "name": "1",
                        "tipo_spazio_id": "Piano",
                        "ente_azienda_id": "Sede 1",
                        "codice_locale_id": "Test",
                        "lettore_id": "Lettore 1",
                        "date_start": "2024-07-01",
                        "date_end": "2024-07-31",
                        "righe_persona_ids": [
                            {
                                "id": 1,
                                "spazio_id": "1",
                                "tag_persona_id": "tgmshiCNlY",
                                "date_start": "2024-08-01",
                                "date_end": "2024-08-31",
                                "suspended": False
                            }
                        ]
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.spazio'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {id} nel model ca.spazio"
                }, ensure_ascii=False, indent=4), status=400)
        vals = {}
        try:
            spazio_id = env['ca.spazio'].browse(int(id))
            # name
            if name:
                vals['name'] = name
            # tipo_spazio_id
            if tipo_spazio_id and type(tipo_spazio_id) == str:
                tipo_spazio = env['ca.tipo_spazio'].search([('name', '=', tipo_spazio_id)])
                if not tipo_spazio:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo spazio '{tipo_spazio_id}' inserito non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_spazio_id'] = tipo_spazio.id
            elif tipo_spazio_id and type(tipo_spazio_id) == int:
                try:
                    env['ca.spazio'].browse(tipo_spazio_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo spazio con id '{tipo_spazio_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_spazio_id'] = tipo_spazio_id
            # ente_azienda_id
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
                vals['ente_azienda_id'] = ente_azienda.id
            elif ente_azienda_id and type(ente_azienda_id) == int:
                try:
                    env['ca.ente_azienda'].browse(ente_azienda_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"L'ente azienda con id '{ente_azienda_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['ente_azienda_id'] = ente_azienda_id
            # codice_locale_id
            if codice_locale_id and type(codice_locale_id) == str and codice_locale_id != "":
                codice_locale = env['ca.codice_locale'].search([('name', '=', codice_locale_id)])
                if not codice_locale:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il codice locale '{codice_locale_id}' inserito non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['codice_locale_id'] = codice_locale.id
            elif codice_locale_id and type(codice_locale_id) == int and codice_locale_id != "":
                try:
                    env['ca.codice_locale'].browse(codice_locale_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il codice locale con id '{codice_locale_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['codice_locale_id'] = codice_locale_id
            elif codice_locale_id == "":
                vals['codice_locale_id'] = False
            # lettore_id
            if lettore_id and type(lettore_id) == str and lettore_id != "":
                lettore = env['ca.lettore'].search([('name', '=', lettore_id)])
                if not lettore:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il lettore '{lettore_id}' inserito non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['lettore_id'] = lettore.id
            elif lettore_id and type(lettore_id) == int and lettore_id != "":
                try:
                    env['ca.lettore'].browse(lettore_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il lettore con id '{lettore_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['lettore_id'] = lettore_id
            elif lettore_id == "":
                vals['lettore_id'] = False
            if 'date_start' in data:
                vals['date_start'] = date_start
            if 'date_end' in data:
                vals['date_end'] = date_end
            if righe_persona_ids:
                for righe in righe_persona_ids:
                    righe_vals = {}
                    righe_id = righe.get('id')
                    if not righe_id:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': "Campo obbligatorio mancante 'id' in 'righe_persona_ids'",
                                'BodyHint': {
                                    "id": 1,
                                    "name": "1",
                                    "tipo_spazio_id": "Piano",
                                    "ente_azienda_id": "Sede 1",
                                    "codice_locale_id": "Test",
                                    "lettore_id": "Lettore 1",
                                    "date_start": "2024-07-01",
                                    "date_end": "2024-07-31",
                                    "righe_persona_ids": [
                                        {
                                            "id": 1,
                                            "spazio_id": "1",
                                            "tag_persona_id": "tgmshiCNlY",
                                            "date_start": "2024-08-01",
                                            "date_end": "2024-08-31",
                                            "suspended": False
                                        }
                                    ]
                                }
                            }
                        }, ensure_ascii=False, indent=4), status=400)
                    try:
                        env['ca.righe_persona'].browse(righe_id).suspended
                    except Exception as e:
                        return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il record con id '{righe_id}' di ca.righe_persona non esiste",
                            'BodyHint': {
                                "id": 1,
                                "name": "1",
                                "tipo_spazio_id": "Piano",
                                "ente_azienda_id": "Sede 1",
                                "codice_locale_id": "Test",
                                "lettore_id": "Lettore 1",
                                "date_start": "2024-07-01",
                                "date_end": "2024-07-31",
                                "righe_persona_ids": [
                                    {
                                        "id": 1,
                                        "spazio_id": "1",
                                        "tag_persona_id": "tgmshiCNlY",
                                        "date_start": "2024-08-01",
                                        "date_end": "2024-08-31",
                                        "suspended": False
                                    }
                                ]
                            }
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                    if righe_id in spazio_id.righe_persona_ids.ids:
                        righe_persona_id = env['ca.righe_persona'].browse(righe_id)
                        if 'date_start' in righe:
                            righe_vals['date_start'] = righe.get('date_start')
                        if 'date_end' in righe:
                            righe_vals['date_end'] = righe.get('date_end')
                        if 'suspended' in righe:
                            righe_vals['suspended'] = eval(righe.get('suspended'))
                        if 'tag_persona_id' in righe:
                            tag_persona_id = righe.get('tag_persona_id')
                            if tag_persona_id and type(tag_persona_id) == str and tag_persona_id != "":
                                tag_persona = env['ca.tag_persona'].search([('token', '=', tag_persona_id)])
                                if not tag_persona:
                                    return Response(json.dumps({
                                        "header": {
                                            'response': 400
                                        },
                                        'body': {
                                            'message': f"Il tag persona con token '{tag_persona_id}' non esiste",
                                            'BodyHint': {
                                                "id": 1,
                                                "name": "1",
                                                "tipo_spazio_id": "Piano",
                                                "ente_azienda_id": "Sede 1",
                                                "codice_locale_id": "Test",
                                                "lettore_id": "Lettore 1",
                                                "date_start": "2024-07-01",
                                                "date_end": "2024-07-31",
                                                "righe_persona_ids": [
                                                    {
                                                        "id": 1,
                                                        "spazio_id": "1",
                                                        "tag_persona_id": "tgmshiCNlY",
                                                        "date_start": "2024-08-01",
                                                        "date_end": "2024-08-31",
                                                        "suspended": False
                                                    }
                                                ]
                                            }
                                        }
                                    }, ensure_ascii=False, indent=4), status=400)
                                righe_vals['tag_persona_id'] = tag_persona.id
                            elif tag_persona_id and type(tag_persona_id) == int and tag_persona_id != "":
                                try:
                                    env['ca.tag_persona'].browse(tag_persona_id).token
                                except Exception as e:
                                    return Response(json.dumps({
                                        "header": {
                                            'response': 400
                                        },
                                        'body': {
                                            'message': f"Il tag persona con id '{tag_persona_id}' inserito non esiste",
                                            'BodyHint': {
                                                "name": "1",
                                                "tipo_spazio_id": "Piano",
                                                "ente_azienda_id": "Sede 1",
                                                "codice_locale_id": "Test",
                                                "lettore_id": "Lettore 1",
                                                "date_start": "2024-07-01",
                                                "date_end": "2024-07-31",
                                                "righe_persona_ids": [
                                                    {
                                                        "spazio_id": "1",
                                                        "tag_persona_id": "tgmshiCNlY",
                                                        "date_start": "2024-08-01",
                                                        "date_end": "2024-08-31",
                                                        "suspended": False
                                                    }
                                                ]
                                            }
                                        }
                                    }, ensure_ascii=False, indent=4), status=400)
                                righe_vals['tag_persona_id'] = tag_persona_id
                            elif tag_persona_id == "":
                                righe_vals['tag_persona_id'] = False
                        if righe_vals:
                            righe_persona_id.write(righe_vals)
            if vals:
                spazio_id.write(vals)
            body = {
                'id': spazio_id.id,
                'name': spazio_id.name,
                'tipo_spazio_id': spazio_id.tipo_spazio_id.display_name,
                'ente_azienda_id': spazio_id.ente_azienda_id.display_name,
                'codice_locale_id': spazio_id.codice_locale_id.display_name or "",
                'lettore_id': spazio_id.lettore_id.display_name or "",
                'date_start': spazio_id.date_start.strftime('%Y-%m-%d') if spazio_id.date_start else "",
                'date_end': spazio_id.date_end.strftime('%Y-%m-%d') if spazio_id.date_end else "",
                'righe_persona_ids': []
            }
            for righe in spazio_id.righe_persona_ids:
                body['righe_persona_ids'].append({
                    'spazio_id': righe.spazio_id.display_name or "",
                    'tag_persona_id': righe.tag_persona_id.token or "",
                    'date_start': righe.date_start.strftime('%Y-%m-%d') if righe.date_start else "",
                    'date_end': righe.date_end.strftime('%Y-%m-%d') if righe.date_end else "",
                    'suspended': righe.suspended
                })
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": body
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        
    @http.route('/api/spazio', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_ca_spazio(self):
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
                        "name": "1",
                        "tipo_spazio_id": "Piano",
                        "ente_azienda_id": "Sede 1",
                        "codice_locale_id": "Test",
                        "lettore_id": "Lettore 1",
                        "date_start": "2024-07-01",
                        "date_end": "2024-07-31",
                        "righe_persona_ids": [
                            {
                                "spazio_id": "1",
                                "tag_persona_id": "tgmshiCNlY",
                                "date_start": "2024-08-01",
                                "date_end": "2024-08-31",
                                "suspended": False
                            }
                        ]
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.spazio'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.spazio"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        name = data.get('name')
        tipo_spazio_id = data.get('tipo_spazio_id')
        ente_azienda_id = data.get('ente_azienda_id')
        if not name:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'name'",
                    'BodyHint': {
                        "name": "1",
                        "tipo_spazio_id": "Piano",
                        "ente_azienda_id": "Sede 1",
                        "codice_locale_id": "Test",
                        "lettore_id": "Lettore 1",
                        "date_start": "2024-07-01",
                        "date_end": "2024-07-31",
                        "righe_persona_ids": [
                            {
                                "spazio_id": "1",
                                "tag_persona_id": "tgmshiCNlY",
                                "date_start": "2024-08-01",
                                "date_end": "2024-08-31",
                                "suspended": False
                            }
                        ]
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not tipo_spazio_id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'tipo_spazio_id'",
                    'BodyHint': {
                        "name": "1",
                        "tipo_spazio_id": "Piano",
                        "ente_azienda_id": "Sede 1",
                        "codice_locale_id": "Test",
                        "lettore_id": "Lettore 1",
                        "date_start": "2024-07-01",
                        "date_end": "2024-07-31",
                        "righe_persona_ids": [
                            {
                                "spazio_id": "1",
                                "tag_persona_id": "tgmshiCNlY",
                                "date_start": "2024-08-01",
                                "date_end": "2024-08-31",
                                "suspended": False
                            }
                        ]
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not ente_azienda_id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'ente_azienda_id'",
                    'BodyHint': {
                        "name": "1",
                        "tipo_spazio_id": "Piano",
                        "ente_azienda_id": "Sede 1",
                        "codice_locale_id": "Test",
                        "lettore_id": "Lettore 1",
                        "date_start": "2024-07-01",
                        "date_end": "2024-07-31",
                        "righe_persona_ids": [
                            {
                                "spazio_id": "1",
                                "tag_persona_id": "tgmshiCNlY",
                                "date_start": "2024-08-01",
                                "date_end": "2024-08-31",
                                "suspended": False
                            }
                        ]
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if tipo_spazio_id and type(tipo_spazio_id) == str:
            tipo_spazio = env['ca.tipo_spazio'].search([('name', '=', tipo_spazio_id)])
            if not tipo_spazio:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il tipo spazio '{tipo_spazio_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            tipo_spazio_id = tipo_spazio.id
        elif tipo_spazio_id and type(tipo_spazio_id) == int:
            try:
                env['ca.tipo_spazio'].browse(tipo_spazio_id).name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il tipo spazio con id '{tipo_spazio_id}' inserito non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if ente_azienda_id and type(ente_azienda_id) == str:
            ente_azienda = env['ca.ente_azienda'].search([('name', '=', ente_azienda_id)])
            if not ente_azienda_id:
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
                env['ca.ente_azienda'].browse(ente_azienda_id).name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"L'ente azienda con id '{ente_azienda_id}' inserita non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            vals = {
                "name": name,
                "tipo_spazio_id": tipo_spazio_id,
                "ente_azienda_id": ente_azienda_id,
            }
            if 'date_start' in data:
                vals['date_start'] = data.get('date_start')
            if 'date_end' in data:
                vals['date_end'] = data.get('date_end')
            codice_locale_id = data.get('codice_locale_id')
            if codice_locale_id and type(codice_locale_id) == str and codice_locale_id != "":
                codice_locale = env['ca.codice_locale'].search([('name', '=', codice_locale_id)])
                if not codice_locale:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il codice locale '{codice_locale_id}' inserito non esiste",
                            'BodyHint': {
                                "name": "1",
                                "tipo_spazio_id": "Piano",
                                "ente_azienda_id": "Sede 1",
                                "codice_locale_id": "Test",
                                "lettore_id": "Lettore 1",
                                "date_start": "2024-07-01",
                                "date_end": "2024-07-31",
                                "righe_persona_ids": [
                                    {
                                        "spazio_id": "1",
                                        "tag_persona_id": "tgmshiCNlY",
                                        "date_start": "2024-08-01",
                                        "date_end": "2024-08-31",
                                        "suspended": False
                                    }
                                ]
                            }
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['codice_locale_id'] = codice_locale.id
            elif codice_locale_id and type(codice_locale_id) == int and codice_locale_id != "":
                try:
                    env['ca.codice_locale'].browse(codice_locale_id).name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il codice locale con id '{codice_locale_id}' inserito non esiste",
                            'BodyHint': {
                                "name": "1",
                                "tipo_spazio_id": "Piano",
                                "ente_azienda_id": "Sede 1",
                                "codice_locale_id": "Test",
                                "lettore_id": "Lettore 1",
                                "date_start": "2024-07-01",
                                "date_end": "2024-07-31",
                                "righe_persona_ids": [
                                    {
                                        "spazio_id": "1",
                                        "tag_persona_id": "tgmshiCNlY",
                                        "date_start": "2024-08-01",
                                        "date_end": "2024-08-31",
                                        "suspended": False
                                    }
                                ]
                            }
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['codice_locale_id'] = codice_locale_id
            elif codice_locale_id == "":
                vals['codice_locale_id'] = False
            lettore_id = data.get('lettore_id')
            if lettore_id and type(lettore_id) == str and lettore_id != "":
                lettore = env['ca.lettore'].search([('name', '=', lettore_id)])
                if not lettore:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il lettore '{lettore_id}' inserito non esiste",
                            'BodyHint': {
                                "name": "1",
                                "tipo_spazio_id": "Piano",
                                "ente_azienda_id": "Sede 1",
                                "codice_locale_id": "Test",
                                "lettore_id": "Lettore 1",
                                "date_start": "2024-07-01",
                                "date_end": "2024-07-31",
                                "righe_persona_ids": [
                                    {
                                        "spazio_id": "1",
                                        "tag_persona_id": "tgmshiCNlY",
                                        "date_start": "2024-08-01",
                                        "date_end": "2024-08-31",
                                        "suspended": False
                                    }
                                ]
                            }
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['lettore_id'] = lettore.id
            elif lettore_id and type(lettore_id) == int and lettore_id != "":
                try:
                    env['ca.lettore'].browse(lettore_id).name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il lettore con id '{lettore_id}' inserito non esiste",
                            'BodyHint': {
                                "name": "1",
                                "tipo_spazio_id": "Piano",
                                "ente_azienda_id": "Sede 1",
                                "codice_locale_id": "Test",
                                "lettore_id": "Lettore 1",
                                "date_start": "2024-07-01",
                                "date_end": "2024-07-31",
                                "righe_persona_ids": [
                                    {
                                        "spazio_id": "1",
                                        "tag_persona_id": "tgmshiCNlY",
                                        "date_start": "2024-08-01",
                                        "date_end": "2024-08-31",
                                        "suspended": False
                                    }
                                ]
                            }
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['lettore_id'] = lettore_id
            elif lettore_id == "":
                vals['lettore_id'] = False
            righe_persona_ids = data.get('righe_persona_ids')
            righe_list = []
            if righe_persona_ids:
                for righe in righe_persona_ids:
                    righe_vals = {}
                    tag_persona_id = righe.get('tag_persona_id')
                    if tag_persona_id and type(tag_persona_id) == str:
                        tag_persona = env['ca.tag_persona'].search([
                            ('token', '=', tag_persona_id)
                        ])
                        if not tag_persona:
                            return Response(json.dumps({
                                "header": {
                                    'response': 400
                                },
                                'body': {
                                    'message': f"Il tag persona con token '{tag_persona_id}' inserito non esiste",
                                    'BodyHint': {
                                        "name": "1",
                                        "tipo_spazio_id": "Piano",
                                        "ente_azienda_id": "Sede 1",
                                        "codice_locale_id": "Test",
                                        "lettore_id": "Lettore 1",
                                        "date_start": "2024-07-01",
                                        "date_end": "2024-07-31",
                                        "righe_persona_ids": [
                                            {
                                                "spazio_id": "1",
                                                "tag_persona_id": "tgmshiCNlY",
                                                "date_start": "2024-08-01",
                                                "date_end": "2024-08-31",
                                                "suspended": False
                                            }
                                        ]
                                    }
                                }
                            }, ensure_ascii=False, indent=4), status=400)
                        righe_vals['tag_persona_id'] = tag_persona.id
                    elif tag_persona_id and type(tag_persona_id) == int:
                        try:
                            env['ca.tag_persona'].browse(tag_persona_id).temp
                        except Exception as e:
                            return Response(json.dumps({
                                "header": {
                                    'response': 400
                                },
                                'body': {
                                    'message': f"Il tag persona con id '{tag_persona_id}' inserito non esiste",
                                    'BodyHint': {
                                        "name": "1",
                                        "tipo_spazio_id": "Piano",
                                        "ente_azienda_id": "Sede 1",
                                        "codice_locale_id": "Test",
                                        "lettore_id": "Lettore 1",
                                        "date_start": "2024-07-01",
                                        "date_end": "2024-07-31",
                                        "righe_persona_ids": [
                                            {
                                                "spazio_id": "1",
                                                "tag_persona_id": "tgmshiCNlY",
                                                "date_start": "2024-08-01",
                                                "date_end": "2024-08-31",
                                                "suspended": False
                                            }
                                        ]
                                    }
                                }
                            }, ensure_ascii=False, indent=4), status=400)
                        righe_vals['tag_persona_id'] = tag_persona_id
                    if 'date_start' in righe:
                        righe_vals['date_start'] = righe.get('date_start')
                    if 'date_end' in righe:
                        righe_vals['date_end'] = righe.get('date_end')
                    if 'suspended' in righe:
                        righe_vals['suspended'] = eval(righe.get('suspended'))
                    righe_list.append((0,0,righe_vals))
            if righe_list:
                vals['righe_persona_ids'] = righe_list
            spazio_id = env['ca.spazio'].create(vals)
            righe_ids = []
            for righe in spazio_id.righe_persona_ids:
                righe_ids.append({
                    "id": righe.id,
                    "tag_persona_id": righe.tag_persona_id.token or "",
                    "date_start": righe.date_start.strftime("%Y-%m-%d") if righe.date_start else "",
                    "date_end": righe.date_end.strftime("%Y-%m-%d") if righe.date_end else "",
                    "suspended": righe.suspended
                })
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    "id": spazio_id.id,
                    "name": spazio_id.name,
                    "tipo_spazio_id": spazio_id.tipo_spazio_id.name,
                    "ente_azienda_id": spazio_id.ente_azienda_id.name,
                    "codice_locale_id":spazio_id.codice_locale_id.name or "",
                    "lettore_id": spazio_id.lettore_id.name or "",
                    "date_start": spazio_id.date_start.strftime("%Y-%m-%d") if spazio_id.date_start else "",
                    "date_end": spazio_id.date_end.strftime("%Y-%m-%d") if spazio_id.date_end else "",
                    "righe_persona_ids": righe_ids
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
        
    @http.route('/api/spazio', auth="none", type='http', methods=['DELETE'],
           csrf=False)
    def api_delete_ca_spazio(self):
        env = api.Environment(request.cr, SUPERUSER_ID,
                                {'active_test': False})
        
        if 'token' in request.httprequest.headers and request.httprequest.headers.get('active_test') == 'True':
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
            env['ca.spazio'].with_user(env.user).check_access_rights('unlink')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di cancellare i record di ca.spazio"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        try:
            ca_spazio_id = env['ca.spazio'].browse(int(id))
            if ca_spazio_id:
                vals = {
                    'id': ca_spazio_id.id,
                    'name': ca_spazio_id.name,
                    'tipo_spazio_id': ca_spazio_id.tipo_spazio_id.display_name,
                    'ente_azienda_id': ca_spazio_id.ente_azienda_id.display_name,
                    'codice_locale_id': ca_spazio_id.codice_locale_id.display_name or "",
                    'lettore_id': ca_spazio_id.lettore_id.display_name or "",
                    'date_start': ca_spazio_id.date_start.strftime('%Y-%m-%d') if ca_spazio_id.date_start else "",
                    'date_end': ca_spazio_id.date_end.strftime('%Y-%m-%d') if ca_spazio_id.date_end else "",
                    'righe_persona_ids': []
                }
                ca_spazio_id.unlink()
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