from odoo import http, api, SUPERUSER_ID
from odoo.http import request, Response
from .auth import InrimApiController
from datetime import datetime
import pytz
import json

class InrimApiPersona(http.Controller):

    @http.route('/api/persona', auth="none", type='http', methods=['GET'],
           csrf=False)
    def api_get_ca_persona(self):
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
        res = []
        ca_persona_ids = env['ca.persona'].search([])
        for persona in ca_persona_ids:
            persona = persona.with_context(lang=env.user.lang)
            vals = {
                'id': persona.id,
                'name': persona.name,
                'lastname': persona.lastname,
                'parent_id': persona.parent_id.token or "",
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
                'fiscalcode': "",
                'freshman': "",
                'nationality': "",
                'birth_date': "",
                'birth_place': "",
                'istat_code': "",
                'ca_documento_ids': []
            }
            if env.user.has_group('inrim_controllo_accessi_base.ca_gdpr'):
                vals.update({
                    'fiscalcode': persona.fiscalcode,
                    'freshman': persona.freshman or "",
                    'nationality': persona.nationality.name or "",
                    'birth_date': persona.birth_date.strftime("%Y/%m/%d") if persona.birth_date else "",
                    'birth_place': persona.birth_place or "",
                    'istat_code': persona.istat_code or "",
                })
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