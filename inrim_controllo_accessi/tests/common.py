from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        # Utenti
        cls.user = cls.env.ref('inrim_anagrafiche.inrim_demo_user')
        cls.user_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_1')
        cls.user_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_2')
        cls.user_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_3')
        cls.user_4 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_4')
        cls.user_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_5')
        # Spazio
        cls.spazio_1 = cls.env.ref('inrim_anagrafiche.ca_spazio_1')
        cls.spazio_2 = cls.env.ref('inrim_anagrafiche.ca_spazio_p0')
        cls.spazio_3 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p001')
        cls.spazio_4 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p002')
        cls.spazio_5 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p003')
        cls.spazio_6 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p004')
        cls.spazio_7 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p005')
        cls.spazio_8 = cls.env.ref('inrim_anagrafiche.ca_spazio_1p006')
        # Lettore
        cls.lettore_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_1')
        cls.lettore_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_2')
        cls.lettore_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_3')
        # Persona
        cls.persona_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_1')
        cls.persona_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_2')
        cls.persona_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_3')
        cls.persona_4 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_4')
        cls.persona_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_5')
        cls.persona_6 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_6')
        # Tag
        cls.tag_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_1')
        cls.tag_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_2')
        cls.tag_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_3')
        cls.tag_4 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_4')
        cls.tag_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_5')
        cls.tag_6 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_6')
        cls.tag_7 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_7')
        cls.tag_8 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_8')
        cls.tag_9 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_9')
        # Tag Lettore
        cls.tag_persona_1 = cls.env['ca.tag_persona'].create({
            'ca_persona_id': cls.persona_6.id,
            'ca_tag_id': cls.tag_8.id,
            'date_start': date.today() - timedelta(days=1),
            'date_end': date.today() + relativedelta(days=3)
        })
        # Punto Accesso
        cls.punto_accesso_1 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p001')
        cls.punto_accesso_2 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p002')
        # Anag Tipologie Istanze
        cls.anag_tipologie_istanze_1 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_ordine_contratto')
        cls.anag_tipologie_istanze_2 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_accordi')
        cls.anag_tipologie_istanze_3 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_bandi')
        cls.anag_tipologie_istanze_4 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_concorsi')
        cls.anag_tipologie_istanze_5 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_inviti_convocazioni')
        cls.anag_tipologie_istanze_6 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_conferimento')
        cls.anag_tipologie_istanze_7 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_assunzione')
        cls.anag_tipologie_istanze_8 = cls.env.ref(
            'inrim_controllo_accessi.ca_anag_tipologie_istanze_visita')
        # Richiesta Accesso Persona
        cls.richiesta_accesso_persona_1 = cls.env[
            'ca.richiesta_accesso_persona'
        ].create({
            'anag_tipologie_istanze_id': cls.anag_tipologie_istanze_1.id,
            'act_application_code': 'Richiesta Accesso Persona',
            'date_start': date.today() - relativedelta(months=1),
            'date_end': date.today() + relativedelta(days=3),
            'persona_id': cls.persona_3.id
        })
        # Richiesta Accesso
        cls.richiesta_accesso_1 = cls.env['ca.richiesta_accesso'].create({
            'date_start': datetime.now() - relativedelta(months=1),
            'date_end': datetime.now() + relativedelta(days=3),
            'ca_richiesta_accesso_persona_ids': cls.env[
                'ca.richiesta_accesso_persona'
            ].create({
                'anag_tipologie_istanze_id': cls.anag_tipologie_istanze_1.id,
                'act_application_code': 'Richiesta Accesso Persona',
                'date_start': datetime.now() - relativedelta(months=1),
                'date_end': datetime.now() + relativedelta(days=3)
            })
        })