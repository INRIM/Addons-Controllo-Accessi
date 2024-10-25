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
        self.assertTrue(self.service_reader_jwt)
        self.assertTrue(self.service_reader_url)
        self.assertTrue(self.info_data)
        self.assertTrue(self.status_data)
        self.assertTrue(self.punto_accesso_1p001)
        self.assertTrue(self.read_events_data)
        self.assertTrue(self.tag_persona_id)
        self.assertTrue(self.path_files)

    def test_2(self):
        """
        Descrizione:
            Verifica che alla creazione di un ca.ente_azienda con tipo Sede si valorizzino i campi jwt e url_gateway_lettori se non popolati

        :return: I campi si popolano correttamente
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        vals = {
            'name': 'Test',
            'pec': 'Test PEC',
            'tipo_ente_azienda_id': self.tipo_ente_azienda_1.id
        }
        ente_azienda_id = self.env['ca.ente_azienda'].create(vals)
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'name': 'Test 1'
        })
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)


    # Test 10
    def test_3(self):
        """
        Descrizione:
            Verifica che alla modifica di un ca.ente_azienda con tipo Sede si valorizzino i campi jwt e url_gateway_lettori se non popolati

        :return: I campi si popolano correttamente
        """
        self.env = self.env(user=self.user_5)
        self.cr = self.env.cr
        vals = {
            'name': 'Test',
            'pec': 'Test PEC',
            'tipo_ente_azienda_id': self.tipo_ente_azienda_2.id
        }
        ente_azienda_id = self.env['ca.ente_azienda'].create(vals)
        self.assertFalse(ente_azienda_id.jwt)
        self.assertFalse(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'name': 'Test 2'
        })
        self.assertFalse(ente_azienda_id.jwt)
        self.assertFalse(ente_azienda_id.url_gateway_lettori)
        ente_azienda_id.write({
            'tipo_ente_azienda_id': self.tipo_ente_azienda_1.id
        })
        self.assertTrue(ente_azienda_id.jwt)
        self.assertTrue(ente_azienda_id.url_gateway_lettori)

    # Test 2
    # @responses.activate
    @respx.mock
    def test_4(self):
        """
        Descrizione:
            Verifica che i valori ricevuti dal metodo post_rfid_info vengono scritti correttamente nei campi del lettore

        :return: I campi vengono scritti correttamente nei campi del lettore
        """

        def info(request, route):
            return httpx.Response(200, json=self.info_data)

        def status(request, route):
            return httpx.Response(200, json=self.status_data)

        respx.post(
            'http://local-host/info',
        ).mock(
            side_effect=info
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            side_effect=status
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.load_reader()

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

        def info(request, route):
            return httpx.Response(200, json=self.info_data)

        def status(request, route):
            return httpx.Response(200, json=self.status_data)

        def events(request, route):
            return httpx.Response(200, json=self.read_events_data)

        respx.post(
            'http://local-host/info',
        ).mock(
            side_effect=info
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            side_effect=status
        )
        respx.post(
            'http://local-host/read-events',
        ).mock(
            side_effect=events
        )

        device = '10.10.10.1'
        device_id = self.info_data['info']['deviceId']
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        code = punto_accesso_id.save_events_to_json()
        self.localfilename = f"{code}_{punto_accesso_id.events_to_read_num}.json"
        file_path = Path(f"{self.path_files}/TODO/{self.localfilename}")
        self.assertTrue(file_path.is_file())

    # Test 4
    @respx.mock
    def test_6(self):
        """
        Descrizione:
            Verifica che i metodi: events_save_json, add_tags, read_json_file funzionino correttamente e restituiscano i risultati attesi

        :return: I metodi funzionano e restituiscono i risultati attesi
        """

        def info(request, route):
            return httpx.Response(200, json=self.info_data)

        def status(request, route):
            return httpx.Response(200, json=self.status_data)

        respx.post(
            'http://local-host/info',
        ).mock(
            side_effect=info
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            side_effect=status
        )

        device = '10.10.10.1'
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device)
        ], limit=1)
        punto_accesso_id.events_process_todo()
        # self.assertTrue(log_integrazione_lettori)
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

        def info(request, route):
            return httpx.Response(200, json=self.info_data)

        def status(request, route):
            return httpx.Response(200, json=self.status_data)

        respx.post(
            'http://local-host/info',
        ).mock(
            side_effect=info
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            side_effect=status
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

        def info(request, route):
            return httpx.Response(200, json=self.info_data)

        def status(request, route):
            return httpx.Response(200, json=self.status_data_empty)

        def tagres(request, route):
            return httpx.Response(200, json=self.res_add_tag)

        respx.post(
            'http://local-host/info',
        ).mock(
            side_effect=info
        )

        respx.post(
            'http://local-host/status',
        ).mock(
            side_effect=status
        )

        respx.post(
            'http://local-host/add-tags',
        ).mock(
            side_effect=tagres
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
