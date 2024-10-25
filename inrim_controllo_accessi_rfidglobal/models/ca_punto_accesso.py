from pathlib import Path

from dateutil import parser
from odoo import models

from .Max5010_rfid_lib import *

logger = logging.getLogger(__name__)
path_files = "/mnt/reader-data"


class CaPuntoAccesso(models.Model):
    _inherit = 'ca.punto_accesso'

    def write_log(
            self, code, lettore_id, expected_events_num=0,
            operation_status="ko", events_read_num=0, error_code=0, msg=""
    ):
        log_model = self.env['ca.log_integrazione_lettori']
        log_model.create({
            'activity_code': code,
            'datetime': datetime.now(),
            'ca_lettore_id': lettore_id,
            'expected_events_num': expected_events_num,
            'events_read_num': events_read_num,
            'operation_status': operation_status,
            'error_code': error_code,
            'log_error': msg,
        })

    def load_reader(self):
        self.ensure_one()
        reader = Max5010RfidClient(
            self.ca_lettore_id.reader_ip,
            self.ente_azienda_id.url_gateway_lettori or "http://local-host",
            self.ente_azienda_id.nome_chiave_header or "authtoken",
            self.ente_azienda_id.jwt or "key"
        )
        try:
            with self.env.cr.savepoint():
                if not self.enable_sync:
                    return reader
                reader.connect()
                vals = {}
                vals['device_id'] = reader.device.info.deviceId
                vals['mode'] = reader.device.info.mode
                vals['mode_type'] = reader.device.info.modeCode
                vals['type'] = reader.device.info.readerType
                vals['available_events'] = reader.device.diagnostic.event_cnt
                if not reader.device.status:
                    vals['system_error'] = True
                self.ca_lettore_id.write(vals)
        except Exception as e:
            logger.info(f"Error: {e}", exc_info=True)
            self.write_log(
                f"CONNECT", self.ca_lettore_id, msg="Reader is OFFLINE")
        finally:
            return reader

    def update_reader_clock(self):
        reader = self.load_reader()
        reader.update_clock()

    def get_tags_boby(self) -> dict:
        timezone_table = self.env[
            'ir.config_parameter'
        ].sudo().get_param('service_reader.timezone_table')
        timezone_table = json.loads(timezone_table)
        tagsBody = {
            "tags": [
                {
                    'idd': tag.ca_tag_id.tag_code,
                    'timezoneConfig': tag.ca_tag_id.timezone_config or '1000000000000000'
                } for tag in self.ca_tag_lettore_ids
            ],
            "timeZoneTable": [item for item in timezone_table]
        }
        return tagsBody

    def get_code_activity(self, prefix):
        return f"{prefix}_AP{self.id}_{self.ca_lettore_id.reader_ip}_{datetime.now().timestamp()}"

    def decode_code(self, code, prefix):
        lst_part = code.split('_')
        if lst_part[0] == prefix:
            punto_accesso_id = int(lst_part[1].replace("AP", ""))
            ip = lst_part[2]
            punto_accesso = self.browse(punto_accesso_id)
            if punto_accesso.id == self.id:
                if punto_accesso.ca_lettore_id.reader_ip == ip:
                    return punto_accesso
        return None

    def update_reader_tags(self):
        self.ensure_one()
        reader = self.load_reader()
        if not self.remote_update or not self.enable_sync or not reader.online:
            return False
        if reader.device.diagnostic.event_cnt > 0:
            return False
        body = self.get_tags_boby()
        activity_code = self.get_code_activity("ADDTAGS")
        logger.info(f"Start updateTags Reader, CodAtt: {activity_code}")
        try:
            with self.env.cr.savepoint():
                res: ActionResponse = reader.write_tags(body)
                if not res.result:
                    msg = f'update_tags, {self.name} Result: {res.result}, hint: check events numebr'
                    logger.error(msg)
                    self.system_error = True
                    self.write_log(
                        activity_code, self.ca_lettore_id.id, msg=msg
                    )
                self.last_update_reader = datetime.now()
                return activity_code
        except Exception as e:
            msg = f'update_tags, {e}'
            logger.exception(msg, exc_info=True)
            self.write_log(
                activity_code, self.ca_lettore_id.id, msg=msg
            )
            return False

    def save_events_to_json(self):
        self.ensure_one()
        reader = self.load_reader()
        if not self.enable_sync or not reader.online:
            return False
        activity_code = self.get_code_activity("READEVNT")
        logger.info(f"Start save events from Reader, CodAtt: {activity_code}")
        data_dir = path_files
        nume_envts = self.events_to_read_num or 1
        reads = True
        count = nume_envts
        try:
            with self.env.cr.savepoint():
                while reads:
                    res = reader.read_and_save_events(
                        nume_envts, data_dir, f'{activity_code}_{count}.json', "TODO")
                    if res.is_error():
                        msg = f"events_save_json: {activity_code}: {res.status} - {res.statusStr}"
                        logger.error(msg)
                        self.write_log(
                            activity_code, self.ca_lettore_id.id, msg=msg
                        )
                    reads = self.recursive_read_events
                    if reads:
                        reads = res.hasMore
                        count += nume_envts

                self.last_reading_events = datetime.now()
                self.events_read_num = count
                return activity_code

        except Exception as e:
            msg = f'Exception in events_save_json: {activity_code}: Err: , {e}'
            logger.exception(msg)
            self.write_log(
                activity_code, self.ca_lettore_id.id, expected_events_num=nume_envts,
                msg=msg
            )
            return False

    def decode_data(self, code, file_path):
        try:
            with self.env.cr.savepoint():
                logger.info(f"Decode data from file Task:{code} - File: {file_path}")
                events: EventsResponse = Max5010RfidClient.load_events_from_file(
                    file_path)
                riga_accesso_model = self.env['ca.anag_registro_accesso']
                if events.eventRecords:
                    for record in events.eventRecords:
                        self.ca_lettore_id.error_code = record.errorCode
                        tag = self.ca_tag_lettore_ids.filtered(
                            lambda x: x.ca_tag_id.tag_code == record.idd)
                        if tag:
                            tag_persona = self.env['ca.tag_persona'].search([
                                ('ca_tag_id.id', '=', tag.id),
                                ('tag_in_use', '=', True)])
                            if tag_persona:
                                riga_accesso_model.aggiungi_riga_accesso(
                                    self, tag_persona,
                                    parser.parse(record.eventDateTime),
                                    type="auto",
                                    access_allowed=record.accessAllowed
                                )
                                return True
                            else:
                                logger.error(
                                    f"tag {record.idd} not associated with no one ")
                                return False
                        else:
                            logger.error(
                                f"tag  {record.idd} not found ")
                            return False
                else:
                    logger.error(
                        f"Error read event file ")
                    return False
        except Exception as e:
            msg = f'Exception in decode event: {code}, File: {file_path}, Err: {e}'
            logger.exception(msg)
            self.write_log(
                code, self.ca_lettore_id.id, msg=msg
            )
            return False

    def events_process_todo(self):
        self.ensure_one()
        logger.info(f"Start process events from Access Point {self.name} - id {self.id}")
        todo = Path(f'{path_files}/TODO')
        found = 0
        done = 0
        err = 0
        skip = 0
        code = self.get_code_activity("LOADEVNT")
        for file_path in todo.glob('*.json'):
            found += 1
            punto_accesso = self.decode_code(file_path.stem, "READEVNT")
            logger.info(f"Decode data from file Task {file_path}")
            if punto_accesso:
                done_dst = Path(f'{path_files}/DONE/{file_path.name}')
                err_dst = Path(f'{path_files}/ERR/{file_path.name}')
                if self.decode_data(code, file_path):
                    file_path.rename(done_dst)
                    done += 1
                    logger.info(f"{code} - file: {file_path} Done")
                else:
                    err += 1
                    file_path.rename(err_dst)
                    logger.error(
                        f"{code} - File  {file_path.name} error impossible to decode Data moved to {err_dst} ")
            else:
                skip += 1
                logger.info(
                    f"{code} Skip File {file_path.name} not for this Access Point {self.id}")
        logger.info(
            f"Complete all tasks for Job events_process_todo: Found: {found} files, {done} done, {skip} skipped, {err} error")

    # super methods
    def check_readers(self):
        res = super().check_readers()
        for point in self.env['ca.punto_accesso'].search([('enable_sync', '=', True)]):
            point.load_reader()
        return True

    def load_readers_data(self):
        res = super().load_readers_data()
        for point in self.env['ca.punto_accesso'].search([('enable_sync', '=', True)]):
            point.save_events_to_json()
        return True

    def eval_readers_data(self):
        res = super().events_process_todo()
        for point in self.env['ca.punto_accesso'].search([('enable_sync', '=', True)]):
            point.events_process_todo()
        return True

    def update_readers_data(self):
        res = super().update_readers_data()
        for point in self.env['ca.punto_accesso'].search([('enable_sync', '=', True)]):
            point.update_reader_tags()
        return True

    def update_clock(self):
        res = super().update_clock()
        for point in self.env['ca.punto_accesso'].search([('enable_sync', '=', True)]):
            point.update_reader_clock()
        return True
