from odoo import models
import logging

logger = logging.getLogger(__name__)
info_path = '/info'
status_path = '/status'

class CaPuntoAccesso(models.Model):
    _inherit = 'ca.punto_accesso'

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

    def post_rfid_status(self, device, data):
        try:
            punto_accesso_id = self.env['ca.punto_accesso'].search([
                ('ca_lettore_id.reader_ip', '=', device)
            ], limit=1)
            if punto_accesso_id:
                vals = {}
                if 'status' in data:
                    if data.get('status') == True:
                        vals['system_error'] = False
                    else:
                        vals['system_error'] = True
                if 'diagnostic' in data:
                    if 'event_cnt' in data['diagnostic']:
                        vals['available_events'] = data['diagnostic']['event_cnt']
                if vals:
                    punto_accesso_id.ca_lettore_id.write(vals)
                return True
            else:
                logger.info(f'{status_path}, ID Dispositivo non trovato {device}')
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{status_path}, Error: {e}")
            logger.info(e)
            return False