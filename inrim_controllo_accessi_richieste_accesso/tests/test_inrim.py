from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo.addons.inrim_controllo_accessi_richieste_accesso.tests.common import TestCommon
from odoo.exceptions import ValidationError
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
        self.assertTrue(self.persona_1)
        self.assertTrue(self.persona_2)
        self.assertTrue(self.persona_3)
        self.assertTrue(self.persona_4)
        self.assertTrue(self.persona_5)
        self.assertTrue(self.persona_6)
        self.assertTrue(self.anag_tipologie_istanze_1)
        self.assertTrue(self.anag_tipologie_istanze_2)
        self.assertTrue(self.anag_tipologie_istanze_3)
        self.assertTrue(self.anag_tipologie_istanze_4)
        self.assertTrue(self.anag_tipologie_istanze_5)
        self.assertTrue(self.anag_tipologie_istanze_6)
        self.assertTrue(self.anag_tipologie_istanze_7)
        self.assertTrue(self.anag_tipologie_istanze_8)
        self.assertTrue(self.richiesta_accesso_persona_1)
        self.assertTrue(self.richiesta_accesso_1)

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

    # Test 9
    def test_5(self):
        """
        Descrizione:
            Utente1 crea un record Richiesta Persona,
            per Persona 3 data inizio 1 mese prima,
            data fine 5 gg da data esecuzione → Richiesta Accesso
            Persona 3
        :return:
            Esiste il nuovo Record, stato=nuova
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        richiesta_accesso_persona_id = self.env[
            'ca.richiesta_accesso_persona'
        ].create({
            'anag_tipologie_istanze_id': self.anag_tipologie_istanze_1.id,
            'ca_persona_id': self.persona_2.id,
            'act_application_code': 'Richiesta Accesso Persona',
            'date_start': (date.today() - relativedelta(months=1)),
            'date_end': date.today() + relativedelta(days=5),
            'persona_id': self.persona_3.id
        })
        self.assertTrue(richiesta_accesso_persona_id.state == 'new')

    # Test 6
    def test_6(self):
        """
        Descrizione:
            Utente1 crea un record Richiesta Servizio Persona,
            vpn per Richiesta Persona 3 data inizio 1 mese prima,
            data fine 5 gg da data esecuzione , per Persona 1 e Persona 2,
            senza servizi aggiuntivi → Richiesta Accesso 1
        :return:
            Esiste il nuovo Record, stato=nuova
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        richiesta_servizi_persona_id = self.env[
            'ca.richiesta_servizi_persona'
        ].create({
            'ca_richiesta_accesso_persona_id': self.richiesta_accesso_persona_1.id,
            'ca_anag_tipologie_istanze_id': self.anag_tipologie_istanze_2.id,
            'date_start': (date.today() - relativedelta(months=1)),
            'date_end': date.today() + relativedelta(days=5),
            'ca_persona_id': self.persona_1.id,
            'persona_id': self.persona_2.id
        })
        self.assertTrue(richiesta_servizi_persona_id.state == 'new')

    # Test 7
    def test_7(self):
        """
        Descrizione:
            Utente1 imposta Richiesta Accesso Persona 3 approvata
        :return:
            Il record passa in stato approvata, con flag in scadenza a True
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        self.richiesta_accesso_persona_1.with_user(
            self.user_1).aggiorna_stato_richiesta('approved')
        self.assertTrue(self.richiesta_accesso_persona_1.state == 'approved')
        self.assertTrue(self.richiesta_accesso_persona_1.expiring)

    # Test 8
    def test_8(self):
        """
        Descrizione:
            Utente2 imposta Richiesta Accesso 1 approvata
        :return:
            Il record e le righe richiesta persona, passano
            ad approvata, con flag in scadenza a True
        """
        self.env = self.env(user=self.user_2)
        self.cr = self.env.cr
        self.richiesta_accesso_1.with_user(
            self.user_2).aggiorna_stato_richiesta('approved')
        self.assertTrue(self.richiesta_accesso_1.state == 'approved')
        self.assertTrue(self.richiesta_accesso_1.expiring)
        self.assertTrue(self.richiesta_accesso_1.
                        ca_richiesta_accesso_persona_ids[0].state == 'approved')
        self.assertTrue(self.richiesta_accesso_1.
                        ca_richiesta_accesso_persona_ids[0].expiring)
