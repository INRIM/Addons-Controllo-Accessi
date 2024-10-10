from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.failureException = True
        # Parametri di sistema
        cls.service_reader_jwt = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.jwt')
        cls.service_reader_url = cls.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.url')
        # Fake Mock Info
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
        # Fake Mock Status
        cls.status_data = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 3268,
                "event_cnt": 4,
                "systemClock": "2023-12-01T18:20:21.000",
            }
        }