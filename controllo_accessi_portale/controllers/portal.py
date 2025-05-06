import datetime

from odoo import http, _
from odoo.http import request
from odoo.tools import parse_date
from odoo.tools.misc import format_datetime
from werkzeug.exceptions import Forbidden, NotFound
from pytz import UTC


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
            vals = {
                'vat': post['vat'],
                'ca_ente_name': post['ca_ente_name'],
                'fiscalcode': post['fiscalcode'],
                'lastname': post['lastname'],
                'name': post['name'],
                'freshman': post['freshman'],
                'email': post['email'],
                'mobile': post['mobile'],
                'ref_domain': post['ref_domain'],
                'date_start': date_start,
                'date_end': date_end,
            }
            if post.get('persona_id') != "":
                vals['persona_id'] = int(post['persona_id'])
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

            REQ_FIELDS = [
                "lastname", "name", "fiscalcode",
                "tipo_ente_azienda_id", "ca_ente_name",
                "ref_domain", "parent_id", "ca_work_info_type_id", "ca_title_id",
                "date_start", "date_end", "ca_tag_id"
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

            if errors:
                print('post', post)
                print('vals', vals)
                return request.render('controllo_accessi_portale.badge_release_view', {
                    "errors": errors,
                    "error_message": "\n".join(error_message),
                    "values": vals
                })

            add_doc = bool(vals["persona_id"])

            wiz = request.env['ca.registra_persona'].create({
                **vals,
                "date_start": datetime.datetime.fromisoformat(post['date_start']).astimezone(UTC).replace(tzinfo=None),
                "date_end": datetime.datetime.fromisoformat(post['date_end']).astimezone(UTC).replace(tzinfo=None),
            })
            wiz.action_confirm()

            if add_doc:
                return request.redirect(f"/badge_release_docs/{int(post['persona_id'])}")
            else:
                return request.redirect('/anagrafiche')

        return request.render('controllo_accessi_portale.badge_release_view', {
            "errors": {},
            "error_message": "",
            "values": {}
        })

    @http.route('/badge_release_docs/<int:persona_id>', auth='user', type='http', website=True)
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
                "tipo_documento_id": int(values['tipo_documento_id']) if 'tipo_documento_id' in values else None,
            }

            if errors:
                return request.render('controllo_accessi_portale.badge_release_docs_view', {
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
        date_start = datetime.datetime.fromisoformat(kwargs['date_start']).astimezone(UTC).replace(tzinfo=None)
        date_end = datetime.datetime.fromisoformat(kwargs['date_end']).astimezone(UTC).replace(tzinfo=None)
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
    @http.route('/get/anagrafiche', type='json', auth='user', website=True, csrf=False)
    def get_anagrafiche(self, **kwargs):
        user = request.env.user
        if not user.has_group('controllo_accessi_portale.inrim_access_portal'):
            raise Forbidden()
        records = request.env['ca.persona'].search([])
        data = []
        row = {}
        for record in records:
            row = {
                'id': record.id,
                'display_name': record.display_name,
                'fiscalcode': record.fiscalcode,
                'is_external': record.is_external,
                'is_internal': record.is_internal,
                'present': (record.present,
                            dict(record._fields['present'].selection).get(
                                record.present)),
                'datetime_event': '',
                'last_reading_event': '',
            }
            if record.person_access_ids:
                if record.person_access_ids[0].datetime_event:
                    row['datetime_event'] = format_datetime(
                        request.env,
                        record.person_access_ids[0].datetime_event,
                        tz=user.tz,
                        lang_code=user.lang,
                    )
                if record.person_access_ids[0].ca_punto_accesso_id and \
                        record.person_access_ids[
                            0].ca_punto_accesso_id.last_reading_events:
                    row['last_reading_event'] = format_datetime(
                        request.env,
                        record.person_access_ids[
                            0].ca_punto_accesso_id.last_reading_events,
                        tz=user.tz,
                        lang_code=user.lang,
                    )
            data.append(row)
        return data

    @http.route('/get/badge_release/ca_persona', auth='user', type='json', website=True)
    def badge_release_ca_persona(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise Forbidden()

        ca_persona = request.env['ca.persona'].search([])

        return ca_persona.read()

    @http.route('/get/badge_release/ca_persona_parent', auth='user', type='json',
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

    @http.route('/get/badge_release/tipo_enti_azienda', auth='user', type='json',
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

    @http.route('/get/badge_release/tipo_enti_azienda_hidden', auth='user', type='json',
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

    @http.route('/get/badge_release/work_info_type', auth='user', type='json',
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

    @http.route('/get/badge_release/titolo_persona', auth='user', type='json',
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

    @http.route('/get/badge_release/tags', auth='user', type='json', website=True)
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

    @http.route('/get/badge_release/ente_azienda', auth='user', type='json',
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

    @http.route('/get/badge_release/work_info', auth='user', type='json', website=True,
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

    @http.route('/get/badge_release/tag_filter_domain', auth='user', type='json',
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
        return tags1_ids.read(), tags2_ids.read()

    @http.route('/get/badge_release_docs/tipo_documento', auth='user', type='json',
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

    @http.route('/get/badge_return/tags', auth='user', type='json', website=True)
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

        return tag_ids.read()
