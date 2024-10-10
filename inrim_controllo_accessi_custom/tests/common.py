from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        # Tipo Ente Azienda
        cls.tipo_ente_azienda_1 = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        cls.tipo_ente_azienda_2 = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata')
        # Utente
        cls.user_5 = cls.env.ref('inrim_anagrafiche.inrim_demo_user_5')
        # Persona
        cls.persona_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_1')
        # Enti/Aziende
        cls.ente_azienda_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        # Punto Accesso
        cls.punto_accesso_1 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p001')