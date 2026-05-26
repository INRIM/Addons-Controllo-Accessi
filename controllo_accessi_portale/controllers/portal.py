import datetime
from typing import Dict

from odoo import http, _
from odoo.http import request
from odoo.orm.domains import Domain as _Domain
expression_AND = _Domain.AND
expression_OR = _Domain.OR
from odoo.tools.misc import format_datetime
from pytz import UTC
from werkzeug.exceptions import Forbidden, NotFound


class CustomPortal(http.Controller):

    # HTTP
    @http.route('/anagrafiche', type='http', auth='user', website=True)
    def anagrafiche(self, **kwargs):
        user = request.env.user
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise NotFound()
        return request.render('controllo_accessi_portale.portal_partner_view', {})

    @http.route('/badge_release', auth='user', type='http', website=True)
    def badge_release_form(self, **post):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise NotFound()

        if post and request.httprequest.method == 'POST':
            date_start = post['date_start']
            date_end = post['date_end']
            ca_persona = None
            vals = {
                'vat': post['vat'],
                'ca_ente_name': post['ca_ente_name'],
                'fiscalcode': post['fiscalcode'],
                'lastname': post['lastname'],
                'name': post['name'],
                'freshman': post['freshman'],
                'email': post['email'],
                'mobile': post['mobile'],
                'date_start': date_start,
                'date_end': date_end,
            }
            if post.get('persona_id') != "":
                vals['persona_id'] = int(post['persona_id'])
                ca_persona = request.env['ca.persona'].browse(vals['persona_id'])
            if post.get('tipo_ente_azienda_id'):
                vals['tipo_ente_azienda_id'] = int(post['tipo_ente_azienda_id'])
            if post.get('azienda'):
                vals['ente_azienda'] = int(post['azienda'])
            if post.get('ca_work_info_type_id'):
                vals['ca_work_info_type_id'] = int(post['ca_work_info_type_id'])
            if post.get('ca_title_id'):
                vals['ca_title_id'] = int(post['ca_title_id'])
            if post.get('ca_tag_id'):
                vals['ca_tag_id'] = int(post['ca_tag_id'])
            if post.get('parent_id'):
                vals['parent_id'] = int(post['parent_id'])
            if post.get('ref_domain'):
                vals['ref_domain'] = post['ref_domain']

            REQ_FIELDS = [
                "lastname", "name", "fiscalcode",
                "tipo_ente_azienda_id", "ca_ente_name",
                "ref_domain", "parent_id", "ca_work_info_type_id", "ca_title_id",
                "date_start", "date_end", "ca_tag_id"
            ]
            if ca_persona and ca_persona.is_internal:
                REQ_FIELDS.pop(REQ_FIELDS.index('ref_domain'))
                REQ_FIELDS.pop(REQ_FIELDS.index('parent_id'))

            errors = {}
            error_message = []
            # Validation
            for field_name in REQ_FIELDS:
                if not post.get(field_name):
                    errors[field_name] = 'missing'

            # error message for empty required fields
            if [err for err in errors.values() if err == 'missing']:
                error_message.append(_('Some required fields are empty.'))

            if errors:
                return request.render('controllo_accessi_portale.badge_release_view', {
                    "errors": errors,
                    "error_message": "\n".join(error_message),
                    "values": vals
                })

            add_doc = not vals.get("persona_id", False)

            wiz = request.env['ca.registra_persona'].with_context(no_compute_tag_id_number=True).create({
                **vals,
                "date_start": datetime.datetime.fromisoformat(
                    post['date_start']).astimezone(UTC).replace(tzinfo=None),
                "date_end": datetime.datetime.fromisoformat(post['date_end']).astimezone(
                    UTC).replace(tzinfo=None),
            })
            wiz.action_confirm()

            if add_doc:
                return request.redirect(f"/badge_release_docs/{wiz.persona_id.id}")
            else:
                return request.redirect('/anagrafiche')

        return request.render('controllo_accessi_portale.badge_release_view', {
            "errors": {},
            "error_message": "",
            "values": {}
        })

    @http.route('/badge_release_docs/<int:persona_id>', auth='user', type='http',
                website=True)
    def badge_release_docs_form(self, persona_id, **post):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise NotFound()

        persona_obj = request.env['ca.persona'].browse(persona_id)

        if not persona_obj.exists():
            raise NotFound()

        if post and request.httprequest.method == 'POST':
            REQ_FIELDS = [
                "tipo_documento_id",
                "validity_start_date",
                "validity_end_date",
                "document_code",
                "issued_by",
            ]

            errors = {}
            error_message = []
            # Validation
            for field_name in REQ_FIELDS:
                if not post.get(field_name):
                    errors[field_name] = 'missing'

            # error message for empty required fields
            if [err for err in errors.values() if err == 'missing']:
                error_message.append(_('Some required fields are empty.'))

            values = {f: post.get(f) for f in REQ_FIELDS}
            values = {
                **values,
                "persona_id": persona_obj.id,
                "tipo_documento_id": int(values[
                                             'tipo_documento_id']) if 'tipo_documento_id' in values else None,
            }

            if errors:
                return request.render(
                    'controllo_accessi_portale.badge_release_docs_view', {
                        "persona_id": persona_obj.id,
                        "errors": errors,
                        "error_message": "\n".join(error_message),
                        "values": values
                    })

            wiz = request.env['ca.registra_doc_persona'].create({
                "persona_id": values["persona_id"],
                "tipo_documento_id": values["tipo_documento_id"],
                "validity_start_date": values["validity_start_date"],
                "validity_end_date": values["validity_end_date"],
                "document_code": values["document_code"],
                "issued_by": values["issued_by"]
            })
            wiz.action_confirm()

            return request.redirect('/anagrafiche')

        return request.render('controllo_accessi_portale.badge_release_docs_view', {
            "persona_id": persona_obj.id,
            "errors": {},
            "error_message": "",
            "values": {}
        })

    @http.route('/badge_return', type='http', auth='user', website=True)
    def portal_badge_return(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise NotFound()
        return request.render('controllo_accessi_portale.badge_return_view', {})

    # SUBMIT
    @http.route('/badge_release/submit', auth='user', type='http', website=True,
                methods=['POST'], csrf=False)
    def badge_release_submit(self, **kwargs):
        date_start = datetime.datetime.fromisoformat(kwargs['date_start']).astimezone(
            UTC).replace(tzinfo=None)
        date_end = datetime.datetime.fromisoformat(kwargs['date_end']).astimezone(
            UTC).replace(tzinfo=None)
        vals = {
            'vat': kwargs['vat'],
            'ca_ente_name': kwargs['ca_ente_name'],
            'fiscalcode': kwargs['fiscalcode'],
            'lastname': kwargs['lastname'],
            'name': kwargs['name'],
            'freshman': kwargs['freshman'],
            'email': kwargs['email'],
            'mobile': kwargs['mobile'],
            'ref_domain': kwargs['ref_domain'],
            'date_start': date_start,
            'date_end': date_end,
        }
        if kwargs['persona_id'] != "":
            vals['persona_id'] = int(kwargs['persona_id']),
        if kwargs['tipo_ente_azienda_id'] != "":
            vals['tipo_ente_azienda_id'] = int(kwargs['tipo_ente_azienda_id']),
        if kwargs['azienda'] != "":
            vals['ente_azienda'] = int(kwargs['azienda'])
        if kwargs['ca_work_info_type_id'] != "":
            vals['ca_work_info_type_id'] = int(kwargs['ca_work_info_type_id'])
        if kwargs['ca_title_id'] != "":
            vals['ca_title_id'] = int(kwargs['ca_title_id'])
        if kwargs['ca_tag_id'] != "":
            vals['ca_tag_id'] = int(kwargs['ca_tag_id'])
        if kwargs['parent_id'] != "":
            vals['parent_id'] = int(kwargs['parent_id'])

        add_doc = bool(vals["persona_id"])

        wiz = request.env['ca.registra_persona'].create(vals)
        wiz.action_confirm()

        if add_doc:
            return request.redirect(f"/badge_release_docs/{int(kwargs['persona_id'])}")
        else:
            return request.redirect('/badge_release')

    @http.route('/badge_return/submit', auth='user', type='http', website=True,
                methods=['POST'], csrf=False)
    def badge_return_submit(self, **kwargs):
        vals = {
            'ca_tag_id': int(kwargs['tag_id']),
        }
        wiz = request.env['ca.restituisci_badge'].create(vals)
        wiz.action_confirm()
        return request.redirect('/badge_return')

    # JSON
    @http.route('/get/anagrafiche', type='jsonrpc', auth='user', website=True, csrf=False)
    def get_anagrafiche(self, limit: int, offset: int, query: str, filter: Dict, **kwargs):
        user = request.env.user

        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise Forbidden()

        # Filtra per:
        # tag_ids presenti, in modo da escludere persone senza nemmeno un tag attivo
        search_domain = [
            ("ca_tag_ids", "!=", False)
        ]
        if query:
            search_domain = expression_AND([[("display_name", "ilike", query)], search_domain])

        if filter:
            if filter.get("internal", False):
                search_domain = expression_AND([[("is_internal", "=", True)], search_domain])
            elif filter.get("external", False):
                search_domain = expression_AND([[("is_external", "=", True)], search_domain])

            if filter.get("is_present", False):
                search_domain = expression_AND([[("present", "=", "yes")], search_domain])

            if filter.get("pa_category_id", None):
                search_domain = expression_AND(
                    [[("person_access_ids.ca_punto_accesso_category_id", "=", filter["pa_category_id"])],
                     search_domain])

        records = request.env['ca.persona'].search(search_domain, limit=limit, offset=offset)
        count = request.env['ca.persona'].search_count(search_domain)
        data = {
            "items": [],
            "total": count
        }
        row = {}
        for record in records:
            row = {
                'id': record.id,
                'display_name': record.display_name,
                'fiscalcode': record.fiscalcode,
                'is_external': record.is_external,
                'is_internal': record.is_internal,
                'present': (record.present,
                            dict(record._fields['present']._description_selection(request.env)).get(
                                record.present)),
                'datetime_event': '',
                'last_reading_event': '',
                'event_direction': '',
                'event_punto_accesso': ''
            }
            if record.person_access_ids:
                # Filtra per:
                # - ca_persona_id
                # - ca_punto_accesso_category_id - per escludere le righe a cui l'utente non ha accesso (vedi record_rule)
                la_search_domain = [
                    ("ca_persona_id", "=", record.id),
                    ("ca_punto_accesso_category_id", "!=", False)
                    # ("ca_punto_accesso_category_id", "in", category_ids.ids)
                ]
                if filter and filter.get("pa_category_id", None):
                    la_search_domain = expression_AND(
                        [[("ca_punto_accesso_category_id", "=", filter["pa_category_id"])], la_search_domain])

                last_access = record.person_access_ids.search(la_search_domain)

                if last_access:
                    last_access = last_access.sorted("datetime_event", reverse=True)[0]

                if last_access.datetime_event:
                    row['datetime_event'] = format_datetime(
                        request.env,
                        last_access.datetime_event,
                        tz=user.tz,
                        lang_code=user.lang,
                    )

                if last_access.direction:
                    row['event_direction'] = dict(last_access._fields['direction']._description_selection(request.env))[
                        last_access.direction]

                if last_access.ca_punto_accesso_category_id:
                    row['event_punto_accesso'] = last_access.ca_punto_accesso_category_id.display_name

            data["items"].append(row)
        return data

    @http.route('/get/anagrafiche/ca_punto_accesso_category', type='jsonrpc', auth='user', website=True, csrf=False)
    def anagrafiche_pa_category(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        # category_ids = request.env['ca.punto_accesso_category'].sudo().search([("allowed_users", "in", [user.id])])
        category_ids = request.env['ca.punto_accesso_category'].search([("ca_access_point_ids", "!=", False)])

        return category_ids.read()

    @http.route('/get/badge_release/ca_persona', auth='user', type='jsonrpc', website=True)
    def badge_release_ca_persona(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        ca_persona = request.env['ca.persona'].search_read([])


        return ca_persona

    @http.route('/get/badge_release/ca_persona_parent', auth='user', type='jsonrpc',
                website=True)
    def badge_release_ca_persona_parent(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        parent_ids = request.env['ca.persona'].search([
            ('is_internal', '=', True),
        ])

        return parent_ids.read()

    @http.route('/get/badge_release/tipo_enti_azienda', auth='user', type='jsonrpc',
                website=True)
    def badge_release_tipo_enti_azienda(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        ente_azienda_ids = request.env['ca.tipo_ente_azienda'].search(
            [('id', 'not in',
              [
                  request.env.ref(
                      'inrim_anagrafiche.tipo_ente_azienda_sede').id,
                  request.env.ref(
                      'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
              ])])

        return ente_azienda_ids.read()

    @http.route('/get/badge_release/tipo_enti_azienda_hidden', auth='user', type='jsonrpc',
                website=True)
    def badge_release_tipo_enti_azienda_hidden(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        ente_azienda_ids = request.env['ca.tipo_ente_azienda'].search(
            [('id', 'in',
              [
                  request.env.ref(
                      'inrim_anagrafiche.tipo_ente_azienda_sede').id,
                  request.env.ref(
                      'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
              ])])

        return ente_azienda_ids.read()

    @http.route('/get/badge_release/work_info_type', auth='user', type='jsonrpc',
                website=True)
    def badge_release_work_info_type(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        work_info_type_ids = request.env['ca.work_info_type'].search([])

        return work_info_type_ids.read()

    @http.route('/get/badge_release/titolo_persona', auth='user', type='jsonrpc',
                website=True)
    def badge_release_titolo_persona(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        titolo_persona_ids = request.env['ca.titolo_persona'].search([])

        return titolo_persona_ids.read()

    @http.route('/get/badge_release/tags', auth='user', type='jsonrpc', website=True)
    def badge_release_tags(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        tag_ids = request.env['ca.tag'].search([
            ('in_use', '=', False),
            ('revoked', '=', False)
        ])

        return tag_ids.read()

    @http.route('/get/badge_release/ente_azienda', auth='user', type='jsonrpc',
                website=True, csrf=False)
    def badge_release_ente_azienda(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        ente_azienda_ids = request.env['ca.ente_azienda'].search([])
        if ente_azienda_ids:
            return ente_azienda_ids.read()
        return {}

    @http.route('/get/badge_release/work_info', auth='user', type='jsonrpc', website=True,
                csrf=False)
    def badge_release_work_info(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        winfo_ids = request.env['ca.work_info'].search([])
        if winfo_ids:
            return winfo_ids.read()
        return {}

    @http.route('/get/badge_release/tag_filter_domain', auth='user', type='jsonrpc',
                website=True, csrf=False)
    def badge_release_tag_filter_domain(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        tags1_ids = request.env['ca.proprieta_tag'].search([
            ('id', 'in', [
                request.env.ref('inrim_anagrafiche.proprieta_tag_visitatore').id,
                request.env.ref('inrim_anagrafiche.proprieta_tag_servizio').id
            ])
        ])
        tags2_ids = request.env['ca.proprieta_tag'].search([
            ('id', 'in', [
                request.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id,
                request.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
            ])
        ])
        tags3_ids = request.env['ca.proprieta_tag'].search([
            ('id', 'in', [
                request.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id
            ])
        ])
        return tags1_ids.read(), tags2_ids.read(), tags3_ids.read()

    @http.route('/get/badge_release_docs/tipo_documento', auth='user', type='jsonrpc',
                website=True, csrf=False)
    def badge_release_tipo_documento(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        tipi_doc = request.env['ca.tipo_doc_ident'].search([])

        return tipi_doc.read()

    @http.route('/get/badge_return/tags', auth='user', type='jsonrpc', website=True)
    def badge_return_tags(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        tag_ids = request.env['ca.tag_persona'].search([
            ('state', '=', "to_give_back"),
            ('ca_tag_id.in_use', '=', True)
        ])

        ret = []

        for record in tag_ids:
            rec_dict = record.read()[0]
            rec_dict["tag_code"] = record.ca_tag_id.tag_code
            ret.append(rec_dict)
        return ret
