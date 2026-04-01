import datetime
from pytz import UTC
from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound
from .common import check_access_permission


class PortalBadgeRelease(http.Controller):
    
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
        
        if post.get('date_start'):
            vals['date_start'] = datetime.datetime.fromisoformat(post['date_start']).astimezone(UTC).replace(tzinfo=None)
        if post.get('date_end'):
            vals['date_end'] = datetime.datetime.fromisoformat(post['date_end']).astimezone(UTC).replace(tzinfo=None)

        for key in ['persona_id', 'tipo_ente_azienda_id', 'azienda', 'ca_work_info_type_id', 'ca_title_id', 'ca_tag_id', 'parent_id']:
            if post.get(key) and post[key] != "":
                clean_key = 'ente_azienda' if key == 'azienda' else key
                vals[clean_key] = int(post[key])

        REQ_FIELDS = ["lastname", "name", "fiscalcode", "tipo_ente_azienda_id", "ca_ente_name", 
                      "ca_work_info_type_id", "ca_title_id", "date_start", "date_end", "ca_tag_id"]
        
        is_internal = False
        if vals.get('persona_id'):
            p = request.env['ca.persona'].browse(vals['persona_id'])
            if p.exists() and p.is_internal: is_internal = True
        
        if not is_internal:
            REQ_FIELDS.extend(["ref_domain", "parent_id"])

        errors = {f: 'missing' for f in REQ_FIELDS if not post.get(f)}
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
            
        fields = [
            'id', 'display_name', 'name', 'lastname', 'fiscalcode', 'email', 'mobile', 
            'is_internal', 'freshman', 'ca_ente_azienda_ids', 'current_tag', 
            'present'
        ]
        return request.env['ca.persona'].search_read([], fields=fields)