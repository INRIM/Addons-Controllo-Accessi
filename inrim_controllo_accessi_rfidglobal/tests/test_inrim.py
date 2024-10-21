from odoo.addons.inrim_controllo_accessi_rfidglobal.tests.common import TestCommon
from datetime import datetime
from odoo.tests import tagged
import os

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
        self.assertTrue(self.punto_accesso_1p001)
        self.assertTrue(self.read_events_data)
        self.assertTrue(self.tag_persona_id)
        self.assertTrue(self.path_files)

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

    # Test 4
    def test_4(self):
        """
        Descrizione:
            Verifica che i metodi: events_save_json, add_tags, read_json_file funzionino correttamente e restituiscano i risultati attesi

        :return: I metodi funzionano e restituiscono i risultati attesi
        """
        datetime_now = datetime.now()
        punto_accesso = self.punto_accesso_1p001
        data = self.read_events_data
        self.env['ca.punto_accesso'].events_save_json(data, punto_accesso, datetime_now)
        todo_path = os.path.join(self.path_files, 'TODO')
        done_path = os.path.join(self.path_files, 'DONE')
        codice_attivita = datetime_now.timestamp()
        name = punto_accesso.ca_lettore_id.name.replace(' ', '_')
        file_name = f'{str(codice_attivita)}_{name}.json'
        file_path = os.path.join(todo_path, file_name)
        self.assertTrue(os.path.isfile(file_path))
        body = self.env['ca.punto_accesso'].add_tags(punto_accesso, 'IT', 'TO')
        self.assertTrue(body)
        self.env['ca.punto_accesso'].read_json_file(punto_accesso, datetime_now)
        log_integrazione_lettori = self.env['ca.log_integrazione_lettori'].search([
            ('activity_code', '=', datetime_now.timestamp()),
            ('ca_lettore_id', '=', punto_accesso.ca_lettore_id.id),
            ('operation_status', '=', 'ok')
        ])
        self.assertTrue(log_integrazione_lettori)
        self.env['ca.anag_registro_accesso'].search([
            ('ca_punto_accesso_id', '=', punto_accesso.id),
            ('ca_tag_persona_id', '=', self.tag_persona_id.id),
            ('type', '=', 'auto')
        ])
        file_path = os.path.join(done_path, file_name)
        self.assertTrue(os.path.isfile(file_path))
        os.remove(file_path)
        self.assertFalse(os.path.isfile(file_path))