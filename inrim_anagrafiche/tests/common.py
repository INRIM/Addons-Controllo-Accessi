from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from datetime import date
import base64

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        # Utenti
        cls.user = cls.env.ref('inrim_anagrafiche.inrim_demo_user')
        cls.user_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_1')
        cls.user_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_2')
        cls.user_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_3')
        cls.user_4 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_4')
        cls.user_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_5')
        # Enti/Aziende
        cls.ente_azienda_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        cls.ente_azienda_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_2')
        cls.ente_azienda_3 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_3')
        cls.ente_azienda_4 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_4')
        cls.ente_azienda_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_5')
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
        # Lettore
        cls.lettore_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_1')
        cls.lettore_2 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_2')