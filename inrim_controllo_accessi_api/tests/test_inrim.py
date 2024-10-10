from odoo.addons.inrim_controllo_accessi_api.tests.common import TestCommon
from odoo.tests import tagged

@tagged("post_install", "-at_install", "inrim")
class ApiTestCommon(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che i parametri di sistema per la connessione a people siano valorizzati

        :return: I dati nei parametri di sistema esistono e sono valorizzati
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
            user_id = self.env['res.users'].search([
                ('login', '=', dt['uid'])
            ])
            if user_id:
                user_id.unlink()
                user_id = False
            persona_id = self.env['ca.persona'].search([
                ('freshman', '=', dt['matricola']),
                ('fiscalcode', '=', dt['codicefiscale'])
            ])
            if persona_id:
                persona_id.unlink()
                persona_id = False
            self.assertFalse(persona_id)
            self.assertFalse(user_id)
            self.env['ca.persona'].get_addressbook_data(data)
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
            spazio_id = self.env['ca.spazio'].search([
                ('name', '=', dt['name'])
            ], limit=1)
            if spazio_id:
                punto_accesso_id = self.env['ca.punto_accesso'].search([
                    ('ca_spazio_id', '=', spazio_id.id)
                ])
                if punto_accesso_id:
                    punto_accesso_id.unlink()
                spazio_id.unlink()
                spazio_id = False
            self.assertFalse(spazio_id)
            self.env['ca.spazio'].get_rooms_data(data)
            spazio_id = self.env['ca.spazio'].search([
                ('name', '=', dt['name']),
                ('tipo_spazio_id.name', '=', dt['type_name']),
                ('ente_azienda_id.ref', '=', dt['institution_address_ref'])
            ], limit=1)
            if dt.get('institution_address_ref') and dt.get('type_name'):
                self.assertTrue(spazio_id)
                self.assertEqual(spazio_id.tipo_spazio_id.name, dt['type_name'])
                self.assertEqual(spazio_id.ente_azienda_id.ref, dt['institution_address_ref'])