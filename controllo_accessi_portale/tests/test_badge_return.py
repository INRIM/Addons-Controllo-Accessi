from datetime import timedelta
from uuid import uuid4

from odoo import fields
from odoo.addons.controllo_accessi_portale.controllers.badge_return import (
    PortalBadgeReturn,
)
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "inrim")
class TestPortalBadgeReturn(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = PortalBadgeReturn()
        cls.type_internal = cls.env.ref('inrim_anagrafiche.tipo_persona_interno')
        cls.prop_temp = cls.env.ref('inrim_anagrafiche.proprieta_tag_temporaneo')
        cls.prop_visitor = cls.env.ref('inrim_anagrafiche.proprieta_tag_visitatore')
        cls.prop_jolly = cls.env.ref('inrim_anagrafiche.proprieta_tag_jolly')
        cls.prop_definitive = cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo')

    def _make_person(self, label):
        return self.env['ca.persona'].create({
            'name': label,
            'lastname': label,
            'type_ids': [(6, 0, [self.type_internal.id])],
        })

    def _make_tag(self, label, property_ids):
        return self.env['ca.tag'].create({
            'name': label,
            'tag_code': uuid4().hex[:16].upper(),
            'ca_proprieta_tag_ids': [(6, 0, property_ids)],
        })

    def _assign_active_tag(self, persona, tag):
        return self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': tag.id,
            'date_start': fields.Datetime.now() - timedelta(days=1),
            'date_end': fields.Datetime.now() + timedelta(days=1),
        })

    def test_badge_return_payload_marks_jolly_tags(self):
        persona = self._make_person('Portal Return Jolly')
        jolly_tag = self._make_tag('Portal Jolly Tag', [self.prop_jolly.id])
        tag_persona = self._assign_active_tag(persona, jolly_tag)

        tags = self.controller._get_badge_return_tags(self.env)
        payload = next(tag for tag in tags if tag['id'] == tag_persona.id)

        self.assertEqual(payload['tag_code'], jolly_tag.tag_code)
        self.assertEqual(payload['temp'], False)
        self.assertEqual(payload['is_jolly'], True)

    def test_temp_filter_includes_temporary_and_jolly_tags(self):
        temp_persona = self._make_person('Portal Return Temp')
        jolly_persona = self._make_person('Portal Return Jolly')
        definitive_persona = self._make_person('Portal Return Definitive')

        temp_tag = self._make_tag(
            'Portal Temp Tag',
            [self.prop_temp.id, self.prop_visitor.id],
        )
        jolly_tag = self._make_tag(
            'Portal Jolly Tag Filtered',
            [self.prop_jolly.id],
        )
        definitive_tag = self._make_tag(
            'Portal Definitive Tag Filtered',
            [self.prop_definitive.id],
        )

        temp_tag_persona = self._assign_active_tag(temp_persona, temp_tag)
        jolly_tag_persona = self._assign_active_tag(jolly_persona, jolly_tag)
        definitive_tag_persona = self._assign_active_tag(definitive_persona, definitive_tag)

        tags = self.controller._get_badge_return_tags(self.env, temp_only=True)
        tag_ids = {tag['id'] for tag in tags}

        self.assertIn(temp_tag_persona.id, tag_ids)
        self.assertIn(jolly_tag_persona.id, tag_ids)
        self.assertNotIn(definitive_tag_persona.id, tag_ids)
