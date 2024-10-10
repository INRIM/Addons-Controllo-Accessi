from odoo.addons.inrim_controllo_accessi_custom.tests.common import TestCommon
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
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
        self.assertTrue(self.tipo_ente_azienda_1)
        self.assertTrue(self.tipo_ente_azienda_2)
        self.assertTrue(self.user_5)
        self.assertTrue(self.persona_1)
        self.assertTrue(self.ente_azienda_1)
        self.assertTrue(self.punto_accesso_1)

    # Test 2
    def test_2(self):
        """
        Descrizione:
            Verifica che alla creazione di un ca.ente_azienda con tipo Sede si valorizzino i campi jwt e url_gateway_lettori se non popolati

        :return: I campi si popolano correttamente
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        vals = {
            'name': 'Test',
            'pec': 'Test PEC',
            'tipo_ente_azienda_id': self.tipo_ente_azienda_1.id
        }
        ente_azienda_id = self.env['ca.ente_azienda'].create(vals)
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'name': 'Test 1'
        })
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)

    # Test 3
    def test_3(self):
        """
        Descrizione:
            Verifica che alla modifica di un ca.ente_azienda con tipo Sede si valorizzino i campi jwt e url_gateway_lettori se non popolati

        :return: I campi si popolano correttamente
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        vals = {
            'name': 'Test',
            'pec': 'Test PEC',
            'tipo_ente_azienda_id': self.tipo_ente_azienda_2.id
        }
        ente_azienda_id = self.env['ca.ente_azienda'].create(vals)
        self.assertFalse(ente_azienda_id.jwt)
        self.assertFalse(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'name': 'Test 2'
        })
        self.assertFalse(ente_azienda_id.jwt)
        self.assertFalse(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'tipo_ente_azienda_id': self.tipo_ente_azienda_1.id
        })
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)

    # Test 4
    def test_4(self):
        """
        Descrizione:
            Verifica che non si possano aggiungere 2 ingressi nello stesso giorno con differenza inferiore a ca.delta_min_riga_accesso

        :return: Se vengono inseriti 2 ingressi nello stesso giorno scatta la constrains
        """
        today = datetime.now()
        vals = {
            'persona_id': self.persona_1.id,
            'ente_azienda_id': self.ente_azienda_1.id,
            'punto_accesso_id': self.punto_accesso_1.id,
            'direction': 'out',
            'datetime_event': today
        }
        self.assertTrue(
            self.env['ca.richiesta_riga_accesso_sede'].create(vals)
        )
        with self.assertRaises(ValidationError):
            self.env['ca.richiesta_riga_accesso_sede'].create(vals)
        delta_min_riga_accesso = float(
            self.env[
                'ir.config_parameter'
            ].sudo().get_param('ca.delta_min_riga_accesso', default=0.0)
        )
        self.assertTrue(
            self.env['ca.richiesta_riga_accesso_sede'].create({
                'persona_id': self.persona_1.id,
                'ente_azienda_id': self.ente_azienda_1.id,
                'punto_accesso_id': self.punto_accesso_1.id,
                'direction': 'out',
                'datetime_event': today + timedelta(hours=delta_min_riga_accesso + 0.1)
            })
        )
        with self.assertRaises(ValidationError):
            self.env['ca.richiesta_riga_accesso_sede'].create({
                'persona_id': self.persona_1.id,
                'ente_azienda_id': self.ente_azienda_1.id,
                'punto_accesso_id': self.punto_accesso_1.id,
                'direction': 'out',
                'datetime_event': today + timedelta(hours=delta_min_riga_accesso - 0.1)
            })