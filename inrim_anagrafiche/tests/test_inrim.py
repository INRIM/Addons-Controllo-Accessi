from odoo.tests import tagged
from odoo.addons.inrim_anagrafiche.tests.common import TestCommon
from odoo.exceptions import AccessError, UserError
import base64
from datetime import date
from dateutil.relativedelta import relativedelta

@tagged("post_install", "-at_install", "inrim")
class TestInrim(TestCommon):

    def test_1(self):
        self.assertTrue(self.user)
        self.assertTrue(self.user_1)
        self.assertTrue(self.user_2)
        self.assertTrue(self.user_3)
        self.assertTrue(self.user_4)
        self.assertTrue(self.user_5)
        self.assertTrue(self.ente_azienda_1)
        self.assertTrue(self.ente_azienda_2)
        self.assertTrue(self.ente_azienda_3)
        self.assertTrue(self.ente_azienda_4)
        self.assertTrue(self.ente_azienda_5)
        self.assertTrue(self.persona_1)
        self.assertTrue(self.persona_2)
        self.assertTrue(self.persona_3)
        self.assertTrue(self.persona_4)
        self.assertTrue(self.persona_5)
        self.assertTrue(self.tag_1)
        self.assertTrue(self.tag_2)
        self.assertTrue(self.tag_3)
        self.assertTrue(self.tag_4)
        self.assertTrue(self.tag_5)
        self.assertTrue(self.tag_6)
        self.assertTrue(self.lettore_1)
        self.assertTrue(self.lettore_2)

    def test_2(self):
        self.env = self.env(user=self.user_2)
        self.cr = self.env.cr
        ca_ente_azienda_id = self.env['ca.ente_azienda'].create({
            'name' : 'Sede 2',
            'pec': 'Pec',
            'tipo_ente_azienda_id': self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            'note': 'Note'
        })
        self.assertTrue(ca_ente_azienda_id)

    def test_3(self):
        self.env = self.env(user=self.user_2)
        self.cr = self.env.cr
        ca_persona_id = self.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '6',
            'fiscalcode': 'Fiscalcode',
            'type_ids': [(6, 0,
                [
                    self.env.ref('inrim_anagrafiche.tipo_persona_esterno').id,
                    self.env.ref('inrim_anagrafiche.tipo_persona_servizi').id
                ]
            )],
            'ca_ente_azienda_ids': [(6, 0, [self.ente_azienda_3.id])],
            'ca_documento_ids': self.env['ca.documento'].create({
                'tipo_documento_id': self.env.ref('inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
                'validity_start_date': date(2024, 1, 1),
                'validity_end_date': date(2024, 3, 31),
                'image_ids': [(6, 0, [
                    self.env['ca.img_documento'].create({
                        'name': 'Fronte',
                        'side': 'fronte',
                        'image': base64.b64encode(b'Fronte Doc Identita')
                    }).id,
                    self.env['ca.img_documento'].create({
                        'name': 'Retro',
                        'side': 'retro',
                        'image': base64.b64encode(b'Retro Doc Identita')
                    }).id
                ])],
                'document_code_id': self.env['ca.codice_documento'].create({
                    'name': 'Codice Doc Persona'
                }).id
            })
        })
        self.assertTrue(ca_persona_id)

    def test_4(self):
        with self.assertRaises(AccessError):
            self.env['ca.persona'].with_user(self.user_3).check_access_rights('write')

    def test_5(self):
        self.assertFalse(self.tag_2.in_use)

    def test_6(self):
        self.env = self.env(user=self.user_4)
        self.cr = self.env.cr
        ca_tag_persona_id = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_5.id,
            'ca_tag_id': self.tag_2.id,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days = 3)
        })
        ca_tag_persona_id._onchange_date()
        self.assertTrue(ca_tag_persona_id and ca_tag_persona_id.ca_tag_id.in_use)

    def test_7(self):
        self.env = self.env(user=self.user_4)
        self.cr = self.env.cr
        ca_tag_persona_id = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_5.id,
            'ca_tag_id': self.tag_2.id,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days = 3)
        })
        ca_tag_persona_id._onchange_date()
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_5.id,
                'ca_tag_id': self.tag_2.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days = 2)
            })

    def test_8(self):
        self.env = self.env(user=self.user_4)
        self.cr = self.env.cr
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_5.id,
                'ca_tag_id': self.tag_6.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days = 2)
            })

    def test_9(self):
        self.env = self.env(user=self.user_4)
        self.cr = self.env.cr
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_3.id,
                'ca_tag_id': self.tag_3.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days = 2)
            })