from odoo.tests import tagged
from odoo.tests.common import TransactionCase
import requests
import json
from datetime import date
from dateutil.relativedelta import relativedelta

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        # Token
        def get_token(cls):
            token_url = cls.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/token/authenticate'
            data = {
                "username": "admin",
                "password": "admin"
            }
            response = requests.post(token_url, json=data)
            return json.loads(response.text)['body']['token']
        cls.token = get_token(cls)
        # Persona
        cls.persona_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_1')
        # Lettore
        cls.lettore_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_1')
        # Tag
        cls.tag_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_1')
        # Tag Persona
        cls.ca_tag_persona_id =  cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_persona_1')
        # Ente Azienda
        cls.ente_azienda_1 = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        # Spazio
        cls.spazio_1 = cls.env.ref('inrim_anagrafiche.ca_spazio_1')
        # Punto Accesso
        cls.punto_accesso_1p001 = cls.env.ref('inrim_controllo_accessi.ca_punto_accesso_1p001')
        # Parametri di sistema
        cls.people_key = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('people.key')
        cls.people_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('people.url')
        cls.api_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('web.base.url')
        # Fake Mock Get Addressbook
        cls.get_addressbook_data = [
            {
                "all_roles": [{}],
                "aspp": False,
                "badge": "E0010150AD255C11",
                "cell_phone_service": "",
                "codicefiscale": "CGNNMO99S70L219I",
                "cognome": "CgnomaA",
                "data_di_nascita": "1999-11-30",
                "data_fine": "",
                "data_fine_servizi": "",
                "data_inizio": "2019-08-01",
                "datanascita": "1999-11-30",
                "defibrillator_emergency": False,
                "division_uo_roles": [],
                "divisione_code": "SIR",
                "divisione_uo": "Sistemi Informatici e Reti",
                "divisione_uo_code": "sistemiinformaticiereti_divisioneuo",
                "divisione_uo_id": 100,
                "emergency_code": "",
                "emergency_user": False,
                "fire_emergency": False,
                "full_name": "CgnomaA NomeA",
                "job_level": "LIVELLO 0",
                "mail": "na.cognomea@inrim.mock",
                "matricola": "9999991",
                "name": "NomeA CgnomaA",
                "nome": "NomeA",
                "orcid": "https://orcid.org/0000-0002-7959-8257",
                "org_structure": "AMMINISTRAZIONE",
                "private_cell_phone": "000000000000",
                "qualifica": "COLLABORATORE T.E.R.",
                "referente": "CgnomaB NomeB",
                "referente_uid": "",
                "responsabile_uid": "nb.cognomeb",
                "room_1": "Cp212",
                "room_2": "",
                "room_3": "",
                "room_4": "",
                "sanitary_emergency": False,
                "service_user": False,
                "telephonNumber": "01139191",
                "tellab": "",
                "tellab1": "",
                "tellab2": "",
                "tipo_personale": "DIPENDENTI T.I.",
                "uid": "na.cognomea"
            },
            {
                "all_roles":[],
                "aspp": False,
                "badge": "E0010150AD255C12",
                "cell_phone_service": "",
                "codicefiscale": "CGNNMB95A01L219Y",
                "cognome": "CognomeB",
                "data_di_nascita": "1995-01-01",
                "data_fine": "",
                "data_fine_servizi": "",
                "data_inizio": "2019-08-01",
                "datanascita": "1980-05-25",
                "defibrillator_emergency": False,
                "division_uo_roles": [
                    {
                        "id":718,
                        "proprieta": False,
                        "tipo":[],
                        "type_id":9
                    }
                ],
                "divisione_code": "SIR",
                "divisione_uo": "Sistemi Informatici e Reti",
                "divisione_uo_code": "sistemiinformaticiereti_divisioneuo",
                "divisione_uo_id": 100,
                "emergency_code": "",
                "emergency_user": False,
                "fire_emergency": False,
                "full_name": "CognomeB NomeB",
                "job_level": "LIVELLO 0",
                "mail": "nb.cognomeb@inrim.mock",
                "matricola": "9999998",
                "name": "NomeB CognomeB",
                "nome": "NomeB",
                "orcid": "https://orcid.org/0000-0002-7959-8257",
                "org_structure": "AMMINISTRAZIONE",
                "private_cell_phone": "000000000000",
                "qualifica": "TECNOLOGO",
                "referente": "CognomeC NomeC",
                "referente_uid": "",
                "responsabile_uid": "nc.cognomec",
                "room_1": "Cp209",
                "room_2": "",
                "room_3": "",
                "room_4": "",
                "sanitary_emergency": False,
                "service_user": False,
                "telephonNumber": "01139191",
                "tellab": "",
                "tellab1": "",
                "tellab2": "",
                "tipo_personale": "DIPENDENTI T.I.",
                "uid": "nb.cognomeb"
            },
            {
                "all_roles": [],
                "aspp": False,
                "badge": "E0010150AD255C13",
                "cell_phone_service": "",
                "codicefiscale": "CGNNMC95L01L219C",
                "cognome": "CognomeC",
                "data_di_nascita": "1995-07-01",
                "data_fine": "",
                "data_fine_servizi": "",
                "data_inizio": "2015-08-01",
                "datanascita": "1980-05-25",
                "defibrillator_emergency": False,
                "division_uo_roles":[
                    {
                        "id":718,
                        "proprieta":False,
                        "tipo":[],
                        "type_id":9
                    }
                ],
                "divisione_code": "SIR",
                "divisione_uo": "Sistemi Informatici e Reti",
                "divisione_uo_code": "sistemiinformaticiereti_divisioneuo",
                "divisione_uo_id": 100,
                "emergency_code": "",
                "emergency_user": False,
                "fire_emergency": False,
                "full_name": "CognomeC NomeC",
                "job_level": "LIVELLO 0",
                "mail": "nb.cognomeb@inrim.mock",
                "matricola": "9999997",
                "name": "NomeC CognomeC",
                "nome": "NomeC",
                "orcid": "https://orcid.org/0000-0002-7959-8257",
                "org_structure": "AMMINISTRAZIONE",
                "private_cell_phone": "000000000000",
                "qualifica": "DIREZIONE",
                "referente": "",
                "referente_uid": "",
                "responsabile_uid": "",
                "room_1": "Cp204",
                "room_2": "",
                "room_3": "",
                "room_4": "",
                "sanitary_emergency": False,
                "service_user": False,
                "telephonNumber": "01139191",
                "tellab": "",
                "tellab1": "",
                "tellab2": "",
                "tipo_personale": "DIPENDENTI T.I.",
                "uid": "nc.cognomec"
            }
        ]
        cls.get_rooms_data = [
            {
                'base_name': '01',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': '1p001',
                'officer_user_uid': 'admin',
                'parent_building_code': '1p0',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '02',
                'institution': 'INRIM',
                'institution_address': 'Cacce',
                'institution_address_ref': 'cacce',
                'institution_ref': 'inrim',
                'maximum_number_user': 1,
                'name': '1p002',
                'divisione_uo_id': 1,
                'officer_user_uid': 'admin',
                'parent_building_code': '1p0',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '03',
                'institution': 'INRIM',
                'institution_address': 'Cacce',
                'institution_address_ref': 'cacce',
                'institution_ref': 'inrim',
                'maximum_number_user': 1,
                'name': '1p003',
                'divisione_uo_id': 1,
                'officer_user_uid': 'admin',
                'parent_building_code': '1p0',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '04',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': '1p004',
                'divisione_uo_id': 1,
                'officer_user_uid': 'user1',
                'parent_building_code': '1p0',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '05',
                'institution': '',
                'institution_address': 'test',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': '1p005',
                'divisione_uo_id': 1,
                'officer_user_uid': 'user2',
                'parent_building_code': '1p0',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '04',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp204',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp2',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '09',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp209',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp2',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }, {
                'base_name': '12',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp212',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp2',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3, 
                'type_name': 'Locale'
            }
        ]