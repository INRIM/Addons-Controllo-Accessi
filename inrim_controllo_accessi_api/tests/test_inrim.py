import requests
from odoo.addons.inrim_controllo_accessi_api.tests.common import TestCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install", "inrim")
class ApiTestCommon(TestCommon):

    # Test 1
    def test_1(self):
        """
        Descrizione:
            Verifica che i parametri di sistema per la connessione a people siano valorizzati

        :return: I dati nei parametri di sistema esistono e sono valorizzati
        """
        self.assertTrue(self.people_key)
        self.assertTrue(self.people_url)
        self.assertTrue(self.get_addressbook_data)
        self.assertTrue(self.get_rooms_data)
        self.assertTrue(self.persona_1)
        self.assertTrue(self.lettore_1)
        self.assertTrue(self.token)
        self.assertTrue(self.tag_1)
        self.assertTrue(self.ente_azienda_1)
        self.assertTrue(self.spazio_1)
        self.assertTrue(self.punto_accesso_1p001)

    # Test 2
    def test_2(self):
        """
        Descrizione:
            Verifica che il metodo get_addressbook_data crei gli utente le persone

        :return: Gli utenti e le persone vengono create correttamente
        """
        data = self.get_addressbook_data
        for dt in data:
            user_id = self.env['res.users'].search([
                ('login', '=', dt['uid'])
            ])
            if user_id:
                user_id.unlink()
                user_id = False
            persona_id = self.env['ca.persona'].search([
                ('freshman', '=', dt['matricola']),
                ('fiscalcode', '=', dt['codicefiscale'])
            ])
            if persona_id:
                persona_id.unlink()
                persona_id = False
            self.assertFalse(persona_id)
            self.assertFalse(user_id)
            self.env['ca.persona'].get_addressbook_data(data)
            user_id = self.env['res.users'].search([
                ('login', '=', dt['uid'])
            ])
            persona_id = self.env['ca.persona'].search([
                ('freshman', '=', dt['matricola']),
                ('fiscalcode', '=', dt['codicefiscale'])
            ])
            self.assertTrue(persona_id)
            self.assertEqual(persona_id.associated_user_id, user_id)
            self.assertEqual(persona_id.fiscalcode, dt['codicefiscale'])
            self.assertEqual(persona_id.freshman, dt['matricola'])
            self.assertTrue(user_id)
            self.assertEqual(user_id.name, dt['name'])
            self.assertEqual(user_id.login, dt['uid'])

    # Test 3
    def test_3(self):
        """
        Descrizione:
            Verifica che il metodo get_rooms_data crei i record di spazio

        :return: I record di spazio vengono creati correttamente
        """
        data = self.get_rooms_data
        for dt in data:
            spazio_id = self.env['ca.spazio'].search([
                ('name', '=', dt['name'])
            ], limit=1)
            if spazio_id:
                punto_accesso_id = self.env['ca.punto_accesso'].search([
                    ('ca_spazio_id', '=', spazio_id.id)
                ])
                if punto_accesso_id:
                    punto_accesso_id.unlink()
                spazio_id.unlink()
                spazio_id = False
            self.assertFalse(spazio_id)
            self.env['ca.spazio'].get_rooms_data(data)
            spazio_id = self.env['ca.spazio'].search([
                ('name', '=', dt['name']),
                ('tipo_spazio_id.name', '=', dt['type_name']),
                ('ente_azienda_id.ref', '=', dt['institution_address_ref'])
            ], limit=1)
            if dt.get('institution_address_ref') and dt.get('type_name'):
                self.assertTrue(spazio_id)
                self.assertEqual(spazio_id.tipo_spazio_id.name, dt['type_name'])
                self.assertEqual(spazio_id.ente_azienda_id.ref,
                                 dt['institution_address_ref'])

    def test_documento(self, test=False):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API documento
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.token}

        # post
        data = {
            "ca_persona_id": self.persona_1.id,
            "tipo_documento_id": self.env.ref(
                'inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
            "validity_start_date": "2024-01-01",
            "validity_end_date": "2024-06-20",
            "issued_by": "Comune",
            "document_code": "Codice Doc Persona 1"
        }

        response = requests.post(self.api_url + '/api/documento', headers=headers,
                                 json=data)
        self.assertEqual(response.status_code, 200)
        id_from_post = response.json().get('id')

        # get
        response = requests.get(self.api_url + '/api/documento', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # put
        data = {
            "id": id_from_post,
            "validity_end_date": "2024-06-26",
        }

        response = requests.put(self.api_url + '/api/documento', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('validity_end_date'), '2024-06-26')

        # delete documento
        if test == False:
            headers = {
                'token': self.token,
                'active_test': 'True'
            }

            data = {
                "id": id_from_post
            }
            response = requests.delete(self.api_url + '/api/documento', headers=headers,
                                       json=data)
            self.assertEqual(response.status_code, 200)
        return id_from_post

    def test_ente_azienda(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API ente_azienda
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.token}
        sede_staccata = self.env.ref(
            "inrim_anagrafiche.tipo_ente_azienda_sede_distaccata")
        ita = self.env.ref("base.it")
        taranto = self.env.ref("base.state_it_ta")
        torino = self.env.ref("base.state_it_to")
        # post
        data = {
            "name": "Azienda 1",
            "parent_id": self.ente_azienda_1.id,
            "parent_path": "",
            "street": "Street",
            "street2": "Street2",
            "state_id": taranto.id,
            "vat": "Vat",
            "note": "Ente Azienda 1",
            "email": "Email",
            "phone": "Phone",
            "mobile": "Mobile",
            "website": "Website",
            "pec": "Pec Test",
            "company_id": self.company.id,
            "tipo_ente_azienda_id": sede_staccata.id,
            "ca_persona_ids": [self.persona_1.id],
            "ref": True,
            "lock": False,
            "url_gateway_lettori": "In base al sistema",
            "nome_chiave_header": "In base al sistema",
            "jwt": "In base al sistema"
        }

        response = requests.post(self.api_url + '/api/ente_azienda', headers=headers,
                                 json=data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        id_from_post = res_data.get('id')

        data = {
            "id": id_from_post,
            "name": "Azienda 1",
            "parent_id": self.ente_azienda_1.id,
            "parent_path": "",
            "street": "Street",
            "street2": "Street2",
            "state_id": {"name": taranto.id, "label": taranto.name},
            "vat": "Vat",
            "note": "Ente Azienda 1",
            "email": "Email",
            "phone": "Phone",
            "mobile": "Mobile",
            "website": "Website",
            "pec": "Pec Test",
            "company_id": {"name": self.company.id, "label": self.company.name},
            "tipo_ente_azienda_id": {
                "name": sede_staccata.id, "label": sede_staccata.name},
            "ca_persona_ids": [
                {"name": self.persona_1.id, "label": self.persona_1.display_name}
            ],
            "ref": True,
            "lock": False,
            "url_gateway_lettori": "In base al sistema",
            "nome_chiave_header": "In base al sistema",
            "jwt": "In base al sistema"
        }
        self.assertEqual(res_data.get('ca_persona_ids'), data['ca_persona_ids'])

        # get
        response = requests.get(self.api_url + '/api/ente_azienda', headers=headers,
                                json=data)

        self.assertEqual(response.status_code, 200)

        # put
        newdata = {
            "id": id_from_post,
            'state_id': torino.id
        }

        response = requests.put(self.api_url + '/api/ente_azienda', headers=headers,
                                json=newdata)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(
            torino.id,
            res_data['state_id']['name']
        )

        # delete

        data = {
            "id": id_from_post
        }
        response = requests.delete(
            self.api_url + '/api/ente_azienda', headers=headers, json=data
        )
        self.assertEqual(response.status_code, 200)

    def test_tipo_ente_azienda(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API tipo_ente_azienda
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.tokentech}

        # post
        data = {
            "name": "Tipo prova",
            "description": "Descrizione",
            "is_internal": True,
            "date_start": "2024-01-01",
            "date_end": "2024-12-31"
        }

        response = requests.post(self.api_url + '/api/tipo_ente_azienda',
                                 headers=headers, json=data)
        self.assertEqual(response.status_code, 200)
        id_from_post = response.json().get('id')

        # get
        response = requests.get(self.api_url + '/api/tipo_ente_azienda', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # put
        headers = {
            'token': self.tokentech,
            'active_test': 'True'
        }

        data = {
            "id": id_from_post,
            "name": "Tipo prova",
            "description": "Descrizione",
            "is_internal": False,
            "date_start": "2024-01-01",
            "date_end": "2024-12-31"
        }

        response = requests.put(self.api_url + '/api/tipo_ente_azienda', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # delete

        data = {
            "id": id_from_post
        }
        response = requests.delete(self.api_url + '/api/tipo_ente_azienda',
                                   headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

    def test_img_documento(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API immagine
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.token}

        # post
        data = {
            "ca_persona_id": self.persona_1.id,
            "tipo_documento_id": self.env.ref(
                'inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
            "validity_start_date": "2024-01-01",
            "validity_end_date": "2024-06-20",
            "issued_by": "Comune",
            "document_code": "Codice Doc Persona 1"
        }

        response = requests.post(self.api_url + '/api/documento', headers=headers,
                                 json=data)

        self.assertEqual(response.status_code, 200)
        documento_id = response.json().get('id')
        ca_tipo_documento_id = response.json().get('tipo_documento_id').get("name")
        side = response.json().get('side', 'fronte')

        # post
        data = {
            "name": "Name",
            "description": "Description",
            "ca_tipo_documento_id": ca_tipo_documento_id,
            "side": side,
            "image": "b'RnJvbnRlIDE='",
            "filename": "immagine.png",
            "ca_documento_id": documento_id
        }

        response = requests.post(self.api_url + '/api/immaginedoc', headers=headers,
                                 json=data)
        self.assertEqual(response.status_code, 200)
        id_from_post = response.json().get('id')

        # get
        response = requests.get(self.api_url + '/api/immaginedoc', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # put

        data = {
            "id": id_from_post,
            "name": "Name",
            "description": "Description",
            "ca_tipo_documento_id": ca_tipo_documento_id,
            "side": side,
            "image": "b'RnJvbnRlIDE='",
            "filename": "immagine.png",
            "ca_documento_id": documento_id
        }

        response = requests.put(self.api_url + '/api/immaginedoc', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # delete

        data = {
            "id": response.json().get('id')
        }
        response = requests.delete(self.api_url + '/api/immaginedoc', headers=headers,
                                   json=data)
        self.assertEqual(response.status_code, 200)

        # delete documento
        headers = {
            'token': self.token,
            'active_test': 'True'
        }

        data = {
            "id": documento_id
        }
        response = requests.delete(self.api_url + '/api/documento', headers=headers,
                                   json=data)
        self.assertEqual(response.status_code, 200)

    def test_lettore(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API lettore
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.tokentech}

        # post
        data = {
            "name": self.lettore_1.name,
            "reader_ip": "127.0.0.1",
            "direction": "In",
            "device_id": "Device ID",
            "type": "Type",
            "mode": "Mode",
            "mode_type": "Mode Type",
            "reader_status": "Reader Status",
            "available_events": 3,
            "error_code": "0000"
        }

        response = requests.post(self.api_url + '/api/lettore', headers=headers,
                                 json=data)

        self.assertEqual(response.status_code, 200)
        id_from_post = response.json()['body'].get('id')

        # get
        response = requests.get(self.api_url + '/api/lettore', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # put
        headers = {
            'token': self.tokentech,
            'active_test': 'True'
        }

        data = {
            "id": id_from_post,
            "name": self.lettore_1.name,
            "reader_ip": "127.0.0.1",
            "direction": "In",
            "device_id": "Device ID",
            "type": "Type",
            "mode": "Mode",
            "mode_type": "Mode Type",
            "reader_status": "Reader Status",
            "available_events": 3,
            "error_code": "0000"
        }

        response = requests.put(self.api_url + '/api/lettore', headers=headers,
                                json=data)
        self.assertEqual(response.status_code, 200)

        # delete
        headers = {
            'token': self.tokentech,
            'active_test': 'True'
        }

        data = {
            "id": response.json()['body'].get('id')
        }
        response = requests.delete(self.api_url + '/api/lettore', headers=headers,
                                   json=data)
        self.assertEqual(response.status_code, 200)

    def test_richiesta_registro_accesso_sede(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST, PUT e DELETE della API richiesta_registro_accesso_sede
            creando un record di test che verrà aggiornato e poi eliminato.
            :return: Status code 200.
        """
        headers = {'token': self.token}

        # post
        data = {
            "persona_id": self.persona_1.token,
            "ente_azienda_id": self.ente_azienda_1.id,
            "punto_accesso_id": self.punto_accesso_1p001.id,
            "datetime_event": "3333-12-31 00:00:00"
        }
        response = requests.post(self.api_url + '/api/richiesta_registro_accesso_sede',
                                 headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

        # get
        response = requests.get(self.api_url + '/api/richiesta_registro_accesso_sede',
                                headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

        # put
        data = {
            "id": response.json()['body'][0]['id'],
            "persona_id": self.persona_1.token,
            "ente_azienda_id": self.ente_azienda_1.id,
            "punto_accesso_id": self.punto_accesso_1p001.id,
            "datetime_event": "3333-12-21 00:00:00"
        }
        response = requests.put(self.api_url + '/api/richiesta_registro_accesso_sede',
                                headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

        # delete
        data = {
            "id": response.json()['body'].get('id')
        }
        response = requests.delete(self.api_url + '/api/richiesta_registro_accesso_sede',
                                   headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

    def test_spazio(self):
        """
        Descrizione:
            Verifica il funzionamento delle richieste POST e PUT della API spazio
            creando un record di test per poi aggiornarlo.
            :return: Status code 200.
        """
        headers = {'token': self.tokentech}

        # post
        data = {
            "name": "Spazio prova",
            "tipo_spazio_id": "Piano",
            "ente_azienda_id": self.ente_azienda_1.id,
            "lettore_id": self.lettore_1.id,
            "date_start": "2024-07-01",
            "date_end": "2024-07-31",
            "righe_persona_ids": [
                {
                    "spazio_id": self.spazio_1.id,
                    "tag_persona_id": self.ca_tag_persona_id.token,
                    "date_start": "2024-07-01",
                    "date_end": "2024-07-31",
                    "suspended": "False"
                }
            ]
        }

        response = requests.post(self.api_url + '/api/spazio', headers=headers,
                                 json=data)
        self.assertEqual(response.status_code, 200)
        id_from_post = response.json()['body'].get('id')
        id_persona_ids = response.json()['body']['righe_persona_ids'][0]['id']

        # get
        response = requests.get(self.api_url + '/api/spazio', headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

        # put
        headers = {
            'token': self.tokentech,
            'active_test': 'True'
        }

        data = {
            "id": id_from_post,
            "name": "Spazio prova",
            "tipo_spazio_id": "Piano",
            "ente_azienda_id": self.ente_azienda_1.id,
            "lettore_id": self.lettore_1.id,
            "date_start": "2024-07-01",
            "date_end": "2024-07-31",
            "righe_persona_ids": [
                {
                    "id": id_persona_ids,
                    "spazio_id": self.spazio_1.id,
                    "tag_persona_id": self.ca_tag_persona_id.token,
                    "date_start": "2024-07-01",
                    "date_end": "2024-07-31",
                    "suspended": "False"
                }
            ]
        }

        response = requests.put(self.api_url + '/api/spazio', headers=headers, json=data)
        self.assertEqual(response.status_code, 200)

        # delete
        headers = {
            'token': self.tokentech,
            'active_test': 'True'
        }

        data = {
            "id": response.json()['body'].get('id')
        }
        response = requests.delete(self.api_url + '/api/spazio', headers=headers,
                                   json=data)
        self.assertEqual(response.status_code, 200)
