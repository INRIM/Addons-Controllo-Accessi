import datetime
from datetime import timedelta
from uuid import uuid4

from odoo import fields
from odoo.addons.controllo_accessi_portale.controllers.badge_release import (
    PortalBadgeRelease,
)
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "inrim")
class TestPortalBadgeRelease(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = PortalBadgeRelease()
        cls.type_internal = cls.env.ref('inrim_anagrafiche.tipo_persona_interno')
        cls.prop_temp = cls.env.ref('inrim_anagrafiche.proprieta_tag_temporaneo')
        cls.prop_visitor = cls.env.ref('inrim_anagrafiche.proprieta_tag_visitatore')
        cls.prop_definitive = cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo')
        cls.tipo_ente_azienda = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        cls.ente_azienda = cls.env['ca.ente_azienda'].create({
            'name': 'Portal Badge Company',
            'tipo_ente_azienda_id': cls.tipo_ente_azienda.id,
            'company_id': cls.env.company.id,
        })

    def _make_person(self, label):
        persona = self.env['ca.persona'].create({
            'name': label,
            'lastname': label,
            'type_ids': [(6, 0, [self.type_internal.id])],
        })
        persona.ca_ente_azienda_ids = [(6, 0, [self.ente_azienda.id])]
        return persona

    def _make_tag(self, label, property_ids):
        return self.env['ca.tag'].create({
            'name': label,
            'tag_code': uuid4().hex[:16].upper(),
            'ca_proprieta_tag_ids': [(6, 0, property_ids)],
        })

    def _assign_current_tag(self, persona, tag):
        return self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': tag.id,
            'date_start': fields.Datetime.now() - timedelta(days=1),
            'date_end': fields.Datetime.now() + timedelta(days=1),
        })

    def test_badge_release_persona_payload_includes_current_tag_temp(self):
        definitive_person = self._make_person('Portal Definitive')
        temporary_person = self._make_person('Portal Temporary')
        plain_person = self._make_person('Portal Plain')

        definitive_tag = self._make_tag(
            'Portal Definitive Tag',
            [self.prop_definitive.id],
        )
        temporary_tag = self._make_tag(
            'Portal Temporary Tag',
            [self.prop_temp.id, self.prop_visitor.id],
        )

        self._assign_current_tag(definitive_person, definitive_tag)
        self._assign_current_tag(temporary_person, temporary_tag)

        personas = self.controller._get_badge_release_personas(
            self.env,
            [('id', 'in', [definitive_person.id, temporary_person.id, plain_person.id])],
        )
        personas_by_id = {persona['id']: persona for persona in personas}

        self.assertEqual(personas_by_id[definitive_person.id]['current_tag_temp'], False)
        self.assertEqual(personas_by_id[temporary_person.id]['current_tag_temp'], True)
        self.assertIsNone(personas_by_id[plain_person.id]['current_tag_temp'])

    def test_existing_persona_does_not_require_entity_type(self):
        persona = self._make_person('Portal Existing')

        req_fields = self.controller._get_badge_release_required_fields(persona)
        self.assertNotIn('tipo_ente_azienda_id', req_fields)

        vals = {
            'persona_id': persona.id,
            'ca_ente_name': '',
            'vat': '',
        }
        vals = self.controller._populate_company_vals_from_persona(vals, persona)

        self.assertEqual(vals['ente_azienda'], self.ente_azienda.id)
        self.assertEqual(vals['ca_ente_name'], self.ente_azienda.name)
        self.assertEqual(vals['tipo_ente_azienda_id'], self.tipo_ente_azienda.id)

    def test_parse_portal_datetime_prefers_iso_with_offset(self):
        parsed = self.controller._parse_portal_datetime(
            self.env,
            {
                'date_start': '2026-04-02T10:00',
                'date_start_iso': '2026-04-02T10:00:00+02:00',
            },
            'date_start',
        )

        self.assertEqual(parsed, datetime.datetime(2026, 4, 2, 8, 0, 0))

    def test_parse_portal_datetime_localizes_naive_value_with_user_timezone(self):
        original_tz = self.env.user.tz
        self.env.user.tz = 'Europe/Rome'
        try:
            parsed = self.controller._parse_portal_datetime(
                self.env,
                {'date_start': '2026-01-15T10:00'},
                'date_start',
            )
        finally:
            self.env.user.tz = original_tz

        self.assertEqual(parsed, datetime.datetime(2026, 1, 15, 9, 0, 0))
