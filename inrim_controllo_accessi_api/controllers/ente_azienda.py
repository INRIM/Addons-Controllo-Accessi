from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiEnteAzienda(http.Controller):

    @http.route('/api/ente_azienda', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_ente_azienda(self):
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
                'ca_persona_ids': ",".join(p.token for p in ente_azienda.ca_persona_ids),
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
                        "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                        "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                        "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                        "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                    ca_persona = env['ca.persona'].search([('token', '=', persona)])
                    if not ca_persona:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': f"La persona con token '{persona}' inserita non esiste",
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
                    "ca_persona_ids": ",".join(p.token for p in ente_azienda_id.ca_persona_ids),
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
                            "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                        "ca_persona_ids": ["6xERuNlgy3", "hIdyCMmFFL"],
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
                        ca_persona = env['ca.persona'].search([('token', '=', persona)])
                        if not ca_persona:
                            return Response(json.dumps({
                                "header": {
                                    'response': 400
                                },
                                'body': {
                                    'message': f"La persona con token '{persona}' inserita non esiste",
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
                    'ca_persona_ids': ",".join(p.token for p in ente_azienda_id.ca_persona_ids),
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