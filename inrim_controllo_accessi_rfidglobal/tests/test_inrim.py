from pathlib import Path

import httpx
import respx
from odoo.addons.inrim_controllo_accessi_rfidglobal.tests.common import TestCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class RfidTestCommon(TestCommon):
    localfilename = ""

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che i parametri di sistema per i lettori rfid siano valorizzati

        :return: I dati nei parametri di sistema esistono e sono valorizzati
        """
        self.assertTrue(self.user_5)
        self.assertTrue(self.service_reader_jwt)
        self.assertTrue(self.service_reader_url)
        self.assertTrue(self.info_data)
        self.assertTrue(self.status_data)
        self.assertTrue(self.punto_accesso_1p001)
        self.assertTrue(self.read_events_data)
        self.assertTrue(self.read_events_data_empty)
        self.assertTrue(self.tag_persona_id)
        self.assertTrue(self.path_files)

    def test_2(self):
        """
        Descrizione:
            Verifica che alla creazione di un ca.ente_azienda con tipo Sede si valorizzino i campi jwt e url_gateway_lettori se non popolati

        :return: I campi si popolano correttamente
        """

        vals = {
            'name': 'Test',
            'pec': 'Test PEC',
            'tipo_ente_azienda_id': self.tipo_ente_azienda_1.id
        }
        ente_azienda_id = self.env['ca.ente_azienda'].with_user(self.user_5).create(vals)
        self.assertFalse(ente_azienda_id.jwt == "")
        self.assertFalse(ente_azienda_id.url_gateway_lettori == "")
        ente_azienda_id.with_user(self.user_5).write({
            'name': 'Test 1'
        })
        self.assertFalse(ente_azienda_id.jwt == "")
        self.assertFalse(ente_azienda_id.url_gateway_lettori == "")

    # Test 2
    # @responses.activate
    @respx.mock
    def test_4(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_info vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        self.punto_accesso_1.commuta_abilitazione()
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.load_reader()

        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)

        self.assertEqual(device_id, punto_accesso_id.ca_lettore_id.device_id)
        self.assertEqual(self.status_data['diagnostic']['event_cnt'],
                         punto_accesso_id.ca_lettore_id.available_events)

    # Test 3
    @respx.mock
    def test_5(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_status vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )
        respx.post(
            'http://local-host/read-events',
        ).mock(
            return_value=httpx.Response(200, json=self.read_events_data)
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.commuta_abilitazione()
        code = punto_accesso_id.save_events_to_json()
        self.localfilename = f"{code}_{punto_accesso_id.events_to_read_num}.json"
        file_path = Path(f"{self.path_files}/TODO/{self.localfilename}")
        self.assertTrue(file_path.is_file())

    # Test 51
    @respx.mock
    def test_51(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_status vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )
        respx.post(
            'http://local-host/read-events',
        ).mock(
            return_value=httpx.Response(200, json=self.read_events_data_empty)
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.commuta_abilitazione()
        code = punto_accesso_id.save_events_to_json()
        self.localfilename = f"{code}_{punto_accesso_id.events_to_read_num}.json"
        file_path = Path(f"{self.path_files}/TODO/{self.localfilename}")
        self.assertFalse(file_path.exists())

    # Test 4
    @respx.mock
    def test_6(self):
        """
        Descrizione:
            Verifica che i metodi: events_save_json, add_tags, read_json_file funzionino correttamente e restituiscano i risultati attesi

        :return: I metodi funzionano e restituiscono i risultati attesi
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )

        device = '10.10.10.1'
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.commuta_abilitazione()
        punto_accesso_id.events_process_todo()
        res = self.env['ca.anag_registro_accesso'].search([
            ('ca_punto_accesso_id', '=', punto_accesso_id.id),
            ('ca_tag_persona_id', '=', self.tag_persona_id.id),
            ('type', '=', 'auto')
        ], limit=1)
        self.assertFalse(res.access_allowed)
        done = Path(f"{self.path_files}/DONE")
        for filed in done.glob('*.json'):
            self.assertTrue(filed.is_file())
            filed.unlink()

    # Test Add Tag event count > 0
    @respx.mock
    def test_7(self):
        """
        Descrizione:
            Verifica che i metodi: events_save_json, add_tags, read_json_file funzionino correttamente e restituiscano i risultati attesi

        :return: I metodi funzionano e restituiscono i risultati attesi
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        res = punto_accesso_id.update_reader_tags()
        self.assertFalse(res)

    # Test Add Tag event count == 0
    @respx.mock
    def test_8(self):
        """
        Descrizione:
            Verifica che i metodi: events_save_json, add_tags, read_json_file funzionino correttamente e restituiscano i risultati attesi

        :return: I metodi funzionano e restituiscono i risultati attesi
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )

        respx.post(
            'http://local-host/add-tags',
        ).mock(
            return_value=httpx.Response(200, json=self.res_add_tag)
        )

        device = '10.10.10.1'
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.enable_sync = True
        tagsBody = punto_accesso_id.get_tags_boby()
        self.assertEqual(len(tagsBody.get('tags')), 6)
        self.assertEqual(len(tagsBody.get('timeZoneTable')), 2)
        res = punto_accesso_id.update_reader_tags()
        self.assertTrue(type(res) == str)

    @respx.mock
    def test_9(self):
        """
        Descrizione:
            Aggiorna orologio di sistema del Reader
        """

        respx.post(
            'http://local-host/info',
        ).mock(
            return_value=httpx.Response(200, json=self.info_data)
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            return_value=httpx.Response(200, json=self.status_data)
        )

        respx.post(
            'http://local-host/update-clock',
        ).mock(
            return_value=httpx.Response(200, json=self.res_add_tag)
        )

        device = '10.10.10.1'
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.commuta_abilitazione()
        result = punto_accesso_id.update_reader_clock()
        self.assertTrue(result)
