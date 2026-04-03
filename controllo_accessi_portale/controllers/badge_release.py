import datetime
import pytz
from pytz import UTC
from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound
from .common import check_access_permission


class PortalBadgeRelease(http.Controller):

    def _get_user_timezone(self, env):
        tz_name = env.user.tz or env.context.get('tz') or 'UTC'
        try:
            return pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            return UTC

    def _parse_portal_datetime(self, env, post, field_name):
        value = post.get(f'{field_name}_iso') or post.get(field_name)
        if not value:
            return None

        parsed = datetime.datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = self._get_user_timezone(env).localize(parsed)

        return parsed.astimezone(UTC).replace(tzinfo=None)

    def _get_badge_release_personas(self, env, domain=None):
        fields = [
            'id', 'display_name', 'name', 'lastname', 'fiscalcode', 'email',
            'mobile', 'is_internal', 'freshman', 'ca_ente_azienda_ids',
            'current_tag', 'present',
        ]
        personas = env['ca.persona'].search_read(domain or [], fields=fields)
        current_tag_ids = [
            persona['current_tag'][0]
            for persona in personas
            if persona.get('current_tag')
        ]
        current_tag_map = {}
        if current_tag_ids:
            current_tag_map = {
                tag['id']: tag['temp']
                for tag in env['ca.tag_persona'].search_read(
                    [('id', 'in', current_tag_ids)],
                    ['temp'],
                )
            }
        for persona in personas:
            current_tag = persona.get('current_tag')
            persona['current_tag_temp'] = (
                current_tag_map.get(current_tag[0]) if current_tag else None
            )
        return personas

    def _get_existing_persona(self, env, vals):
        if not vals.get('persona_id'):
            return env['ca.persona']
        return env['ca.persona'].browse(vals['persona_id']).exists()

    def _populate_company_vals_from_persona(self, vals, persona):
        if not persona:
            return vals
        ente = persona.ca_ente_azienda_ids[:1]
        if not ente:
            return vals
        if not vals.get('ente_azienda'):
            vals['ente_azienda'] = ente.id
        if not vals.get('ca_ente_name'):
            vals['ca_ente_name'] = ente.name
        if not vals.get('tipo_ente_azienda_id'):
            vals['tipo_ente_azienda_id'] = ente.tipo_ente_azienda_id.id
        if not vals.get('vat'):
            vals['vat'] = ente.vat
        return vals

    def _get_badge_release_required_fields(self, persona):
        req_fields = [
            "lastname", "name", "fiscalcode", "ca_ente_name",
            "ca_work_info_type_id", "ca_title_id", "date_start",
            "date_end", "ca_tag_id",
        ]
        if not persona:
            req_fields.insert(3, "tipo_ente_azienda_id")
        if not (persona and persona.is_internal):
            req_fields.extend(["ref_domain", "parent_id"])
        return req_fields
    
    @http.route('/badge_release', auth='user', type='http', website=True)
    def badge_release_form(self, **post):
        user = request.env.user
        if not check_access_permission(user):
            raise NotFound()

        if post and request.httprequest.method == 'POST':
            return self._handle_badge_release_post(post)

        vals = {k: v for k, v in post.items()} if post else {}

        return request.render('controllo_accessi_portale.badge_release_view', {
            "errors": {}, "error_message": "", "values": vals
        })

    @http.route('/badge_release/submit', auth='user', type='http', website=True, methods=['POST'], csrf=False)
    def badge_release_submit(self, **kwargs):
        return self._handle_badge_release_post(kwargs)

    def _handle_badge_release_post(self, post):
        vals = {
            'vat': post['vat'], 'ca_ente_name': post['ca_ente_name'], 'fiscalcode': post['fiscalcode'],
            'lastname': post['lastname'], 'name': post['name'], 'freshman': post['freshman'],
            'email': post['email'], 'mobile': post['mobile'], 'ref_domain': post.get('ref_domain'),
        }

        date_start = self._parse_portal_datetime(request.env, post, 'date_start')
        date_end = self._parse_portal_datetime(request.env, post, 'date_end')
        if date_start:
            vals['date_start'] = date_start
        if date_end:
            vals['date_end'] = date_end

        for key in ['persona_id', 'tipo_ente_azienda_id', 'azienda', 'ca_work_info_type_id', 'ca_title_id', 'ca_tag_id', 'parent_id']:
            if post.get(key) and post[key] != "":
                clean_key = 'ente_azienda' if key == 'azienda' else key
                vals[clean_key] = int(post[key])

        persona = self._get_existing_persona(request.env, vals)
        vals = self._populate_company_vals_from_persona(vals, persona)
        req_fields = self._get_badge_release_required_fields(persona)

        errors = {
            field_name: 'missing'
            for field_name in req_fields
            if not vals.get(field_name)
        }
        if errors:
            return request.render('controllo_accessi_portale.badge_release_view', {
                "errors": errors, "error_message": _('Some required fields are empty.'), "values": post
            })

        add_doc = not vals.get("persona_id")
        wiz = request.env['ca.registra_persona'].with_context(no_compute_tag_id_number=True).create(vals)
        wiz.action_confirm()
        if add_doc:
            return request.redirect(f"/badge_release_docs/{wiz.persona_id.id}")
        return request.redirect('/anagrafiche')

    @http.route('/get/badge_release/init_data', auth='user', type='json', website=True)
    def get_badge_release_init_data(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise Forbidden()
        
        Env = request.env
        
        tags = Env['ca.tag'].search_read(
            [('in_use', '=', False), ('revoked', '=', False)],
            fields=['id', 'name', 'display_name', 'tag_code', 'temp', 'ca_proprieta_tag_ids']
        )

        tag_domains = {
            'visitor': [Env.ref('inrim_anagrafiche.proprieta_tag_visitatore').id, Env.ref('inrim_anagrafiche.proprieta_tag_servizio').id],
            'internal': [Env.ref('inrim_anagrafiche.proprieta_tag_jolly').id, Env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id],
            'temp': [Env.ref('inrim_anagrafiche.proprieta_tag_jolly').id]
        }
        
        work_infos = Env['ca.work_info'].search_read(
            [('state', '=', 'active')],
            fields=['ca_persona_id', 'date_start', 'date_end', 'ca_work_info_type_id', 'ca_title_id']
        )

        ids_hidden = [
            Env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            Env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
        ]
        
        tipo_enti_hidden = Env['ca.tipo_ente_azienda'].search_read([('id', 'in', ids_hidden)], ['id', 'display_name'])
        
        tipo_enti = Env['ca.tipo_ente_azienda'].search_read(
            [('id', 'not in', ids_hidden)], 
            ['id', 'name', 'display_name']
        )

        return {
            'tags': tags,
            'tag_domains': tag_domains,
            'work_infos': work_infos,
            'titoli': Env['ca.titolo_persona'].search_read([], ['id', 'name', 'display_name', 'structured']),
            'work_info_types': Env['ca.work_info_type'].search_read([], ['id', 'name', 'display_name']),
            'enti_aziende': Env['ca.ente_azienda'].search_read([], ['id', 'name', 'display_name', 'vat', 'tipo_ente_azienda_id']),
            'tipo_enti_hidden_ids': [t['id'] for t in tipo_enti_hidden],
            'tipo_enti': tipo_enti,
            'persona_parent': Env['ca.persona'].search_read([('is_internal', '=', True)], ['id', 'display_name', 'present'])
        }

    @http.route('/get/badge_release/ca_persona', auth='user', type='json', website=True)
    def badge_release_ca_persona(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise Forbidden()
        return self._get_badge_release_personas(request.env)
