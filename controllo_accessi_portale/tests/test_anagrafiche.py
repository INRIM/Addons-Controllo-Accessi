from datetime import date, timedelta
from uuid import uuid4

from odoo import fields
from odoo.addons.controllo_accessi_portale.controllers.anagrafiche import (
    PortalAnagrafiche,
)
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class TestPortalAnagrafiche(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = PortalAnagrafiche()
        cls.portal_user = cls.env.user
        cls.portal_user.write({
            'tz': 'Europe/Rome',
            'lang': cls.portal_user.lang or 'en_US',
        })
        cls.type_internal = cls.env.ref('inrim_anagrafiche.tipo_persona_interno')
        cls.type_external = cls.env.ref('inrim_anagrafiche.tipo_persona_esterno')
        cls.tipo_ente_azienda = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        cls.tipo_spazio = cls.env.ref('inrim_anagrafiche.tipo_spazio_locale')
        cls.ente_azienda = cls.env['ca.ente_azienda'].create({
            'name': 'Portal Test HQ',
            'tipo_ente_azienda_id': cls.tipo_ente_azienda.id,
            'company_id': cls.env.company.id,
            'tz': 'Europe/Rome',
        })
        cls.spazio = cls.env['ca.spazio'].create({
            'name': 'Portal Test Space',
            'tipo_spazio_id': cls.tipo_spazio.id,
            'ente_azienda_id': cls.ente_azienda.id,
        })
        cls.spazio_in = cls.env['ca.spazio'].create({
            'name': 'Portal Test Space In',
            'tipo_spazio_id': cls.tipo_spazio.id,
            'ente_azienda_id': cls.ente_azienda.id,
        })
        cls.spazio_out = cls.env['ca.spazio'].create({
            'name': 'Portal Test Space Out',
            'tipo_spazio_id': cls.tipo_spazio.id,
            'ente_azienda_id': cls.ente_azienda.id,
        })
        cls.reader_in = cls.env['ca.lettore'].create({
            'name': 'Portal Test Reader In',
            'reader_ip': f'10.200.0.{int(uuid4().hex[:2], 16)}',
            'direction': 'in',
        })
        cls.reader_out = cls.env['ca.lettore'].create({
            'name': 'Portal Test Reader Out',
            'reader_ip': f'10.200.1.{int(uuid4().hex[:2], 16)}',
            'direction': 'out',
        })
        cls.reader_local = cls.env['ca.lettore'].create({
            'name': 'Portal Test Reader Local',
            'reader_ip': f'10.200.2.{int(uuid4().hex[:2], 16)}',
            'direction': 'in',
        })
        cls.reader_local_only = cls.env['ca.lettore'].create({
            'name': 'Portal Test Reader Local Only',
            'reader_ip': f'10.200.3.{int(uuid4().hex[:2], 16)}',
            'direction': 'in',
        })
        cls.category_in = cls.env['ca.punto_accesso_category'].create({
            'name': 'Portal Test In',
            'code': 'PORTAL_TEST_IN',
        })
        cls.category_out = cls.env['ca.punto_accesso_category'].create({
            'name': 'Portal Test Out',
            'code': 'PORTAL_TEST_OUT',
        })
        cls.category_local_only = cls.env['ca.punto_accesso_category'].create({
            'name': 'Portal Test Local Only',
            'code': 'PORTAL_TEST_LOCAL_ONLY',
        })
        cls.punto_accesso_1 = cls.env['ca.punto_accesso'].create({
            'ca_spazio_id': cls.spazio_in.id,
            'ca_lettore_id': cls.reader_in.id,
            'ca_category': cls.category_in.id,
            'typology': 'stamping',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
        })
        cls.punto_accesso_2 = cls.env['ca.punto_accesso'].create({
            'ca_spazio_id': cls.spazio_out.id,
            'ca_lettore_id': cls.reader_out.id,
            'ca_category': cls.category_out.id,
            'typology': 'stamping',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
        })
        cls.punto_accesso_local = cls.env['ca.punto_accesso'].create({
            'ca_spazio_id': cls.spazio.id,
            'ca_lettore_id': cls.reader_local.id,
            'ca_category': cls.category_in.id,
            'typology': 'local_access',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
        })
        cls.punto_accesso_local_only = cls.env['ca.punto_accesso'].create({
            'ca_spazio_id': cls.spazio.id,
            'ca_lettore_id': cls.reader_local_only.id,
            'ca_category': cls.category_local_only.id,
            'typology': 'local_access',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
        })

    def _make_person_with_tag(self, label, person_type):
        persona = self.env['ca.persona'].create({
            'name': label,
            'lastname': label,
            'type_ids': [(6, 0, [person_type.id])],
        })
        tag = self.env['ca.tag'].create({
            'name': f'{label} Tag',
            'tag_code': uuid4().hex[:16].upper(),
        })
        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': tag.id,
            'date_start': fields.Datetime.now() - timedelta(days=1),
            'date_end': fields.Datetime.now() + timedelta(days=1),
        })
        return persona, tag_persona

    def _add_access(self, punto_accesso, tag_persona, datetime_event):
        return self.env['ca.anag_registro_accesso'].aggiungi_riga_accesso(
            punto_accesso,
            tag_persona,
            datetime_event,
        )

    def _load_data(
            self, query, filter_values=None, order_by='last_event',
            order_dir='desc'):
        return self.controller._get_anagrafiche_data(
            self.env,
            self.portal_user,
            80,
            0,
            query,
            filter_values or {},
            order_by,
            order_dir,
        )

    def test_get_anagrafiche_uses_today_accesses_and_latest_event(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        query = 'PortalMidnight'

        latest_person, latest_tag = self._make_person_with_tag(
            f'{query} Latest',
            self.type_external,
        )
        other_person, other_tag = self._make_person_with_tag(
            f'{query} Other',
            self.type_internal,
        )
        yesterday_person, yesterday_tag = self._make_person_with_tag(
            f'{query} Yesterday',
            self.type_internal,
        )

        self._add_access(
            self.punto_accesso_1,
            latest_tag,
            today_start_utc - timedelta(minutes=5),
        )
        self._add_access(
            self.punto_accesso_1,
            latest_tag,
            today_start_utc + timedelta(hours=9),
        )
        self._add_access(
            self.punto_accesso_2,
            latest_tag,
            today_start_utc + timedelta(hours=11),
        )
        self._add_access(
            self.punto_accesso_1,
            other_tag,
            today_start_utc + timedelta(hours=10),
        )
        self._add_access(
            self.punto_accesso_1,
            yesterday_tag,
            today_start_utc - timedelta(hours=1),
        )

        data = self._load_data(query)

        self.assertEqual(data['total'], 2)
        self.assertEqual(
            [item['id'] for item in data['items']],
            [latest_person.id, other_person.id],
        )
        latest_row = data['items'][0]
        self.assertEqual(latest_row['present'][0], 'no')
        self.assertEqual(
            latest_row['event_punto_accesso'],
            self.category_out.display_name,
        )
        self.assertTrue(latest_row['datetime_event'])
        self.assertNotIn(yesterday_person.id, [item['id'] for item in data['items']])

    def test_get_anagrafiche_applies_internal_external_presence_and_category_filters(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        query = 'PortalFilters'

        internal_person, internal_tag = self._make_person_with_tag(
            f'{query} Internal',
            self.type_internal,
        )
        external_person, external_tag = self._make_person_with_tag(
            f'{query} External',
            self.type_external,
        )

        self._add_access(
            self.punto_accesso_1,
            internal_tag,
            today_start_utc + timedelta(hours=8),
        )
        self._add_access(
            self.punto_accesso_1,
            external_tag,
            today_start_utc + timedelta(hours=9),
        )
        self._add_access(
            self.punto_accesso_2,
            external_tag,
            today_start_utc + timedelta(hours=12),
        )

        internal_data = self._load_data(query, {'internal': True})
        self.assertEqual(internal_data['total'], 1)
        self.assertEqual(internal_data['items'][0]['id'], internal_person.id)

        external_data = self._load_data(query, {'external': True})
        self.assertEqual(external_data['total'], 1)
        self.assertEqual(external_data['items'][0]['id'], external_person.id)
        self.assertEqual(
            external_data['items'][0]['event_punto_accesso'],
            self.category_out.display_name,
        )

        present_data = self._load_data(query, {'is_present': True})
        self.assertEqual(present_data['total'], 1)
        self.assertEqual(present_data['items'][0]['id'], internal_person.id)

        category_data = self._load_data(
            query,
            {'pa_category_id': self.category_in.id},
        )
        self.assertEqual(category_data['total'], 2)
        access_point_rows = {item['id']: item for item in category_data['items']}
        self.assertEqual(
            access_point_rows[internal_person.id]['event_punto_accesso'],
            self.category_in.display_name,
        )
        self.assertEqual(
            access_point_rows[external_person.id]['event_punto_accesso'],
            self.category_in.display_name,
        )

    def test_get_anagrafiche_ignores_non_stamping_accesses(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        query = 'PortalLocalOnly'

        local_person, local_tag = self._make_person_with_tag(
            query,
            self.type_internal,
        )
        self._add_access(
            self.punto_accesso_local,
            local_tag,
            today_start_utc + timedelta(hours=7),
        )

        data = self._load_data(query)

        self.assertEqual(data['total'], 0)
        self.assertEqual(data['items'], [])

    def test_get_anagrafiche_applies_remote_sorting(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        query = 'PortalSorting'

        alpha_person, alpha_tag = self._make_person_with_tag(
            f'{query} Alpha',
            self.type_internal,
        )
        bravo_person, bravo_tag = self._make_person_with_tag(
            f'{query} Bravo',
            self.type_internal,
        )
        charlie_person, charlie_tag = self._make_person_with_tag(
            f'{query} Charlie',
            self.type_internal,
        )

        self._add_access(
            self.punto_accesso_1,
            alpha_tag,
            today_start_utc + timedelta(hours=8),
        )
        self._add_access(
            self.punto_accesso_1,
            charlie_tag,
            today_start_utc + timedelta(hours=9),
        )
        self._add_access(
            self.punto_accesso_2,
            bravo_tag,
            today_start_utc + timedelta(hours=10),
        )

        last_event_desc = self._load_data(query)
        self.assertEqual(
            [item['id'] for item in last_event_desc['items']],
            [bravo_person.id, charlie_person.id, alpha_person.id],
        )

        last_event_asc = self._load_data(
            query,
            order_by='last_event',
            order_dir='asc',
        )
        self.assertEqual(
            [item['id'] for item in last_event_asc['items']],
            [alpha_person.id, charlie_person.id, bravo_person.id],
        )

        name_asc = self._load_data(
            query,
            order_by='display_name',
            order_dir='asc',
        )
        self.assertEqual(
            [item['id'] for item in name_asc['items']],
            [alpha_person.id, bravo_person.id, charlie_person.id],
        )

        name_desc = self._load_data(
            query,
            order_by='display_name',
            order_dir='desc',
        )
        self.assertEqual(
            [item['id'] for item in name_desc['items']],
            [charlie_person.id, bravo_person.id, alpha_person.id],
        )

    def test_get_anagrafiche_loads_only_categories_used_by_today_stamping_accesses(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        person_in, tag_in = self._make_person_with_tag(
            'PortalCategoryIn',
            self.type_internal,
        )
        person_out, tag_out = self._make_person_with_tag(
            'PortalCategoryOut',
            self.type_external,
        )
        person_local, tag_local = self._make_person_with_tag(
            'PortalCategoryLocal',
            self.type_external,
        )

        self._add_access(
            self.punto_accesso_1,
            tag_in,
            today_start_utc + timedelta(hours=8),
        )
        self._add_access(
            self.punto_accesso_2,
            tag_out,
            today_start_utc + timedelta(hours=9),
        )
        self._add_access(
            self.punto_accesso_local_only,
            tag_local,
            today_start_utc + timedelta(hours=10),
        )

        categories = self.controller._get_anagrafiche_access_point_categories(
            self.env,
            self.portal_user,
        )

        category_ids = [record['id'] for record in categories]

        self.assertIn(self.category_in.id, category_ids)
        self.assertIn(self.category_out.id, category_ids)
        self.assertNotIn(self.category_local_only.id, category_ids)

    def test_get_anagrafiche_loads_categories_even_if_access_point_rule_hides_points(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        hidden_user = self.env['res.users'].with_context(
            no_reset_password=True,
        ).create({
            'name': 'Portal Hidden Categories User',
            'login': f'portal_hidden_{uuid4().hex[:8]}',
            'email': f'portal_hidden_{uuid4().hex[:8]}@example.com',
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, [self.env.company.id])],
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('controllo_accessi.ca_ca').id,
            ])],
        })
        hidden_reader = self.env['ca.lettore'].create({
            'name': 'Portal Hidden Reader',
            'reader_ip': f'10.200.4.{int(uuid4().hex[:2], 16)}',
            'direction': 'in',
        })
        hidden_category = self.env['ca.punto_accesso_category'].create({
            'name': 'Portal Hidden Category',
            'code': 'PORTAL_HIDDEN_CATEGORY',
        })
        hidden_point = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.spazio.id,
            'ca_lettore_id': hidden_reader.id,
            'ca_category': hidden_category.id,
            'typology': 'stamping',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
            'allowed_users': [(6, 0, [])],
        })
        hidden_person, hidden_tag = self._make_person_with_tag(
            'PortalHiddenCategory',
            self.type_internal,
        )
        self._add_access(
            hidden_point,
            hidden_tag,
            today_start_utc + timedelta(hours=11),
        )

        self.assertFalse(
            self.env['ca.punto_accesso'].with_user(hidden_user).search(
                [('id', '=', hidden_point.id)],
                limit=1,
            )
        )

        user_env = self.env['ca.punto_accesso_category'].with_user(hidden_user).env
        categories = self.controller._get_anagrafiche_access_point_categories(
            user_env,
            hidden_user,
        )
        category_ids = [record['id'] for record in categories]

        self.assertIn(hidden_category.id, category_ids)

    def test_get_anagrafiche_filters_hidden_point_category_without_point_read_access(self):
        today_start_utc = self.controller._get_day_start_utc(self.portal_user)
        hidden_user = self.env['res.users'].with_context(
            no_reset_password=True,
        ).create({
            'name': 'Portal Hidden Filter User',
            'login': f'portal_hidden_filter_{uuid4().hex[:8]}',
            'email': f'portal_hidden_filter_{uuid4().hex[:8]}@example.com',
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, [self.env.company.id])],
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('controllo_accessi.ca_ca').id,
                self.env.ref('controllo_accessi_portale.inrim_access_portal').id,
            ])],
        })
        hidden_reader = self.env['ca.lettore'].create({
            'name': 'Portal Hidden Filter Reader',
            'reader_ip': f'10.200.5.{int(uuid4().hex[:2], 16)}',
            'direction': 'in',
        })
        hidden_category = self.env['ca.punto_accesso_category'].create({
            'name': 'Portal Hidden Filter Category',
            'code': 'PORTAL_HIDDEN_FILTER_CATEGORY',
        })
        hidden_point = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.spazio.id,
            'ca_lettore_id': hidden_reader.id,
            'ca_category': hidden_category.id,
            'typology': 'stamping',
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=30),
            'allowed_users': [(6, 0, [])],
        })
        hidden_person, hidden_tag = self._make_person_with_tag(
            'PortalHiddenFilter',
            self.type_internal,
        )
        self._add_access(
            hidden_point,
            hidden_tag,
            today_start_utc + timedelta(hours=12),
        )

        self.assertFalse(
            self.env['ca.punto_accesso'].with_user(hidden_user).search(
                [('id', '=', hidden_point.id)],
                limit=1,
            )
        )

        user_env = self.env['ca.persona'].with_user(hidden_user).env
        data = self.controller._get_anagrafiche_data(
            user_env,
            hidden_user,
            80,
            0,
            'PortalHiddenFilter',
            {'pa_category_id': hidden_category.id},
        )

        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['id'], hidden_person.id)
