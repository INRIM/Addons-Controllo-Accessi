from datetime import date
from unittest.mock import patch
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "inrim")
class TestCoreTagPersona(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_internal = cls.env.ref('inrim_anagrafiche.tipo_persona_interno')
        cls.prop_definitive = cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo')
        cls.prop_jolly = cls.env.ref('inrim_anagrafiche.proprieta_tag_jolly')
        cls.tipo_ente_azienda = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        cls.tipo_spazio = cls.env.ref('inrim_anagrafiche.tipo_spazio_locale')
        cls.ente_azienda = cls.env['ca.ente_azienda'].create({
            'name': 'Portal Core Test HQ',
            'tipo_ente_azienda_id': cls.tipo_ente_azienda.id,
            'company_id': cls.env.company.id,
            'tz': 'Europe/Rome',
        })
        cls.space = cls.env['ca.spazio'].create({
            'name': 'Portal Core Test Space',
            'tipo_spazio_id': cls.tipo_spazio.id,
            'ente_azienda_id': cls.ente_azienda.id,
        })

    def _make_tag(self, label):
        return self.env['ca.tag'].create({
            'name': label,
            'tag_code': uuid4().hex[:16].upper(),
            'ca_proprieta_tag_ids': [(6, 0, [self.prop_definitive.id])],
        })

    def _make_person(self, label):
        return self.env['ca.persona'].create({
            'name': label,
            'lastname': label,
            'type_ids': [(6, 0, [self.type_internal.id])],
        })

    def test_scheduled_tag_persona_becomes_to_give_back(self):
        persona = self._make_person('Core Future Person')
        tag = self._make_tag('Core Future Tag')
        future_start = fields.Datetime.now() + relativedelta(minutes=10)
        future_end = future_start + relativedelta(days=1)

        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': tag.id,
            'date_start': future_start,
            'date_end': future_end,
        })

        self.assertEqual(tag_persona.state, 'scheduled')

        with patch(
            'odoo.addons.inrim_anagrafiche.models.ca_tag_persona.fields.Datetime.now',
            return_value=future_start + relativedelta(minutes=1),
        ):
            tag_persona.check_update_record_by_date_valididty()

        self.assertEqual(tag_persona.state, 'to_give_back')

    def test_scheduled_tag_persona_syncs_enabled_stamping_access_point(self):
        persona = self._make_person('Core Sync Person')
        tag = self._make_tag('Core Sync Tag')
        lettore = self.env['ca.lettore'].create({
            'name': 'Portal Core Scheduled Sync',
            'reader_ip': '10.10.10.25',
            'direction': 'in',
        })
        access_point = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.space.id,
            'ca_lettore_id': lettore.id,
            'typology': 'stamping',
            'enable_sync': True,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30),
        })

        future_start = fields.Datetime.now() + relativedelta(minutes=10)
        future_end = future_start + relativedelta(days=1)
        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': tag.id,
            'date_start': future_start,
            'date_end': future_end,
        })

        self.assertEqual(tag_persona.state, 'scheduled')
        self.assertFalse(self.env['ca.tag_lettore'].search([
            ('ca_lettore_id', '=', lettore.id),
            ('ca_tag_id', '=', tag.id),
            ('ca_punto_accesso_id', '=', access_point.id),
        ], limit=1))

        future_now = future_start + relativedelta(minutes=1)
        with patch(
            'odoo.addons.inrim_anagrafiche.models.ca_tag_persona.fields.Datetime.now',
            return_value=future_now,
        ), patch(
            'odoo.addons.inrim_controllo_accessi.models.ca_lettore_persona.fields.Datetime.now',
            return_value=future_now,
        ):
            tag_persona.check_update_record_by_date_valididty()

        self.assertEqual(tag_persona.state, 'to_give_back')

        tag_lettore = self.env['ca.tag_lettore'].search([
            ('ca_lettore_id', '=', lettore.id),
            ('ca_tag_id', '=', tag.id),
            ('ca_punto_accesso_id', '=', access_point.id),
        ], limit=1)
        self.assertTrue(tag_lettore)
        self.assertEqual(tag_lettore.state, 'active')

        lettore_persona = self.env['ca.lettore_persona'].search([
            ('ca_tag_lettore_id', '=', tag_lettore.id),
            ('ca_tag_persona', '=', tag_persona.id),
        ], limit=1)
        self.assertTrue(lettore_persona)
        self.assertEqual(lettore_persona.state, 'active')

    def test_return_jolly_badge_marks_tag_as_available(self):
        persona = self._make_person('Core Return Jolly Person')
        lettore = self.env['ca.lettore'].create({
            'name': 'Core Return Jolly Stamping Reader',
            'reader_ip': '10.10.10.26',
            'direction': 'in',
        })
        self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.space.id,
            'ca_lettore_id': lettore.id,
            'typology': 'stamping',
            'enable_sync': True,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30),
        })
        jolly_tag = self.env['ca.tag'].create({
            'name': 'Core Return Jolly Tag',
            'tag_code': uuid4().hex[:16].upper(),
            'ca_proprieta_tag_ids': [(6, 0, [self.prop_jolly.id])],
        })
        active_start = fields.Datetime.now() - relativedelta(days=1)
        active_end = fields.Datetime.now() + relativedelta(days=1)
        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': persona.id,
            'ca_tag_id': jolly_tag.id,
            'date_start': active_start,
            'date_end': active_end,
        })

        self.assertTrue(jolly_tag.in_use)
        self.assertEqual(tag_persona.state, 'to_give_back')

        returned_at = fields.Datetime.now()
        with patch(
            'odoo.addons.inrim_anagrafiche.models.ca_tag_persona.fields.Datetime.now',
            return_value=returned_at,
        ):
            wizard = self.env['ca.restituisci_badge'].create({
                'ca_tag_id': tag_persona.id,
            })
            wizard.action_confirm()

        tag_persona = self.env['ca.tag_persona'].with_context(
            active_test=False,
        ).browse(tag_persona.id)
        jolly_tag.invalidate_recordset()

        self.assertEqual(tag_persona.state, 'returned')
        self.assertFalse(tag_persona.active)
        self.assertFalse(jolly_tag.in_use)
        self.assertFalse(
            self.env['ca.tag_persona'].search([
                ('id', '=', tag_persona.id),
                ('state', '=', 'to_give_back'),
            ], limit=1)
        )
        self.assertTrue(
            self.env['ca.tag'].search([
                ('id', '=', jolly_tag.id),
                ('in_use', '=', False),
                ('revoked', '=', False),
            ], limit=1)
        )
