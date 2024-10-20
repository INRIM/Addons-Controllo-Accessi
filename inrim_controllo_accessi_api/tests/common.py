import json

import requests
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True

        # Token
        def get_token(clz, user, passw):
            token_url = clz.env['ir.config_parameter'].sudo().get_param(
                'web.base.url') + '/token/authenticate'
            data = {
                "username": user,
                "password": passw
            }
            response = requests.post(token_url, json=data)
            return json.loads(response.text).get('token')

        cls.token = get_token(cls, "user3", "demo3")
        cls.tokentech = get_token(cls, "user5", "demo5")

        cls.company = cls.env.ref('controllo_accessi_inrim_app.res_company_inrim')
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
        cls.api_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('web.base.url')
