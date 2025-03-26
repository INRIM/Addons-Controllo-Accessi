from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.tools.misc import format_datetime
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
    def badge_release_form(self, **kwargs):
        user = request.env.user
        if (
                not user.has_group('controllo_accessi.ca_portineria') and
                (not user.has_group('controllo_accessi.ca_ru') or
                 not user.has_group('controllo_accessi_portale.inrim_access_portal'))
        ):
            raise NotFound()

        return request.render('controllo_accessi_portale.badge_release_view', {})

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
            'date_end': datetime.strptime(kwargs['date_end'][:-6],
                                          '%Y-%m-%dT%H:%M:%S.%f').strftime(
                '%Y-%m-%d %H:%M:%S'),
            'date_start': datetime.strptime(kwargs['date_start'][:-6],
                                            '%Y-%m-%dT%H:%M:%S.%f').strftime(
                '%Y-%m-%d %H:%M:%S'),
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
        wiz = request.env['ca.registra_persona'].create(vals)
        wiz.action_confirm()
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

        ente_azienda_ids = request.env['ca.tipo_ente_azienda'].search([('id', 'not in',
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

        ente_azienda_ids = request.env['ca.tipo_ente_azienda'].search([('id', 'in',
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
