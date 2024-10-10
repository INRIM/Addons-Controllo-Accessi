from odoo.addons.inrim_controllo_accessi_rfidglobal.tests.common import TestCommon
from odoo.tests import tagged

@tagged("post_install", "-at_install", "inrim")
class RfidTestCommon(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che i parametri di sistema per i lettori rfid siano valorizzati

        :return: I dati nei parametri di sistema esistono e sono valorizzati
        """
        self.assertTrue(self.service_reader_jwt)
        self.assertTrue(self.service_reader_url)
        self.assertTrue(self.info_data)
        self.assertTrue(self.status_data)

    # Test 2
    def test_2(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_info vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """
        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        self.env['ca.punto_accesso'].post_rfid_info(device, self.info_data)
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        self.assertEqual(device_id, punto_accesso_id.ca_lettore_id.device_id)

    # Test 3
    def test_3(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_status vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """
        device = '10.10.10.1'
        event_cnt = self.status_data['diagnostic']['event_cnt']
        self.env['ca.punto_accesso'].post_rfid_status(device, self.status_data)
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        self.assertEqual(event_cnt, punto_accesso_id.ca_lettore_id.available_events)