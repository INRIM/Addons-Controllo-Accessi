from odoo.addons.controllo_accessi_inrim_app.tests.common import TestCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class CustomTestCommon(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica la presenza dei dati per i test

        :return: I dati per i test esistono
        """

        self.assertTrue(self.people_key)
        self.assertTrue(self.people_url)
        self.assertTrue(self.get_addressbook_data)
        self.assertTrue(self.get_rooms_data)

    # Test 2
    def test_2(self):
        """
        Descrizione:
            Verifica che il metodo get_addressbook_data crei gli utente le persone

        :return: Gli utenti e le persone vengono create correttamente
        """
        data = self.get_addressbook_data
        for dt in data:
            self.env['ca.persona'].get_addressbook_data([dt])
            user_id = self.env['res.users'].search([
                ('login', '=', dt['uid'])
            ])
            persona_id = self.env['ca.persona'].search([
                ('freshman', '=', dt['matricola']),
                ('fiscalcode', '=', dt['codicefiscale'])
            ])
            self.assertTrue(persona_id)
            self.assertEqual(persona_id.associated_user_id, user_id)
            self.assertEqual(persona_id.fiscalcode, dt['codicefiscale'])
            self.assertEqual(persona_id.freshman, dt['matricola'])
            self.assertTrue(user_id)
            self.assertEqual(user_id.name, dt['name'])
            self.assertEqual(user_id.login, dt['uid'])

    # Test 3
    def test_3(self):
        """
        Descrizione:
            Verifica che il metodo get_rooms_data crei i record di spazio

        :return: I record di spazio vengono creati correttamente
        """
        data = self.get_rooms_data
        for dt in data:
            self.env['ca.spazio'].get_rooms_data([dt])
            spazio_id = self.env['ca.spazio'].search([
                ('name', '=', dt['name']),
                ('tipo_spazio_id.name', '=', dt['type_name']
            )
            ], limit=1)
            self.assertTrue(spazio_id)
            self.assertEqual(spazio_id.tipo_spazio_id.name, dt['type_name'])
