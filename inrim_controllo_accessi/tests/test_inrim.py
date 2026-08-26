import base64
import csv
import io

from datetime import date, datetime, timedelta
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.inrim_controllo_accessi.tests.common import TestCommon
from odoo.exceptions import UserError, ValidationError
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
            self.user_5).create({
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

        self.assertEqual(ca_tag_lettore.state, 'active')

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
        # portineria consegna il tag e lo disassocia
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
        self.punto_accesso_3.remote_update = False
        self.punto_accesso_3.local_access_detach(tag_p)
        tag_p.set_retuned()
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

    def test_92(self):
        """
        Un tag persona schedulato, quando entra in validita', viene
        promosso a to_give_back e sincronizzato sui punti accesso attivi.
        """
        lettore_id = self.env['ca.lettore'].with_user(
            self.user_5).create({
            'name': 'Lettore Scheduled Sync',
            'reader_ip': '10.10.10.15',
            'direction': 'in'
        })

        punto_accesso_id = self.env['ca.punto_accesso'].with_user(
            self.user_5).create({
            'ca_spazio_id': self.spazio_7.id,
            'ca_lettore_id': lettore_id.id,
            'typology': 'stamping',
            'enable_sync': True,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30)
        })

        future_start = fields.Datetime.now() + relativedelta(minutes=10)
        future_end = future_start + relativedelta(days=1)
        tag_persona = self.env['ca.tag_persona'].with_user(
            self.user_1).create({
            'ca_persona_id': self.persona_3.id,
            'ca_tag_id': self.tag_9.id,
            'date_start': future_start,
            'date_end': future_end,
        })

        self.assertEqual(tag_persona.state, 'scheduled')
        self.assertFalse(self.env['ca.tag_lettore'].search([
            ('ca_lettore_id', '=', lettore_id.id),
            ('ca_tag_id', '=', self.tag_9.id),
            ('ca_punto_accesso_id', '=', punto_accesso_id.id),
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
            ('ca_lettore_id', '=', lettore_id.id),
            ('ca_tag_id', '=', self.tag_9.id),
            ('ca_punto_accesso_id', '=', punto_accesso_id.id),
        ], limit=1)
        self.assertTrue(tag_lettore)
        self.assertEqual(tag_lettore.state, 'active')

        lettore_persona = self.env['ca.lettore_persona'].search([
            ('ca_tag_lettore_id', '=', tag_lettore.id),
            ('ca_tag_persona', '=', tag_persona.id),
        ], limit=1)
        self.assertTrue(lettore_persona)
        self.assertEqual(lettore_persona.state, 'active')

    # Test 93
    def test_93(self):
        """
        Descrizione:
            Wizard badge generico: la creazione scrive il tag su tutti i
            punti accesso di timbratura

        :return:
            Un ca.tag_lettore attivo per ogni punto accesso stamping
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visiting')
        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'Visiting 01',
            'tag_code': 'e00101500000ba01',
        })
        wizard.action_confirm()

        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BA01')], limit=1)
        self.assertTrue(tag)
        self.assertFalse(tag.revoked)
        self.assertIn(tipo_badge.ca_proprieta_tag_id, tag.ca_proprieta_tag_ids)
        self.assertIn(
            self.env.ref('inrim_anagrafiche.proprieta_tag_valido'),
            tag.ca_proprieta_tag_ids)

        access_points = self.env['ca.punto_accesso'].search([
            ('typology', '=', 'stamping')])
        self.assertTrue(access_points)
        for access_point in access_points:
            tag_lettore = self.env['ca.tag_lettore'].search([
                ('ca_tag_id', '=', tag.id),
                ('ca_punto_accesso_id', '=', access_point.id),
            ], limit=1)
            self.assertTrue(tag_lettore)
            self.assertTrue(access_point.remote_update)

    # Test 94
    def test_94(self):
        """
        Descrizione:
            Wizard badge generico: la revoca marca il tag come Revocato e
            rimuove il collegamento tag_lettore da ogni punto accesso

        :return:
            Tag revocato e nessun ca.tag_lettore attivo
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_support_staff')
        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'Support Staff 01',
            'tag_code': 'e00101500000ba02',
        })
        wizard.action_confirm()
        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BA02')], limit=1)
        self.assertTrue(tag)

        revoke_wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'revoke',
            'ca_tag_id': tag.id,
        })
        self.assertIn(tag, revoke_wizard.revocable_tag_ids)
        revoke_wizard.action_confirm()

        self.assertTrue(tag.revoked)
        self.assertNotIn(
            self.env.ref('inrim_anagrafiche.proprieta_tag_valido'),
            tag.ca_proprieta_tag_ids)
        self.assertFalse(tag.in_use)
        self.assertFalse(self.env['ca.tag_lettore'].search([
            ('ca_tag_id', '=', tag.id)]))
        for tag_lettore in self.env['ca.tag_lettore'].with_context(
                active_test=False).search([('ca_tag_id', '=', tag.id)]):
            self.assertEqual(tag_lettore.state, 'expired')

    # Test 95
    def test_95(self):
        """
        Descrizione:
            Un badge generico e' selezionabile nel wizard di registrazione
            persona esterna

        :return:
            Il tag generico compare tra i tag disponibili
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_external_contractor')
        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'External Contractor 01',
            'tag_code': 'e00101500000ba03',
        })
        wizard.action_confirm()
        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BA03')], limit=1)

        titolo_esterno = self.env['ca.titolo_persona'].search([
            ('structured', '=', False)], limit=1)
        if not titolo_esterno:
            titolo_esterno = self.env['ca.titolo_persona'].create({
                'name': 'Esterno Test',
                'code': 'EXT_TEST',
                'structured': False,
            })
        registra = self.env['ca.registra_persona'].new({
            'ca_title_id': titolo_esterno.id,
        })
        registra.compute_available_tags()
        # il wizard e' un record virtuale: i tag disponibili sono NewId
        self.assertIn(tag.id, registra.available_tags_ids._origin.ids)

    # Test 96
    def test_96(self):
        """
        Descrizione:
            Wizard badge generico: la revoca di un badge attualmente in uso
            chiude il tag_persona, le abilitazioni lettore_persona e revoca
            il tag

        :return:
            Tag persona restituito, nessuna abilitazione attiva, tag revocato
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visitatore')
        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'Visitatore 01',
            'tag_code': 'e00101500000ba04',
        })
        wizard.action_confirm()
        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BA04')], limit=1)
        self.assertTrue(tag)

        tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.persona_5.id,
            'ca_tag_id': tag.id,
            'date_start': fields.Datetime.now() - timedelta(days=1),
            'date_end': fields.Datetime.now() + relativedelta(days=3),
        })
        self.assertEqual(tag_persona.state, 'to_give_back')
        self.assertTrue(tag.in_use)

        revoke_wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'revoke',
            'ca_tag_id': tag.id,
        })
        revoke_wizard._onchange_ca_tag_id()
        self.assertEqual(revoke_wizard.ca_persona_id, self.persona_5)
        revoke_wizard.action_confirm()

        self.assertEqual(tag_persona.state, 'returned')
        self.assertFalse(tag_persona.active)
        self.assertTrue(tag.revoked)
        self.assertFalse(tag.in_use)
        self.assertFalse(self.env['ca.tag_lettore'].search([
            ('ca_tag_id', '=', tag.id)]))
        self.assertFalse(self.env['ca.lettore_persona'].search([
            ('ca_tag_persona', '=', tag_persona.id)]))

    # Test 97
    def test_97(self):
        """
        Descrizione:
            Un nuovo punto accesso di timbratura riceve i badge generici
            gia' esistenti tramite stamping_attach

        :return:
            Il tag generico risulta collegato al nuovo lettore
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visiting')
        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'Visiting 02',
            'tag_code': 'e00101500000ba05',
        })
        wizard.action_confirm()
        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BA05')], limit=1)

        lettore = self.env['ca.lettore'].create({
            'name': 'Lettore Badge Generico',
            'reader_ip': '10.0.0.211',
            'direction': 'in',
        })
        punto_accesso = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.spazio_5.id,
            'ca_lettore_id': lettore.id,
            'typology': 'stamping',
            'enable_sync': False,
            'date_start': date.today(),
            'date_end': date.today() + relativedelta(days=30),
        })
        self.assertFalse(self.env['ca.tag_lettore'].search([
            ('ca_tag_id', '=', tag.id),
            ('ca_punto_accesso_id', '=', punto_accesso.id)]))

        punto_accesso.commuta_abilitazione()

        self.assertTrue(punto_accesso.enable_sync)
        self.assertTrue(self.env['ca.tag_lettore'].search([
            ('ca_tag_id', '=', tag.id),
            ('ca_punto_accesso_id', '=', punto_accesso.id)]))

    # Test 98
    def test_98(self):
        """
        Descrizione:
            Il wizard badge generico propone il nome del prossimo badge
            in base al prefisso del tipo e alla numerazione gia' usata

        :return:
            Il nome proposto segue la serie '<prefisso> - <progressivo>'
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visiting')
        self.assertEqual(
            tipo_badge.get_next_badge_names(1), ['Visiting - 1'])

        wizard = self.env['ca.gestione_badge_generico'].new({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
        })
        wizard._onchange_tipo_badge_id()
        self.assertEqual(wizard.name, 'Visiting - 1')

        tipo_badge.create_badges([{
            'name': 'Visiting - 1',
            'tag_code': 'E00101500000BB01',
        }])
        self.assertEqual(
            tipo_badge.get_next_badge_names(3),
            ['Visiting - 2', 'Visiting - 3', 'Visiting - 4'])

        # anche un badge revocato occupa il suo numero
        tag = self.env['ca.tag'].search([
            ('tag_code', '=', 'E00101500000BB01')], limit=1)
        self.env['ca.gestione_badge_generico'].create({
            'mode': 'revoke',
            'ca_tag_id': tag.id,
        }).action_confirm()
        self.assertEqual(
            tipo_badge.get_next_badge_names(1), ['Visiting - 2'])

        # il prefisso esplicito ha la precedenza sul nome del tipo
        tipo_badge.badge_prefix = 'Visiting Lab'
        self.assertEqual(
            tipo_badge.get_next_badge_names(1), ['Visiting Lab - 1'])

    # Test 99
    def test_99(self):
        """
        Descrizione:
            Import massivo badge generici: il wizard genera il template con
            i nomi gia' compilati e crea i badge dal file ricaricato

        :return:
            Un ca.tag per riga del file, scritto sui punti accesso stamping
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_support_staff')
        wizard = self.env['ca.importa_badge_generico'].create({
            'tipo_badge_id': tipo_badge.id,
            'quantity': 3,
            'file_format': 'csv',
        })
        wizard.action_generate_template()
        self.assertEqual(wizard.state, 'template')
        self.assertTrue(wizard.template_file)
        self.assertTrue(wizard.template_filename.endswith('.csv'))

        template = base64.b64decode(wizard.template_file).decode('utf-8-sig')
        rows = list(csv.reader(io.StringIO(template), delimiter=';'))
        self.assertEqual(rows[0], ['Nome', 'Codice'])
        self.assertEqual(
            [row[0] for row in rows[1:] if row],
            ['Support Staff - 1', 'Support Staff - 2', 'Support Staff - 3'])
        self.assertEqual([row[1] for row in rows[1:] if row], ['', '', ''])

        # l'operatore compila la colonna codice, l'ultima riga resta vuota
        codes = ['e00101500000bc01', 'E00101500000BC02', '']
        filled = 'Nome;Codice\r\n' + ''.join(
            f"{row[0]};{code}\r\n"
            for row, code in zip(rows[1:], codes))
        wizard.write({
            'import_file': base64.b64encode(filled.encode('utf-8-sig')),
            'import_filename': 'badge.csv',
        })
        wizard.action_import()

        self.assertEqual(wizard.state, 'done')
        self.assertEqual(len(wizard.created_tag_ids), 2)
        self.assertIn('2 generic badges created', wizard.result_message)
        self.assertIn('1 rows skipped', wizard.result_message)

        access_points = self.env['ca.punto_accesso'].search([
            ('typology', '=', 'stamping')])
        for tag in wizard.created_tag_ids:
            self.assertEqual(tag.tag_code, tag.tag_code.upper())
            self.assertIn(
                tipo_badge.ca_proprieta_tag_id, tag.ca_proprieta_tag_ids)
            for access_point in access_points:
                self.assertTrue(self.env['ca.tag_lettore'].search([
                    ('ca_tag_id', '=', tag.id),
                    ('ca_punto_accesso_id', '=', access_point.id),
                ], limit=1))

    # Test 100
    def test_100(self):
        """
        Descrizione:
            Import massivo badge generici: un codice duplicato blocca
            l'intero import, nessun badge viene creato

        :return:
            UserError e nessun ca.tag creato
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visitatore')
        tipo_badge.create_badges([{
            'name': 'Visitatore - 1',
            'tag_code': 'E00101500000BD01',
        }])
        wizard = self.env['ca.importa_badge_generico'].create({
            'tipo_badge_id': tipo_badge.id,
            'quantity': 2,
        })
        filled = (
            'Nome;Codice\r\n'
            'Visitatore - 2;E00101500000BD01\r\n'
            'Visitatore - 3;E00101500000BD02\r\n'
            'Visitatore - 4;e00101500000bd02\r\n'
        )
        wizard.write({
            'import_file': base64.b64encode(filled.encode('utf-8-sig')),
            'import_filename': 'badge.csv',
        })
        with self.assertRaises(UserError):
            wizard.action_import()
        self.assertFalse(self.env['ca.tag'].with_context(
            active_test=False).search([
                ('tag_code', 'in',
                 ['E00101500000BD02', 'E00101500000BD03'])]))

    # Test 101
    def test_101(self):
        """
        Descrizione:
            Import massivo badge generici in formato xlsx

        :return:
            I badge del foglio Excel vengono creati
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_external_contractor')
        wizard = self.env['ca.importa_badge_generico'].create({
            'tipo_badge_id': tipo_badge.id,
            'quantity': 2,
            'file_format': 'xlsx',
        })
        wizard.action_generate_template()
        self.assertTrue(wizard.template_filename.endswith('.xlsx'))

        from openpyxl import load_workbook
        content = io.BytesIO(base64.b64decode(wizard.template_file))
        workbook = load_workbook(filename=content)
        sheet = workbook.active
        self.assertEqual(
            [sheet.cell(1, 1).value, sheet.cell(1, 2).value],
            ['Nome', 'Codice'])
        self.assertEqual(sheet.cell(2, 1).value, 'External Contractor - 1')
        sheet.cell(2, 2).value = 'e00101500000be01'
        sheet.cell(3, 2).value = 'E00101500000BE02'
        output = io.BytesIO()
        workbook.save(output)

        wizard.write({
            'import_file': base64.b64encode(output.getvalue()),
            'import_filename': 'badge.xlsx',
        })
        wizard.action_import()

        self.assertEqual(len(wizard.created_tag_ids), 2)
        self.assertEqual(
            sorted(wizard.created_tag_ids.mapped('tag_code')),
            ['E00101500000BE01', 'E00101500000BE02'])

    # Test 102
    def test_102(self):
        """
        Descrizione:
            Import massivo badge generici: nome duplicato e codice in
            formato non valido bloccano l'import

        :return:
            UserError e nessun badge creato
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_visiting')
        tipo_badge.create_badges([{
            'name': 'Visiting - 1',
            'tag_code': 'E00101500000BF01',
        }])
        wizard = self.env['ca.importa_badge_generico'].create({
            'tipo_badge_id': tipo_badge.id,
            'quantity': 2,
        })

        # nome gia' presente a database
        wizard.write({
            'import_file': base64.b64encode(
                ('Nome;Codice\r\n'
                 'Visiting - 1;E00101500000BF02\r\n').encode('utf-8-sig')),
            'import_filename': 'badge.csv',
        })
        with self.assertRaises(UserError):
            wizard.action_import()

        # codice rovinato da Excel
        wizard.write({
            'import_file': base64.b64encode(
                ('Nome;Codice\r\n'
                 'Visiting - 2;1,00101E+15\r\n').encode('utf-8-sig')),
        })
        with self.assertRaises(UserError):
            wizard.action_import()

        # nome duplicato dentro al file
        wizard.write({
            'import_file': base64.b64encode(
                ('Nome;Codice\r\n'
                 'Visiting - 2;E00101500000BF03\r\n'
                 'Visiting - 2;E00101500000BF04\r\n').encode('utf-8-sig')),
        })
        with self.assertRaises(UserError):
            wizard.action_import()

        self.assertFalse(self.env['ca.tag'].with_context(
            active_test=False).search([
                ('tag_code', 'like', 'E00101500000BF0'),
                ('tag_code', '!=', 'E00101500000BF01')]))

    # Test 103
    def test_103(self):
        """
        Descrizione:
            Il badge jolly e' configurato come tipo badge generico e il
            wizard singolo rifiuta un codice non esadecimale

        :return:
            Tipo jolly presente, UserError sul codice non valido
        """
        tipo_badge = self.env.ref(
            'inrim_controllo_accessi.tipo_badge_generico_jolly')
        self.assertEqual(tipo_badge.person_type, 'internal')
        self.assertEqual(
            tipo_badge.ca_proprieta_tag_id,
            self.env.ref('inrim_anagrafiche.proprieta_tag_jolly'))
        self.assertEqual(
            tipo_badge.get_next_badge_names(1), ['Badge Jolly - 1'])
        self.assertIn(
            tipo_badge.ca_proprieta_tag_id.id,
            self.env['ca.tipo_badge_generico'].get_proprieta_tag_ids(
                'internal'))

        wizard = self.env['ca.gestione_badge_generico'].create({
            'mode': 'add',
            'tipo_badge_id': tipo_badge.id,
            'name': 'Badge Jolly - 1',
            'tag_code': '1,00101E+15',
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()
        self.assertFalse(self.env['ca.tag'].with_context(
            active_test=False).search([('name', '=', 'Badge Jolly - 1')]))

        wizard.tag_code = 'e00101500000c001'
        wizard.action_confirm()
        tag = self.env['ca.tag'].search([
            ('name', '=', 'Badge Jolly - 1')], limit=1)
        self.assertEqual(tag.tag_code, 'E00101500000C001')

