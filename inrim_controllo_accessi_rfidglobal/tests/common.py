from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        cls.tipo_ente_azienda_1 = cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        cls.tipo_ente_azienda_2 = cls.env.ref(
            'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata')
        cls.ente_azienda_1 = cls.env.ref(
            'inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        # Parametri di sistema
        cls.service_reader_jwt = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.jwt')
        cls.service_reader_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.url')
        # Mock Info
        cls.info_data = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 0,
                "event_cnt": 0
            },
            "info": {
                "deviceId": "29335616",
                "readerType": "ID MAX50.xx",
                "mode": "Access Mode",
                "modeCode": "0x20"
            }
        }
        # Mock Status
        cls.status_data = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 3268,
                "event_cnt": 4,
                "systemClock": "2023-12-01T18:20:21.000",
            }
        }
        cls.status_data_empty = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 3268,
                "event_cnt": 0,
                "systemClock": "2023-12-01T18:20:21.000",
            }
        }
        cls.res_add_tag = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 0,
                "event_cnt": 0
            },
            "result": True
        }
        # Punto Accesso
        cls.punto_accesso_1p001 = cls.env.ref(
            'inrim_controllo_accessi.ca_punto_accesso_1p001')
        # Tag Persona
        cls.tag_persona_id = cls.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_persona_1')
        # Mock Read Events
        cls.read_events_data = {
            "status": 148,
            "statusStr": "OK",
            "layoutIdd": True,
            "layoutTimeStamp": True,
            "layoutEventStatus": True,
            "layoutInput": True,
            "dataSetsLenght": 5,
            "hasMore": True,
            "layout": [
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False
            ],
            "eventRecords": [
                {
                    "idd": "E0010150AD255C11",
                    "eventDateTime": "2023-02-24T07:03:13",
                    "errorCode": "0000",
                    "accessAllowed": False,
                    "digitalInput": [
                        True,
                        True,
                        True,
                        True,
                        False,
                        False,
                        False,
                        False
                    ]
                },
                {
                    "idd": "E0010150AD255C12",
                    "eventDateTime": "2023-02-14T17:03:13",
                    "errorCode": "0000",
                    "accessAllowed": True,
                    "digitalInput": [
                        True,
                        True,
                        True,
                        True,
                        False,
                        False,
                        False,
                        False
                    ]
                },
                {
                    "idd": "E0010150AD255C13",
                    "eventDateTime": "2023-02-24T07:03:13",
                    "errorCode": "0000",
                    "accessAllowed": True,
                    "digitalInput": [
                        True,
                        True,
                        True,
                        True,
                        False,
                        False,
                        False,
                        False
                    ]
                },
                {
                    "idd": "E0010150AD255C13",
                    "eventDateTime": "2023-02-24T07:03:15",
                    "errorCode": "0000",
                    "accessAllowed": True,
                    "digitalInput": [
                        True,
                        True,
                        True,
                        True,
                        False,
                        False,
                        False,
                        False
                    ]
                },
                {
                    "idd": "E0010150AD255C14",
                    "eventDateTime": "2023-02-24T07:03:15",
                    "errorCode": "0000",
                    "accessAllowed": True,
                    "digitalInput": [
                        True,
                        True,
                        True,
                        True,
                        False,
                        False,
                        False,
                        False
                    ]
                }
            ]
        }

        cls.path_files = '/mnt/reader-data'
        cls.event_fname = ""
