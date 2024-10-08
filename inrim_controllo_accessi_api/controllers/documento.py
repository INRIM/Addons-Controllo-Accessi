from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiDocumento(http.Controller):

    @http.route('/api/documento', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_gest_documento(self):
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
            env['ca.documento'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.documento"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_documento_ids = env['ca.documento'].search([])
        for documento in ca_documento_ids:
            images = []
            for image in documento.image_ids:
                images.append({
                'id': image.id,
                'name': image.name,
                'description': image.description or "",
                'ca_tipo_documento_id': image.ca_tipo_documento_id.name,
                'side': dict(image._fields['side'].selection).get(image.side),
                'image': str(image.image),
                'filename': image.filename,
                'ca_documento_id': image.ca_documento_id.id })
            vals = {
                'id': documento.id,
                'ca_persona_id': documento.ca_persona_id.token,
                'tipo_documento_id': documento.tipo_documento_id.name,
                'validity_start_date': documento.validity_start_date.strftime("%Y-%m-%d"),
                'validity_end_date': documento.validity_end_date.strftime("%Y-%m-%d"),
                'image_ids': images,
                'issued_by': documento.issued_by,
                'document_code': documento.document_code,
                'ca_stato_documento_id': documento.ca_stato_documento_id.name
            }
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)

    @http.route('/api/documento', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_gest_documento(self):
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
                            'ca_persona_id': '6xERuNlgy3',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Comune',
                            'document_code': 'Codice Doc Persona 1',
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.documento'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.documento"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        ca_persona_id = data.get('ca_persona_id')
        tipo_documento_id = data.get('tipo_documento_id')
        validity_start_date = data.get('validity_start_date')
        validity_end_date = data.get('validity_end_date')
        issued_by = data.get('issued_by')
        document_code = data.get('document_code')
        if not id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'id'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': 'dUqwMV0tTL',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Carta D’identita',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not tipo_documento_id:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'tipo_documento_id'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': 'dUqwMV0tTL',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Carta D’identita',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not validity_start_date:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'validity_start_date'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': 'dUqwMV0tTL',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Carta D’identita',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not validity_end_date:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'validity_end_date'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': 'dUqwMV0tTL',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Carta D’identita',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not issued_by:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'issued_by'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': '6xERuNlgy3',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Carta D’identita',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        if not document_code:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                'body': {
                    'message': "Campo obbligatorio mancante 'document_code'",
                    'BodyHint': {
                        'id': 1,
                        'ca_persona_id': 'dUqwMV0tTL',
                        'tipo_documento_id': 'Carta D’identita',
                        'validity_start_date': '2024-01-01',
                        'validity_end_date': '2024-06-20',
                        'issued_by': 'Comune',
                        'document_code': 'Comune'
                    }
                }
            }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.documento'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {id} nel model ca.documento"
                }, ensure_ascii=False, indent=4), status=400)
        vals = {}
        try:
            documento = env[
                'ca.documento'
            ].browse(int(id))
            if type(tipo_documento_id) == str:
                tipo_documento = env['ca.tipo_doc_ident'].search([('name', '=', tipo_documento_id)])
                if not tipo_documento_id:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo di documento '{tipo_documento_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_documento_id'] = tipo_documento.id
            elif type(tipo_documento_id) == int:
                try:
                    env['ca.documento'].browse(tipo_documento_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo di documento con id '{tipo_documento_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['tipo_documento_id'] = tipo_documento_id  
            if type(ca_persona_id) == str:
                ca_persona = env['ca.persona'].search([('token', '=', ca_persona_id)])
                if not ca_persona:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La persona con token '{ca_persona_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['ca_persona_id'] = ca_persona.id
            elif type(ca_persona_id) == int:
                try:
                    env['ca.documento'].browse(ca_persona_id).display_name
                except Exception as e:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La persona con id '{ca_persona_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                vals['ca_persona_id'] = ca_persona_id  
            try:
                vals['validity_start_date'] = validity_start_date
                vals['validity_end_date'] = validity_end_date
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Errore: {e}"
                }, ensure_ascii=False, indent=4), status=400)
            vals['issued_by'] = issued_by
            vals['document_code'] = document_code
            if vals:
                documento.write(vals)
                documento._onchange_validity_end_date()
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': documento.id,
                    'ca_persona_id': documento.ca_persona_id.token,
                    'tipo_documento_id' : documento.tipo_documento_id.name,
                    'validity_start_date': documento.validity_start_date.strftime("%Y-%m-%d"),
                    'validity_end_date': documento.validity_end_date.strftime("%Y-%m-%d"),
                    'issued_by' : documento.issued_by,
                    'document_code' : documento.document_code,
                    'ca_stato_documento_id' : documento.ca_stato_documento_id.name
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
        

    @http.route('/api/documento', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_gest_documento(self):
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
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Comune',
                            'document_code': 'Codice Doc Persona 1',
                        }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.documento'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.documento"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        ca_persona_id = data.get('ca_persona_id')
        if type(ca_persona_id) == str:
                ca_persona = env['ca.persona'].search([('token', '=', ca_persona_id)])
                if not ca_persona:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"La persona con token '{ca_persona_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                ca_persona_id = ca_persona.id
        elif type(ca_persona_id) == int:
            try:
                ca_persona = env['ca.documento'].browse(ca_persona_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"La persona con id '{ca_persona_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
            ca_persona_id = ca_persona_id
        tipo_documento_id = data.get('tipo_documento_id')
        if type(tipo_documento_id) == str:
                tipo_documento = env['ca.tipo_doc_ident'].search([('name', '=', tipo_documento_id)])
                if not tipo_documento_id:
                    return Response(json.dumps({
                        "header": {
                            'response': 400
                        },
                        'body': {
                            'message': f"Il tipo di documento '{tipo_documento_id}' non esiste",
                        }
                    }, ensure_ascii=False, indent=4), status=400)
                tipo_documento_id = tipo_documento.id
        elif type(tipo_documento_id) == int:
            try:
                env['ca.tipo_doc_ident'].browse(tipo_documento_id).display_name
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': f"Il tipo di documento con id '{tipo_documento_id}' non esiste",
                    }
                }, ensure_ascii=False, indent=4), status=400)
        validity_start_date = data.get('validity_start_date')
        validity_end_date = data.get('validity_end_date')
        issued_by = data.get('issued_by')
        document_code = data.get('document_code')
        if not tipo_documento_id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'tipo_documento_id'",
                        'BodyHint': {
                            'id': 1,
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Carta D’identita',
                            'document_code': 'Comune'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not validity_start_date:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'validity_start_date'",
                        'BodyHint': {
                            'id': 1,
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Carta D’identita',
                            'document_code': 'Comune'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not validity_end_date:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'validity_end_date'",
                        'BodyHint': {
                            'id': 1,
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Carta D’identita',
                            'document_code': 'Comune'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not issued_by:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'issued_by'",
                        'BodyHint': {
                            'id': 1,
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Carta D’identita',
                            'document_code': 'Comune'
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not document_code:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'document_code'",
                        'BodyHint': {
                            'id': 1,
                            'ca_persona_id': 'dUqwMV0tTL',
                            'tipo_documento_id': 'Carta D’identita',
                            'validity_start_date': '2024-01-01',
                            'validity_end_date': '2024-06-20',
                            'issued_by': 'Comune',
                            'document_code': 'Comune',
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            vals = {
                'ca_persona_id': ca_persona_id,
                'tipo_documento_id': tipo_documento_id,
                'validity_start_date': validity_start_date,
                'validity_end_date': validity_end_date,
                'issued_by': issued_by,
                'document_code' : document_code
            }
            documento = env['ca.documento'].create(vals)
            documento._onchange_validity_end_date()
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': documento.id,
                    'ca_persona_id': documento.ca_persona_id.token,
                    'tipo_documento_id' : documento.tipo_documento_id.name,
                    'validity_start_date': documento.validity_start_date.strftime("%Y-%m-%d"),
                    'validity_end_date': documento.validity_end_date.strftime("%Y-%m-%d"),
                    'issued_by' : documento.issued_by,
                    'document_code' : documento.document_code,
                    'ca_stato_documento_id' : documento.ca_stato_documento_id.name
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