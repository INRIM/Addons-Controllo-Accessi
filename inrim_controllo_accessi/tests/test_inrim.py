from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.inrim_controllo_accessi.tests.common import TestCommon
from odoo.exceptions import ValidationError
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
        self.assertTrue(self.punto_accesso_3)

    # Test 4
    def test_4(self):
        """
        Descrizione:
            Utente5 crea in Lettore → Lettore 4 IP:10.10.10.5
        :return: 
            Esiste Lettore 4
        """

        lettore_id = self.env['ca.lettore'].with_user(
            self.user_5).create({
            'name': 'Lettore 4',
            'reader_ip': '10.10.10.5',
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
        lettore_id = self.env['ca.lettore'].with_user(
            self.user_5).create({
            'name': 'Lettore 5',
            'reader_ip': '10.10.10.6',
            'direction': 'out'
        })

        punto_accesso_id = self.env['ca.punto_accesso'].with_user(
            self.user_1).create({
            'ca_spazio_id': self.spazio_8.id,
            'ca_lettore_id': lettore_id.id,
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
        # self.env = self.env(user=self.user_1)
        # self.cr = self.env.cr
        tag_persona_2 = self.env['ca.tag_persona'].with_user(
            self.user_1).create({
            'ca_persona_id': self.persona_1.id,
            'ca_tag_id': self.tag_7.id,
            'date_start': fields.Datetime.today() - timedelta(days=1),
            'date_end': fields.Datetime.today() + relativedelta(days=3)
        })
        self.assertTrue(tag_persona_2)
        tag_persona_3 = self.env['ca.tag_persona'].with_user(
            self.user_1).create({
            'ca_persona_id': self.persona_2.id,
            'ca_tag_id': self.tag_8.id,
            'date_start': fields.Datetime.today() - timedelta(days=1),
            'date_end': fields.Datetime.today() + relativedelta(days=3)
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
        self.assertTrue(self.punto_accesso_2)

        self.punto_accesso_2.commuta_abilitazione()

        # 1
        ca_tag_lettore = self.env['ca.tag_lettore'].with_user(
            self.user_1).search([
            ('ca_lettore_id', "=", self.lettore_2.id),
            ('ca_tag_id', "=", self.tag_8.id),
        ])

        self.assertTrue(self.punto_accesso_2.enable_sync)
        # 5
        tag_persona_id = self.env['ca.tag_persona'].with_user(
            self.user_1).search([
            ('ca_tag_id', '=', self.tag_8.id)
        ])
        self.assertTrue(tag_persona_id.ca_tag_id.id, self.tag_8.id)

        lettore_persona = self.env['ca.lettore_persona'].with_user(
            self.user_1).search([
            ('ca_tag_lettore_id', '=', ca_tag_lettore.id),
            ('ca_tag_persona', '=', tag_persona_id.id)
        ])

        self.assertEqual(lettore_persona.state, 'active')
        # 6
        anag_registro_accesso_id = self.env[
            'ca.anag_registro_accesso'].with_user(
            self.user_1).aggiungi_riga_accesso(
            self.punto_accesso_2, self.tag_persona_1, datetime.now())
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

        self.punto_accesso_1.commuta_abilitazione()
        # 1
        tag_persona = self.env['ca.tag_persona'].with_user(
            self.user_1).create({
            'ca_persona_id': self.persona_3.id,
            'ca_tag_id': self.tag_9.id,
            'date_start': fields.Datetime.today() - timedelta(days=1),
            'date_end': fields.Datetime.today() + relativedelta(days=3)
        })

        self.assertTrue(tag_persona)
        # 2
        self.assertTrue(self.punto_accesso_1.elabora_persone_abilitate())

    def test_9(self):
        """
        Descrizione:
            Credo un punto accesso locale e provo ad attivare un tag senza averlo associato ad una persona

        :return: non viene attivato il tag-lettore
        """
        self.punto_accesso_3.commuta_abilitazione()
        self.assertFalse(self.punto_accesso_3.local_access_attach(self.tag_4))

    def test_90(self):
        """
        Descrizione:
            Credo Tag pesrona -> viene attivato il tag-lettore per l'accesso
            Disattivo la pesrona -> viene disattivato il tag-lettore per l'accesso

        :return:
        """
        # portineria consegns il tag e lo disassocia
        tag_p = self.env['ca.tag_persona'].with_user(
            self.user_1).create({
            'ca_persona_id': self.persona_3.id,
            'ca_tag_id': self.tag_9.id,
            'date_start': fields.Datetime.today() - timedelta(days=1),
            'date_end': fields.Datetime.today() + relativedelta(days=3)
        })
        tag_lettore = self.env['ca.tag_lettore'].search(
            [
                ('ca_tag_id', '=', self.tag_9.id),
                ('ca_lettore_id', "=", self.lettore_3.id)
            ], limit=1)
        self.assertFalse(tag_lettore)
        self.assertTrue(self.punto_accesso_3.local_access_attach(self.tag_9))
        tag_lettore = self.env['ca.tag_lettore'].search(
            [
                ('ca_tag_id', '=', self.tag_9.id),
                ('ca_lettore_id', "=", self.lettore_3.id)
            ], limit=1)
        self.assertTrue(tag_lettore)
        self.assertTrue(self.punto_accesso_3.remote_update)
        # portineria riprende il tag e lo disassocia
        tag_p.set_retuned()
        self.punto_accesso_3.remote_update = False
        self.punto_accesso_3.local_access_detach(self.persona_3)
        self.assertTrue(self.punto_accesso_3.remote_update)
        self.assertFalse(self.punto_accesso_3.local_access_attach(self.tag_9))

    def test_91(self):
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
            self.env['ca.richiesta_riga_accesso_sede'].with_user(
                self.user_1).create(vals)
        )
        with self.assertRaises(ValidationError):
            self.env['ca.richiesta_riga_accesso_sede'].with_user(
                self.user_1).create(vals)
        delta_min_riga_accesso = float(
            self.env[
                'ir.config_parameter'
            ].sudo().get_param('ca.delta_min_riga_accesso', default=0.0)
        )
        self.assertTrue(
            self.env['ca.richiesta_riga_accesso_sede'].with_user(
                self.user_1).create({
                'persona_id': self.persona_1.id,
                'ente_azienda_id': self.ente_azienda_1.id,
                'punto_accesso_id': self.punto_accesso_1.id,
                'direction': 'out',
                'datetime_event': today + timedelta(hours=delta_min_riga_accesso + 0.1)
            })
        )
        with self.assertRaises(ValidationError):
            self.env['ca.richiesta_riga_accesso_sede'].with_user(
                self.user_1).create({
                'persona_id': self.persona_1.id,
                'ente_azienda_id': self.ente_azienda_1.id,
                'punto_accesso_id': self.punto_accesso_1.id,
                'direction': 'out',
                'datetime_event': today + timedelta(hours=delta_min_riga_accesso - 0.1)
            })
