import base64
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo.addons.inrim_anagrafiche.tests.common import TestCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class TestInrim(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che tutti i models in Dati per Test abbiano i dati

        :return:  Corrispondenza dei dati per numero di record alla search
        """

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

    # Test 2
    def test_2(self):
        """
         Utente1 crea una Sede 2
        :return: Esiste Sede 2 in ente azienda
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        ca_ente_azienda_id = self.env['ca.ente_azienda'].create({
            'name': 'Sede 2',
            'pec': 'Pec',
            'tipo_ente_azienda_id': self.env.ref(
                'inrim_anagrafiche.tipo_ente_azienda_sede').id,
            'note': 'Note'
        })
        self.assertTrue(ca_ente_azienda_id)

    # Test 3
    def test_3(self):
        """
        Utente1 crea un record Persona 6 di tipo:
        esterno, servizi, collegato ad Azienda Test con doc identita’

        :return: Esiste il record Persona 6 stato Completata
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        ca_persona_id = self.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '6',
            'fiscalcode': 'Fiscalcode1',
            'type_ids': [(6, 0,
                          [
                              self.env.ref(
                                  'inrim_anagrafiche.tipo_persona_esterno').id,
                              self.env.ref(
                                  'inrim_anagrafiche.tipo_persona_servizi').id
                          ]
                          )],
            'ca_ente_azienda_ids': [(6, 0, [self.ente_azienda_3.id])],
            'ca_documento_ids': self.env['ca.documento'].create({
                'tipo_documento_id': self.env.ref(
                    'inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
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

    # Test 4
    def test_4(self):
        """
         Utente3 modifica Persona 6

        :return: Utente3 modifica con successo persona 6
        """
        self.assertFalse(
            self.env['ca.persona'].with_user(self.user_3).check_access_rights(
                'write'))

    # Test 5
    def test_5(self):
        """
        Tag 2 in Tag → “in Uso” e’ False
        :return: Vero
        """
        self.assertFalse(self.tag_2.in_use)

    # Test 6
    def test_6(self):
        """
        Utente1 crea un record Tag Persona collegando Persona
        6 a Tag 2 , inizio oggi fine oggi + 3gg

        :return: Esiste il nuovo Record Tag 2 in Tag → “in Uso” True
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        ca_tag_persona_id = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_6.id,
            'ca_tag_id': self.tag_2.id,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=3)
        })
        self.assertTrue(
            ca_tag_persona_id and ca_tag_persona_id.ca_tag_id.in_use)

    # Test 7
    def test_7(self):
        """
        Utente1 crea un record Tag Persona collegando Persona
        6 a Tag 2 , inizio oggi fine oggi +2

        :return: Errore:” Tag 2 gia in uso nel periodo”
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_6.id,
            'ca_tag_id': self.tag_2.id,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=3)
        })
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_6.id,
                'ca_tag_id': self.tag_2.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days=2)
            })

    # Test 8
    def test_8(self):
        """
        Utente1 crea un record Tag Persona collegando Persona
        6 a Tag 6 , inizio oggi fine oggi +2

        :return: Errore: "Tag 6 risulta revocato"
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_6.id,
                'ca_tag_id': self.tag_6.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days=2)
            })

    # Test 9
    def test_9(self):
        """
        Utente1 crea un record Tag Persona collegando Persona
        6 a Tag 3 , inizio oggi fine oggi +2

        :return: Errore: "Tag 3; ad un esterno possono essere
        assegnati solo Tag di Tipo Temporaneo"
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        with self.assertRaises(UserError):
            self.env['ca.tag_persona'].create({
                'ca_persona_id': self.persona_6.id,
                'ca_tag_id': self.tag_3.id,
                'date_start': date.today(),
                'date_end': date.today() + relativedelta(days=2)
            })
