import json
import logging
import os
import shutil
from datetime import datetime

import requests
from odoo import models, fields

logger = logging.getLogger(__name__)
info_path = '/info'
status_path = '/status'
read_events_path = '/read-events'
add_tags_path = '/add-tags'


class CaPuntoAccesso(models.Model):
    _inherit = 'ca.punto_accesso'

    def prepare_header(self):
        rfid_token_jwt = self.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.jwt')

        header = {
            'authtoken': rfid_token_jwt
        }
        return header

    def update_rfid_data(self, device):
        try:
            rfid_token_jwt = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.jwt')
            header = {
                'authtoken': rfid_token_jwt
            }
            body = {
                'device': device
            }
            rfid_url = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.url')
            info_url = f'{rfid_url}{info_path}'
            status_url = f'{rfid_url}{status_path}'
            info_request = requests.post(info_url, headers=header, json=body,
                                         verify=False)
            if info_request.status_code == 200:
                logger.info(f"{info_url}, Status Code: {info_request.status_code}")
                self.post_rfid_info(device, info_request.json())
            else:
                logger.info(f"{info_url}, Status Code: {info_request.status_code}")
            status_request = requests.post(status_url, headers=header, json=body,
                                           verify=False)
            if status_request.status_code == 200:
                logger.info(f"{status_url}, Status Code: {status_request.status_code}")
                self.post_rfid_status(device, status_request.json())
                self.env.cr.commit()
            else:
                logger.info(f"{status_url}, Status Code: {status_request.status_code}")
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"Error: {e}")

    def post_rfid_info(self, device, data):
        try:
            punto_accesso_id = self.env['ca.punto_accesso'].search([
                ('ca_lettore_id.reader_ip', '=', device)
            ], limit=1)
            if punto_accesso_id:
                vals = {}
                if 'info' in data:
                    if 'deviceId' in data['info']:
                        vals['device_id'] = data['info'].get('deviceId')
                    if 'mode' in data['info']:
                        vals['mode'] = data['info'].get('mode')
                    if 'modeCode' in data['info']:
                        vals['mode_type'] = data['info'].get('modeCode')
                    if 'readerType' in data['info']:
                        vals['type'] = data['info'].get('readerType')
                if vals:
                    punto_accesso_id.ca_lettore_id.write(vals)
                return True
            else:
                logger.info(f'{info_path}, ID Dispositivo non trovato {device}')
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{info_path}, Error: {e}")
            return False

    # check_reader
    def post_rfid_status(self, device, data):
        try:
            punto_accesso_id = self.env['ca.punto_accesso'].search([
                ('ca_lettore_id.reader_ip', '=', device)
            ], limit=1)
            if punto_accesso_id:
                vals = {}
                vals_punto_accesso = {}
                if 'status' in data:
                    if data.get('status') == True:
                        vals['system_error'] = False
                    else:
                        vals['system_error'] = True
                if 'diagnostic' in data:
                    if 'event_cnt' in data['diagnostic']:
                        vals['available_events'] = data['diagnostic']['event_cnt']
                        vals_punto_accesso['events_to_read_num'] = data['diagnostic'][
                                                                       'event_cnt'] + punto_accesso_id.events_to_read_num
                if vals:
                    punto_accesso_id.ca_lettore_id.write(vals)
                if vals_punto_accesso:
                    punto_accesso_id.write(vals_punto_accesso)
                return True
            else:
                logger.info(f'{status_path}, ID Dispositivo non trovato {device}')
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{status_path}, Error: {e}")
            logger.info(e)
            return False

    def add_tags(
            self, punto_accesso_id, holidayTableCountry,
            holidayTableCity, holidayTable=False
    ):
        device = punto_accesso_id.ca_lettore_id.reader_ip
        body = {
            'device': device,
            'holidayTable': holidayTable,
            'holidayTableCountry': holidayTableCountry,
            'holidayTableCity': holidayTableCity,
            'tags': [],
            'timeZoneTable': [],
        }
        punto_accesso_id = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device),
            ('remote_update', '=', True)
        ], limit=1)
        if punto_accesso_id:
            for tag in punto_accesso_id.ca_tag_lettore_ids:
                body['tags'].append({
                    'idd': tag.ca_tag_id.tag_code,
                    'timezoneConfig': tag.ca_tag_id.timezone_config or '1000000000000000'
                })
            timezone_table = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.timezone_table')
            timezone_table = json.loads(timezone_table)
            body['timeZoneTable'] = json.dumps(timezone_table)
        return body

    def post_add_tags(
            self, device, holidayTableCountry,
            holidayTableCity, holidayTable=False
    ):
        try:
            rfid_token_jwt = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.jwt')
            rfid_url = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.url')
            header = {
                'authtoken': rfid_token_jwt
            }
            punto_accesso_id = self.env['ca.punto_accesso'].search([
                ('ca_lettore_id.reader_ip', '=', device),
                ('remote_update', '=', True)
            ], limit=1)
            if punto_accesso_id:
                body = self.add_tags(
                    punto_accesso_id, holidayTableCountry,
                    holidayTableCity, holidayTable
                )
                add_tags_url = f'{rfid_url}{add_tags_path}'
                add_tags_request = requests.post(add_tags_url, headers=header, json=body,
                                                 verify=False)
                if add_tags_request.status_code == 200:
                    punto_accesso_id.remote_update = False
                    logger.info(
                        f"{add_tags_url}, Status Code: {add_tags_request.status_code}")
                    return True
                else:
                    logger.info(
                        f"{add_tags_url}, Status Code: {add_tags_request.status_code}")
                    return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f'Error: {e}')
            return False

    def events_save_json(self, data, punto_accesso, datetime_now):
        json_data = json.dumps(data, indent=4)
        modulo_path = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(modulo_path, '..', 'data', 'TODO')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        name = punto_accesso.ca_lettore_id.name.replace(' ', '_')
        CodAtt = datetime_now.timestamp()
        json_file_path = os.path.join(data_dir, f'{str(CodAtt)}_{name}.json')
        with open(json_file_path, 'w') as json_file:
            json_file.write(json_data)
        punto_accesso.last_reading_events = datetime_now
        if data.get('eventRecords'):
            for record in data['eventRecords']:
                if record.get('eventDateTime'):
                    punto_accesso.last_update_reader = (
                        datetime.strptime(
                            record.get('eventDateTime'),
                            '%Y-%m-%dT%H:%M:%S'
                        )
                    )
                for tag in punto_accesso.ca_tag_lettore_ids:
                    if record.get('idd'):
                        if tag.ca_tag_id.tag_code == record['idd']:
                            if record.get('errorCode'):
                                tag.ca_lettore_id.error_code = record.get('errorCode')
            punto_accesso.ca_lettore_id.available_events -= len(data['eventRecords'])
            punto_accesso.events_read_num += len(data['eventRecords'])

    def post_read_events(self, punto_accesso, datetime_now):
        try:
            rfid_token_jwt = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.jwt')
            header = {
                'authtoken': rfid_token_jwt
            }
            body = {
                'device': punto_accesso.ca_lettore_id.reader_ip,
                'numberEvents': punto_accesso.ca_lettore_id.available_events
            }
            rfid_url = self.env[
                'ir.config_parameter'
            ].sudo().get_param('service_reader.url')
            read_events_url = f'{rfid_url}{read_events_path}'
            read_events_request = requests.post(read_events_url, headers=header,
                                                json=body, verify=False)
            if read_events_request.status_code == 200:
                data = read_events_request.json()
                self.events_save_json(data, punto_accesso, datetime_now)
            else:
                logger.info(
                    f"{read_events_url}, Status Code: {read_events_request.status_code}")
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f'Error: {e}')
            return False

    def read_json_file(self, punto_accesso, datetime_now):
        todo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'TODO')
        err_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ERR')
        done_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'DONE')
        if not os.path.exists(todo_path):
            raise FileNotFoundError(f"La cartella {todo_path} non esiste.")
        json_files = [f for f in os.listdir(todo_path) if f.endswith('.json')]
        for json_file in json_files:
            file_path = os.path.join(todo_path, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('eventRecords'):
                        for record in data['eventRecords']:
                            if record.get('idd'):
                                tag_id = self.env['ca.tag'].search([
                                    ('tag_code', '=', record['idd'])
                                ], limit=1)
                                tag_ids = self.env['ca.tag_lettore'].search([
                                    ('ca_punto_accesso_id', '=', punto_accesso.id)
                                ]).mapped('ca_tag_id')
                                if tag_id and tag_ids and tag_id in tag_ids:
                                    tag_persona_id = self.env['ca.tag_persona'].search([
                                        ('ca_tag_id', '=', tag_id.id),
                                        ('date_start', '<=', fields.date.today()),
                                        ('date_end', '>=', fields.date.today())
                                    ])
                                    if tag_persona_id:
                                        self.env['ca.anag_registro_accesso'].create({
                                            'ca_punto_accesso_id': punto_accesso.id,
                                            'ca_tag_persona_id': tag_persona_id.id,
                                            'type': 'auto'
                                        })
                                        if not os.path.exists(done_path):
                                            os.makedirs(done_path)
                                        done_file_path = os.path.join(done_path,
                                                                      json_file)
                                        shutil.move(file_path, done_file_path)
                                        logger.info(f'Lettura file: {json_file}, OK')
                                        self.env['ca.log_integrazione_lettori'].create({
                                            'activity_code': datetime_now.timestamp(),
                                            'datetime': datetime_now,
                                            'ca_lettore_id': punto_accesso.ca_lettore_id.id,
                                            'operation_status': 'ok',
                                            'error_code': punto_accesso.ca_lettore_id.error_code
                                        })
            except json.JSONDecodeError as e:
                if not os.path.exists(err_path):
                    os.makedirs(err_path)
                err_file_path = os.path.join(err_path, json_file)
                shutil.move(file_path, err_file_path)
                logger.info(f'Lettura file: {json_file}, KO')
                self.env['ca.log_integrazione_lettori'].create({
                    'activity_code': datetime_now.timestamp(),
                    'datetime': datetime_now,
                    'ca_lettore_id': punto_accesso.ca_lettore_id.id,
                    'operation_status': 'ko',
                    'log_error': e,
                    'error_code': punto_accesso.ca_lettore_id.error_code
                })

    def sync_reader_data(
            self, device, holidayTableCountry,
            holidayTableCity, holidayTable=False
    ):
        punto_accesso_ids = self.env['ca.punto_accesso'].search([
            ('ca_lettore_id.reader_ip', '=', device),
            ('system_error', '=', False),
            ('enable_sync', '=', True),
            ('direction', '=', 'in')
        ])
        datetime_now = datetime.now()
        logger.info(f'Codice Attività: {datetime_now.timestamp()}')
        for punto_accesso in punto_accesso_ids:
            self.update_rfid_data(punto_accesso.ca_lettore_id.reader_ip)
            if punto_accesso.ca_lettore_id.available_events > 0:
                self.post_read_events(punto_accesso, datetime_now)
            self.post_add_tags(
                device, holidayTableCountry,
                holidayTableCity, holidayTable
            )
            self.read_json_file(punto_accesso, datetime_now)

    def sync_readers_data(
            self, holidayTableCountry,
            holidayTableCity, holidayTable=False
    ):
        punto_accesso_ids = self.env['ca.punto_accesso'].search([])
        for punto_accesso in punto_accesso_ids:
            self.sync_reader_data(
                punto_accesso.ca_lettore_id.reader_ip, holidayTableCountry,
                holidayTableCity, holidayTable
            )

    def check_readers(self):
        punto_accesso_ids = self.env['ca.punto_accesso'].search([])
        for punto_accesso in punto_accesso_ids:
            self.update_rfid_data(punto_accesso.ca_lettore_id.reader_ip)
