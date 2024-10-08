from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiImgDocumento(http.Controller):
    
    @http.route('/api/immagine', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_gest_immagine(self):
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
            env['ca.img_documento'].with_user(env.user).check_access_rights('read')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha accesso ai record di ca.img_documento"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        ca_image_ids = env['ca.img_documento'].search([])
        for image in ca_image_ids:
            vals = {
                'id': image.id,
                'name': image.name,
                'description': image.description or "",
                'ca_tipo_documento_id': image.ca_tipo_documento_id.name,
                'side': dict(image._fields['side'].selection).get(image.side),
                'image': str(image.image),
                'filename': image.filename,
                'ca_documento_id': image.ca_documento_id.id
            }
            res.append(vals)
        return Response(json.dumps({
            "header": {
                'response': 200
            },
            "body": res
        }, ensure_ascii=False, indent=4), status=200)

    @http.route('/api/immagine', auth="none", type='http', methods=['PUT'],
           csrf=False)
    def api_put_gest_immagine(self):
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
                            'ca_tipo_documento_id': 'Carta D’identita',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.img_documento'].with_user(env.user).check_access_rights('write')
        except Exception as e:
            return Response(json.dumps({
                    "header": {
                        'response': 401
                    },
                    'body': {
                        'permission': f"L'utente {user_id.name} non ha il permesso di modifiare i record di ca.img_documento"
                    }
                }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        description = data.get('description')
        ca_tipo_documento_id = data.get('ca_tipo_documento_id')
        side = data.get('side')
        image = data.get('image')
        try:
            image = eval(image)
        except Exception as e:
            pass
        filename = data.get('filename')
        ca_documento_id = data.get('ca_documento_id')
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
                            'ca_tipo_documento_id': 'Carta D’identita',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
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
                            'id': 1,
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'Carta D’identita',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not side:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'side'",
                        'BodyHint': {
                            'id': 1,
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'Carta D’identita',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not image:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'image'",
                        'BodyHint': {
                            'id': 1,
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'Carta D’identita',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            'ca_documento_id': 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.img_documento'].browse(int(id)).display_name
        except:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Non é stato trovato nessun record con id {id} nel model ca.img_documento"
                }, ensure_ascii=False, indent=4), status=400)
        vals = {}
        try:
            img_documento = env[
                'ca.img_documento'
            ].browse(int(id))
            if name:
                vals['name'] = name
            if description != False:
                vals['description'] = description
            if ca_tipo_documento_id:
                ca_tipo_documento_id = data.get('ca_tipo_documento_id')
                if type(ca_tipo_documento_id) == str:
                    tipo_documento_id = env['ca.tipo_doc_ident'].search([('name', '=', ca_tipo_documento_id)])
                    if not tipo_documento_id:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': f"Il tipo di documento '{ca_tipo_documento_id}' non esiste",
                            }
                        }, ensure_ascii=False, indent=4), status=400)
                    vals['ca_tipo_documento_id'] = tipo_documento_id.id
                elif ca_tipo_documento_id and type(ca_tipo_documento_id) == int and ca_tipo_documento_id != "":
                    try:
                        env['ca.img_documento'].browse(ca_tipo_documento_id).display_name
                    except Exception as e:
                        return Response(json.dumps({
                            "header": {
                                'response': 400
                            },
                            'body': {
                                'message': f"Il tipo di documento con id '{ca_tipo_documento_id}' non esiste",
                            }
                        }, ensure_ascii=False, indent=4), status=400)
                    vals['ca_tipo_documento_id'] = ca_tipo_documento_id
                elif ca_tipo_documento_id == "":
                    vals['ca_tipo_documento_id'] = False    
            if side != False:
                selection_items = dict(img_documento._fields['side'].selection)
                for key, value in selection_items.items():
                    if side == value:
                        vals['side'] = key
            if image != False:
                vals['image'] = image
            if filename != False:
                vals['filename'] = filename
            if ca_documento_id != False:
                vals['ca_documento_id'] = ca_documento_id
            if vals:
                img_documento.write(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'id': img_documento.id,
                    'name': img_documento.name,
                    'description' : img_documento.description,
                    'ca_tipo_documento_id' : img_documento.ca_tipo_documento_id.name,
                    'side' : dict(img_documento._fields['side'].selection).get(img_documento.side),
                    'image' : str(img_documento.image) or "",
                    'filename' : img_documento.filename or "",
                    'ca_documento_id' : img_documento.ca_documento_id.id
                }
            }, ensure_ascii=False, indent=4), status=200)
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 400
                },
                "body": f"Errore: {e}"
            }, ensure_ascii=False, indent=4), status=400)
    
    @http.route('/api/immagine', auth="none", type='http', methods=['POST'],
           csrf=False)
    def api_post_gest_immagine(self):
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
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'False',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            'ca_documento_id': 1
                        }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            env['ca.img_documento'].with_user(env.user).check_access_rights('create')
        except Exception as e:
            return Response(json.dumps({
                "header": {
                    'response': 401
                },
                'body': {
                    'permission': f"L'utente {user_id.name} non ha il permesso di creare i record di ca.img_documento"
                }
            }, ensure_ascii=False, indent=4), status=401)
        data = json.loads(byte_string.decode('utf-8'))
        name = data.get('name')
        description = data.get('description')
        ca_tipo_documento_id = data.get('ca_tipo_documento_id')
        if ca_tipo_documento_id:
            tipo_documento_id = env['ca.tipo_doc_ident'].search([('name', '=', ca_tipo_documento_id)])
            if not tipo_documento_id:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Il tipo documento '{ca_tipo_documento_id}' inserito non esiste"
                }, ensure_ascii=False, indent=4), status=400)
            ca_tipo_documento_id = tipo_documento_id.id
        side = data.get('side')
        if side:
            try:
                img_documento = env['ca.img_documento'].browse()
                selection_items = dict(img_documento._fields['side'].selection)
                for key, value in selection_items.items():
                    if side == value:
                        side = key
            except Exception as e:
                return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    "body": f"Errore: {e}"
                }, ensure_ascii=False, indent=4), status=400)
        image = data.get('image')
        filename = data.get('filename')
        ca_documento_id = data.get('ca_documento_id')
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
                            'ca_tipo_documento_id': 'False',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not side:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'side'",
                        'BodyHint': {
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'False',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            "ca_documento_id": 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not image:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'image'",
                        'BodyHint': {
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'False',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            'ca_documento_id': 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        if not ca_documento_id:
            return Response(json.dumps({
                    "header": {
                        'response': 400
                    },
                    'body': {
                        'message': "Campo obbligatorio mancante 'ca_documento_id'",
                        'BodyHint': {
                            'name': 'Name',
                            'description': 'Description',
                            'ca_tipo_documento_id': 'False',
                            'side': 'Fronte',
                            'image': "b'RnJvbnRlIDE='",
                            'filename': 'immagine.png',
                            'ca_documento_id': 1
                        }
                    }
                }, ensure_ascii=False, indent=4), status=400)
        try:
            image = eval(image)
        except Exception as e:
            pass
        try:
            vals = {
                'name': name,
                'description': description or '',
                'ca_tipo_documento_id': ca_tipo_documento_id,
                'side': side,
                'image': image,
                'filename' : filename,
                'ca_documento_id' : ca_documento_id
            }
            img_documento = env['ca.img_documento'].create(vals)
            return Response(json.dumps({
                "header": {
                    'response': 200
                },
                "body": {
                    'name': img_documento.name,
                    'description': img_documento.description,
                    'ca_tipo_documento_id' : img_documento.ca_tipo_documento_id.name,
                    'side' : dict(img_documento._fields['side'].selection).get(img_documento.side),
                    'image' : str(img_documento.image) or "",
                    'filename' : img_documento.filename or "",
                    'ca_documento_id' : img_documento.ca_documento_id.id
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