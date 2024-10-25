from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo.addons.inrim_controllo_accessi.tests.common import TestCommon
from odoo.exceptions import UserError,ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class TestInrim(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che tutti i models in Dati per Test abbiano i dati

        :return: 
            Corrispondenza dei dati per numero di record alla search
        """
        self.assertTrue(self.user)
        self.assertTrue(self.user_1)
        self.assertTrue(self.user_2)
        self.assertTrue(self.user_3)
        self.assertTrue(self.user_4)
        self.assertTrue(self.user_5)
        self.assertTrue(self.spazio_1)
        self.assertTrue(self.spazio_2)
        self.assertTrue(self.spazio_3)
        self.assertTrue(self.spazio_4)
        self.assertTrue(self.spazio_5)
        self.assertTrue(self.spazio_6)
        self.assertTrue(self.spazio_7)
        self.assertTrue(self.spazio_8)
        self.assertTrue(self.lettore_1)
        self.assertTrue(self.lettore_2)
        self.assertTrue(self.lettore_3)
        self.assertTrue(self.persona_1)
        self.assertTrue(self.persona_2)
        self.assertTrue(self.persona_3)
        self.assertTrue(self.persona_4)
        self.assertTrue(self.persona_5)
        self.assertTrue(self.persona_6)
        self.assertTrue(self.tag_1)
        self.assertTrue(self.tag_2)
        self.assertTrue(self.tag_3)
        self.assertTrue(self.tag_4)
        self.assertTrue(self.tag_5)
        self.assertTrue(self.tag_6)
        self.assertTrue(self.tag_7)
        self.assertTrue(self.tag_8)
        self.assertTrue(self.tag_9)
        self.assertTrue(self.tag_persona_1)
        self.assertTrue(self.punto_accesso_1)
        self.assertTrue(self.punto_accesso_2)

    # Test 2
    def test_2(self):
        """
        Descrizione:
            Utente5 crea record tipo_spazio Virtuale
        :return: 
            Esiste Virtuale in ente tipo_spazio
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        tipo_spazio_id = self.env['ca.tipo_spazio'].create({
            'name': 'Virtuale'
        })
        self.assertTrue(tipo_spazio_id)

    # Test 3
    def test_3(self):
        """
        Descrizione:
            Utente1 crea un record Servizio di tipo:servizio test
        :return: 
            Errore utente non abilitato
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        with self.assertRaises(Exception):
            self.env['ca.anag_servizi'].create({
                'name': 'Servizio Test',
                'spazio_id': self.spazio_1.id
            })

    # Test 4
    def test_4(self):
        """
        Descrizione:
            Utente5 crea in Lettore → Lettore 3 IP:10.10.10.4
        :return: 
            Esiste Lettore 3
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        lettore_id = self.env['ca.lettore'].create({
            'name': 'Lettore 3',
            'reader_ip': '10.10.10.4',
            'direction': 'in'
        })
        self.assertTrue(lettore_id)

    # Test 5
    def test_5(self):
        """
        Descrizione:
            Utente1 crea un record Punto Accesso: Lettore 3 ingresso nel 1p006
        :return: 
            Esiste il nuovo punto di accesso
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        punto_accesso_id = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.spazio_8.id,
            'ca_lettore_id': self.lettore_3.id,
            'typology': 'stamping',
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30)
        })
        self.assertTrue(punto_accesso_id)

    # Test 6
    def test_6(self):
        """
        Descrizione:
            Utente1 crea Tag Persona collegando:
                Persona 1 e Tag 7 , inizio ieri fine oggi + 3gg
                Persona 2 e Tag 8 , inizio ieri fine oggi + 3gg
        :return: 
            Esistono i nuovi record validi
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        tag_persona_2 = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_1.id,
            'ca_tag_id': self.tag_7.id,
            'date_start': date.today() - timedelta(days=1),
            'date_end': date.today() + relativedelta(days=3)
        })
        self.assertTrue(tag_persona_2)
        tag_persona_3 = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_2.id,
            'ca_tag_id': self.tag_8.id,
            'date_start': date.today() - timedelta(days=1),
            'date_end': date.today() + relativedelta(days=3)
        })
        self.assertTrue(tag_persona_3)

    # Test 7
    def test_7(self):
        """
        Descrizione:
            1. Utente1: Aggiunge Punto Accesso → ingresso sede | Campus, Lettore 3, Timbratura, Abilitato=False |
            2. Utente1: Esegue aggiungi_riga_accesso: Tag 7, ingresso sede
            3. Utente4: Esegue aggiungi_riga_accesso
            4. Utente1: Esegue il metodo commuta_abilitazione
            5. Utente1: Esegue il metodo Punto_Accesso.elabora_persone_abilitate
            6. Utente4: Esegue aggiungi_riga_accesso:Tag 7, ingresso sede
        :return: 
            1. Esiste il record
            2. Errore utente non abilitato
            3. Errore punto accesso non attivo
            4. Il punto accesso e’ attivo
            5. Si aggiornano i record in Lettore Persona
            6. E’ presente la timbratura in Registro Accesso
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        # 1
        ca_tag_lettore = self.env['ca.tag_lettore'].create({
            'ca_lettore_id': self.lettore_3.id,
            'ca_tag_id': self.tag_8.id,
            'date_start': date.today() - timedelta(days=1),
            'date_end': date.today() + relativedelta(days=3)
        })
        punto_accesso_id = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.spazio_3.id,
            'ca_lettore_id': self.lettore_3.id,
            'typology': 'stamping',
            'enable_sync': False,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30),
            'ca_tag_lettore_ids': [(6, 0, [ca_tag_lettore.id])]
        })
        tag_persona_id = self.env['ca.tag_persona'].search([
            ('ca_tag_id', '=', ca_tag_lettore.ca_tag_id.id)
        ])
        self.env['ca.punto_accesso_persona'].create({
            'ca_tag_lettore_id': ca_tag_lettore.id,
            'ca_tag_persona': tag_persona_id.id,
            'date': date.today(),
            'state': 'active'
        })
        self.assertTrue(punto_accesso_id)

        # - Commentati da Alessio Gerace 23-10-2024
        #
        # with self.assertRaises(UserError):
        #     self.env['ca.anag_registro_accesso'].aggiungi_riga_accesso(
        #         punto_accesso_id, self.tag_persona_1, datetime.now())
        # # 3
        # self.env = self.env(user=self.user_4)
        # self.cr = self.env.cr
        # with self.assertRaises(UserError):
        #     self.env['ca.anag_registro_accesso'].aggiungi_riga_accesso(
        #         punto_accesso_id, self.tag_persona_1, datetime.now())
        #
        # - Commentati da Alessio Gerace 23-10-2024

        # 4
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        punto_accesso_id.commuta_abilitazione()
        self.assertTrue(punto_accesso_id.enable_sync)
        # 5
        punto_accesso_persona = self.env['ca.punto_accesso_persona'].search([
            ('ca_tag_lettore_id', '=', ca_tag_lettore.id),
            ('ca_tag_persona', '=', tag_persona_id.id)
        ])
        self.assertEqual(punto_accesso_persona.state, 'active')
        punto_accesso_id.elabora_persone_abilitate()
        self.assertEqual(punto_accesso_persona.state, 'active')
        # 6
        self.env = self.env(user=self.user_4)
        self.cr = self.env.cr
        anag_registro_accesso_id = self.env[
            'ca.anag_registro_accesso'].aggiungi_riga_accesso(
            punto_accesso_id, self.tag_persona_1, datetime.now())
        self.assertTrue(anag_registro_accesso_id)

    # Test 8
    def test_8(self):
        """
        Descrizione:
            1. Utente1 crea Tag Persona collegando Persona 3 e Tag 9 , inizio ieri fine oggi + 3gg
            2. Utente1: esegue il metodo Lettore_Persona.elabora_persone_abilitate
        :return: 
            1. Esiste il nuovo record
            2. Si aggiornano i record in Lettore Persona
        """
        self.env = self.env(user=self.user_1)
        self.cr = self.env.cr
        # 1
        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_3.id,
            'ca_tag_id': self.tag_9.id,
            'date_start': date.today() - timedelta(days=1),
            'date_end': date.today() + relativedelta(days=3)
        })
        self.assertTrue(tag_persona)
        # 2
        self.assertFalse(self.punto_accesso_1.elabora_persone_abilitate())


    def test_9(self):
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
