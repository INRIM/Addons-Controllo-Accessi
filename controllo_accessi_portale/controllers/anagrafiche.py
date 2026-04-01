import datetime
from typing import Dict
from pytz import UTC

from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.tools.misc import format_datetime
from werkzeug.exceptions import Forbidden, NotFound

from .common import check_access_permission


class PortalAnagrafiche(http.Controller):

    @http.route('/anagrafiche', type='http', auth='user', website=True)
    def anagrafiche(self, **kwargs):
        user = request.env.user
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise NotFound()
        return request.render('controllo_accessi_portale.portal_partner_view', {})

    @http.route('/get/anagrafiche', type='json', auth='user', website=True, csrf=False)
    def get_anagrafiche(self, limit: int, offset: int, query: str, filter: Dict, **kwargs):
        user = request.env.user
        today_at_00 = datetime.datetime.combine(datetime.date.today(), datetime.time.min).astimezone(UTC).replace(tzinfo=None)
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise Forbidden()
        search_domain = [("ca_tag_ids", "!=", False), ("last_access", ">=", today_at_00)]
        if query:
            search_domain = expression.AND([[("display_name", "ilike", query)], search_domain])
        if filter:
            if filter.get("internal"):
                search_domain = expression.AND([[("is_internal", "=", True)], search_domain])
            elif filter.get("external"):
                search_domain = expression.AND([[("is_external", "=", True)], search_domain])
            if filter.get("is_present"):
                search_domain = expression.AND([[("present", "=", "yes")], search_domain])
            if filter.get("pa_category_id"):
                search_domain = expression.AND([[("person_access_ids.ca_punto_accesso_category_id", "=", filter["pa_category_id"])], search_domain])
        records = request.env['ca.persona'].search(search_domain, limit=limit, offset=offset)
        count = request.env['ca.persona'].search_count(search_domain)
        access_map = {}
        if records:
            person_ids = records.ids
            access_domain = [
                ('ca_persona_id', 'in', person_ids),
                ('ca_punto_accesso_category_id', '!=', False),
                ('typology', '=', 'stamping')
            ]
            if filter and filter.get("pa_category_id"):
                access_domain = expression.AND([[("ca_punto_accesso_category_id", "=", filter["pa_category_id"])], access_domain])
            all_accesses = request.env['ca.anag_registro_accesso'].search_read(
                access_domain,
                fields=['ca_persona_id', 'datetime_event', 'direction', 'ca_punto_accesso_category_id'],
                order='datetime_event desc, id desc'
            )
            for acc in all_accesses:
                p_id = acc['ca_persona_id'][0]
                if p_id not in access_map:
                    access_map[p_id] = acc
        data = {"items": [], "total": count}
        AccessModel = request.env['ca.anag_registro_accesso']
        direction_selection = dict(AccessModel.fields_get(['direction'])['direction']['selection'])
        cat_ids = set()
        for acc in access_map.values():
            if acc['ca_punto_accesso_category_id']:
                cat_ids.add(acc['ca_punto_accesso_category_id'][0])
        cat_names = {}
        if cat_ids:
            cats = request.env['ca.punto_accesso_category'].browse(cat_ids)
            for c in cats:
                cat_names[c.id] = c.display_name
        present_labels = dict(request.env['ca.persona'].fields_get(['present'])['present']['selection'])
        for record in records:
            row = {
                'id': record.id, 
                'display_name': record.display_name, 
                'fiscalcode': record.fiscalcode,
                'is_external': record.is_external, 
                'is_internal': record.is_internal,
                'present': (record.present, present_labels.get(record.present)),
                'datetime_event': '', 
                'last_reading_event': '', 
                'event_direction': '', 
                'event_punto_accesso': ''
            }
            last_access = access_map.get(record.id)
            if last_access:
                if last_access['datetime_event']:
                    row['datetime_event'] = format_datetime(request.env, last_access['datetime_event'], tz=user.tz, lang_code=user.lang)
                raw_dir = last_access['direction']
                row['event_direction'] = direction_selection.get(raw_dir, raw_dir)
                cat_tuple = last_access['ca_punto_accesso_category_id']
                if cat_tuple:
                    row['event_punto_accesso'] = cat_names.get(cat_tuple[0], cat_tuple[1])
            data["items"].append(row)
        return data

    @http.route('/get/anagrafiche/ca_punto_accesso_category', type='json', auth='user', website=True, csrf=False)
    def anagrafiche_pa_category(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise NotFound()
        return request.env['ca.punto_accesso_category'].search([("ca_access_point_ids", "!=", False)]).read()