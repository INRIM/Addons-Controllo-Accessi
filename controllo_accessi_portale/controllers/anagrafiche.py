import datetime
from typing import Dict

import pytz
from pytz import UTC

from odoo import http
from odoo.http import request
from odoo.orm.domains import Domain as _Domain
expression_AND = _Domain.AND
expression_OR = _Domain.OR
from odoo.tools.misc import format_datetime
from werkzeug.exceptions import Forbidden, NotFound

from .common import check_access_permission


class PortalAnagrafiche(http.Controller):

    def _get_day_start_utc(self, user):
        user_tz = pytz.timezone(user.tz or 'UTC')
        local_now = datetime.datetime.now(user_tz)
        return local_now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ).astimezone(UTC).replace(tzinfo=None)

    def _build_access_domain(self, user, query: str, filter_values: Dict):
        search_domain = [
            # The portal list must be built only from stamping events.
            ("typology", "=", "stamping"),
            ("ca_punto_accesso_category_id", "!=", False),
            ("datetime_event", ">=", self._get_day_start_utc(user)),
        ]
        if query:
            search_domain = expression_AND([
                search_domain,
                [("ca_persona_id.display_name", "ilike", query.strip())],
            ])
        if filter_values.get("internal"):
            search_domain = expression_AND([
                search_domain,
                [("ca_persona_id.is_internal", "=", True)],
            ])
        elif filter_values.get("external"):
            search_domain = expression_AND([
                search_domain,
                [("ca_persona_id.is_external", "=", True)],
            ])
        if filter_values.get("is_present"):
            search_domain = expression_AND([
                search_domain,
                [("ca_persona_id.present", "=", "yes")],
            ])
        if filter_values.get("pa_category_id"):
            search_domain = expression_AND([
                search_domain,
                [("ca_punto_accesso_category_id", "=", filter_values["pa_category_id"])],
            ])
        return search_domain

    def _normalize_order(self, order_by: str, order_dir: str):
        if order_by not in ('display_name', 'last_event'):
            order_by = 'last_event'
        if order_dir not in ('asc', 'desc'):
            order_dir = 'asc' if order_by == 'display_name' else 'desc'
        return order_by, order_dir

    def _get_anagrafiche_data(
            self, env, user, limit: int, offset: int, query: str,
            filter_values: Dict, order_by: str = 'last_event',
            order_dir: str = 'desc'):
        access_model = env['ca.anag_registro_accesso']
        persona_model = env['ca.persona']
        filter_values = filter_values or {}
        order_by, order_dir = self._normalize_order(order_by, order_dir)
        access_domain = self._build_access_domain(user, query, filter_values)

        grouped_accesses = access_model.read_group(
            access_domain,
            ['ca_persona_id', 'last_event:max(datetime_event)'],
            ['ca_persona_id'],
            lazy=False,
        )
        grouped_accesses = [
            group for group in grouped_accesses if group.get('ca_persona_id')
        ]
        all_person_ids = [group['ca_persona_id'][0] for group in grouped_accesses]
        personas_by_id = {
            persona.id: persona
            for persona in persona_model.browse(all_person_ids).exists()
        }
        sortable_entries = []
        for group in grouped_accesses:
            person_id = group['ca_persona_id'][0]
            persona = personas_by_id.get(person_id)
            if not persona:
                continue
            sortable_entries.append({
                'person_id': person_id,
                'display_name_key': (persona.display_name or '').casefold(),
                'last_event': group.get('last_event') or datetime.datetime.min,
            })
        reverse = order_dir == 'desc'
        if order_by == 'display_name':
            sortable_entries.sort(
                key=lambda entry: (
                    entry['display_name_key'],
                    entry['person_id'],
                ),
                reverse=reverse,
            )
        else:
            sortable_entries.sort(
                key=lambda entry: (
                    entry['last_event'],
                    entry['person_id'],
                ),
                reverse=reverse,
            )

        total = len(sortable_entries)
        page_end = offset + limit if limit is not None else None
        paged_entries = sortable_entries[offset:page_end]
        person_ids = [entry['person_id'] for entry in paged_entries]
        data = {"items": [], "total": total}
        if not person_ids:
            return data

        latest_access_rows = access_model.search_read(
            expression_AND([access_domain, [('ca_persona_id', 'in', person_ids)]]),
            fields=[
                'ca_persona_id',
                'datetime_event',
                'direction',
                'ca_punto_accesso_id',
                'ca_punto_accesso_category_id',
            ],
            order='datetime_event desc, id desc',
        )
        latest_access_map = {}
        for access in latest_access_rows:
            person_id = access['ca_persona_id'][0]
            if person_id not in latest_access_map:
                latest_access_map[person_id] = access

        direction_selection = dict(
            access_model.fields_get(['direction'])['direction']['selection']
        )
        present_labels = dict(
            persona_model.fields_get(['present'])['present']['selection']
        )

        access_point_ids = {
            access['ca_punto_accesso_id'][0]
            for access in latest_access_map.values()
            if access.get('ca_punto_accesso_id')
        }
        access_point_names = {
            point.id: point.display_name
            for point in env['ca.punto_accesso'].browse(access_point_ids)
        }

        for person_id in person_ids:
            persona = personas_by_id.get(person_id)
            if not persona:
                continue
            row = {
                'id': persona.id,
                'display_name': persona.display_name,
                'fiscalcode': persona.fiscalcode,
                'is_external': persona.is_external,
                'is_internal': persona.is_internal,
                'present': (
                    persona.present,
                    present_labels.get(persona.present),
                ),
                'datetime_event': '',
                'last_reading_event': '',
                'event_direction': '',
                'event_punto_accesso': '',
            }
            last_access = latest_access_map.get(persona.id)
            if last_access:
                if last_access.get('datetime_event'):
                    row['datetime_event'] = format_datetime(
                        env,
                        last_access['datetime_event'],
                        tz=user.tz,
                        lang_code=user.lang,
                    )
                raw_direction = last_access.get('direction')
                row['event_direction'] = direction_selection.get(
                    raw_direction, raw_direction or ''
                )
                access_category = last_access.get('ca_punto_accesso_category_id')
                if access_category:
                    row['event_punto_accesso'] = access_category[1]
                access_point = last_access.get('ca_punto_accesso_id')
                if access_point and not row['event_punto_accesso']:
                    row['event_punto_accesso'] = access_point_names.get(
                        access_point[0], access_point[1]
                    )
            data["items"].append(row)
        return data

    def _get_anagrafiche_access_point_categories(self, env, user):
        access_domain = self._build_access_domain(user, None, {})
        grouped_accesses = env['ca.anag_registro_accesso'].read_group(
            access_domain,
            ['ca_punto_accesso_category_id'],
            ['ca_punto_accesso_category_id'],
            lazy=False,
        )
        category_ids = [
            group['ca_punto_accesso_category_id'][0]
            for group in grouped_accesses
            if group.get('ca_punto_accesso_category_id')
        ]
        if not category_ids:
            return []
        return env['ca.punto_accesso_category'].sudo().search_read(
            [('id', 'in', category_ids)],
            fields=['id', 'name', 'display_name'],
            order='name asc, id asc',
        )

    @http.route('/anagrafiche', type='http', auth='user', website=True)
    def anagrafiche(self, **kwargs):
        user = request.env.user
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise NotFound()
        return request.render('controllo_accessi_portale.portal_partner_view', {})

    @http.route('/get/anagrafiche', type='jsonrpc', auth='user', website=True, csrf=False)
    def get_anagrafiche(
            self, limit: int, offset: int, query: str, filter: Dict,
            order_by: str = 'last_event', order_dir: str = 'desc', **kwargs):
        user = request.env.user
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise Forbidden()
        return self._get_anagrafiche_data(
            request.env,
            user,
            limit,
            offset,
            query,
            filter,
            order_by,
            order_dir,
        )

    @http.route(
        ['/get/anagrafiche/ca_punto_accesso_category', '/get/anagrafiche/ca_punto_accesso'],
        type='jsonrpc',
        auth='user',
        website=True,
        csrf=False,
    )
    def anagrafiche_punto_accesso_category(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise NotFound()
        return self._get_anagrafiche_access_point_categories(request.env, user)
