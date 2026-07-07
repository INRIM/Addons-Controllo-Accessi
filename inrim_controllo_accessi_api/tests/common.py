from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class TestCommon(HttpCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = AssertionError
        cls.company = cls.env.ref('base.main_company')
        # Persona
        cls.persona_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_1')
        # Lettore
        cls.lettore_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_1')
        # Tag
        cls.tag_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_1')
        # Tag Persona
        cls.ca_tag_persona_id = cls.env.ref(
            'inrim_anagrafiche.inrim_demo_ca_tag_persona_1')
        # Ente Azienda
        cls.ente_azienda_1 = cls.env.ref(
            'inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        # Spazio
        cls.spazio_1 = cls.env.ref('inrim_anagrafiche.ca_spazio_1')
        # Punto Accesso
        cls.punto_accesso_1p001 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p001')
        cls.api_url = cls.base_url()

    def setUp(self):
        super().setUp()
        self.token = self._fetch_token("user3", "demo3")
        self.tokentech = self._fetch_token("user5", "demo5")

    def _fetch_token(self, username, password):
        response = self.url_open(
            '/token/authenticate',
            json={"username": username, "password": password},
        )
        return response.json().get('token')
