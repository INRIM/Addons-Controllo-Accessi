from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        # Enti/Aziende
        cls.ente_azienda_1 = cls.env.ref(
            'inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')

        # Punto Accesso
        cls.punto_accesso_1 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p001')
        cls.punto_accesso_2 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p002')

        # Parametri di sistema
        cls.people_key = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('people.key')
        cls.people_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('people.url')

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
                "room_1": "Cp312",
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
                "all_roles": [],
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
                        "id": 718,
                        "proprieta": False,
                        "tipo": [],
                        "type_id": 9
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
                "room_1": "Cp309",
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
                "division_uo_roles": [
                    {
                        "id": 718,
                        "proprieta": False,
                        "tipo": [],
                        "type_id": 9
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
                "room_1": "Cp304",
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
                'name': '1p101',
                'officer_user_uid': 'admin',
                'parent_building_code': '1p1',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '02',
                'institution': 'INRIM',
                'institution_address': 'Cacce',
                'institution_address_ref': 'cacce',
                'institution_ref': 'inrim',
                'maximum_number_user': 1,
                'name': '1p102',
                'divisione_uo_id': 1,
                'officer_user_uid': 'admin',
                'parent_building_code': '1p1',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '03',
                'institution': 'INRIM',
                'institution_address': 'Cacce',
                'institution_address_ref': 'cacce',
                'institution_ref': 'inrim',
                'maximum_number_user': 1,
                'name': '1p103',
                'divisione_uo_id': 1,
                'officer_user_uid': 'admin',
                'parent_building_code': '1p1',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '04',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': '1p104',
                'divisione_uo_id': 1,
                'officer_user_uid': 'user1',
                'parent_building_code': '1p1',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '05',
                'institution': '',
                'institution_address': 'test',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': '1p105',
                'divisione_uo_id': 1,
                'officer_user_uid': 'user2',
                'parent_building_code': '1p1',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '04',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp304',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp3',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '09',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp309',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp3',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            },
            {
                'base_name': '12',
                'institution': '',
                'institution_address': '',
                'institution_address_ref': '',
                'institution_ref': '',
                'maximum_number_user': 1,
                'name': 'Cp312',
                'divisione_uo_id': 1,
                'officer_user_uid': '',
                'parent_building_code': 'Cp3',
                'parent_building_id': 3025,
                'prefix': '01-N-',
                'surface': 0,
                'technical_location': False,
                'type': 3,
                'type_name': 'Locale'
            }
        ]
        # Richiesta Accesso Persona
