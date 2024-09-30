from odoo import models
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class CaLettore(models.Model):
    _inherit = 'ca.lettore'

    def post_rfid_info(self, device): # self.env['ca.lettore'].post_rfid_info('10.10.10.1')
        company_id = self.env.company
        if company_id.enable_rfid:
            rfid_token_jwt = company_id.rfid_token_jwt
            header = {
                'authtoken': rfid_token_jwt
            }
            body = {
                'device': device
            }
            rfid_url = company_id.rfid_url
            rfid_info_path = company_id.rfid_info_path
            info_url = f'{rfid_url}{rfid_info_path}'
            try:
                request = requests.post(info_url, headers=header, json=body, verify=False)
                if request.status_code == 200:
                    logger.info(f"{info_url}, Status Code: {request.status_code}")
                    data = request.json()
                    lettore_id = self.env['ca.lettore'].search([
                        ('reader_ip', '=', device)
                    ], limit=1)
                    if lettore_id:
                        vals = {}
                        if 'status' in data:
                            vals['reader_status'] = str(data.get('status'))
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
                            lettore_id.write(vals)
                            self.env.cr.commit()
                        self.post_rfid_status(device)
                    else:
                        logger.info(f'{info_url}, ID Dispositivo non trovato {device}')
                else:
                    logger.info(f"{info_url}, Status Code: {request.status_code}")
            except Exception as e:
                self.env.cr.rollback()
                logger.info(f"{info_url}, Status Code: {request.status_code}")
                logger.info(e)

    def post_rfid_status(self, device):
        company_id = self.env.company
        if company_id.enable_rfid:
            rfid_token_jwt = company_id.rfid_token_jwt
            header = {
                'authtoken': rfid_token_jwt
            }
            body = {
                'device': device
            }
            rfid_url = company_id.rfid_url
            rfid_status_path = company_id.rfid_status_path
            status_url = f'{rfid_url}{rfid_status_path}'
            try:
                request = requests.post(status_url, headers=header, json=body, verify=False)
                if request.status_code == 200:
                    logger.info(f"{status_url}, Status Code: {request.status_code}")
                    data = request.json()
                    lettore_id = self.env['ca.lettore'].search([
                        ('reader_ip', '=', device)
                    ], limit=1)
                    if lettore_id:
                        vals = {}
                        if 'diagnostic' in data:
                            if 'event_cnt' in data['diagnostic']:
                                vals['available_events'] = data['diagnostic']['event_cnt']
                        if vals:
                            lettore_id.write(vals)
                            self.env.cr.commit()
                    else:
                        logger.info(f'{status_url}, ID Dispositivo non trovato {device}')
                else:
                    logger.info(f"{status_url}, Status Code: {request.status_code}")
            except Exception as e:
                self.env.cr.rollback()
                logger.info(f"{status_url}, Status Code: {request.status_code}")
                logger.info(e)