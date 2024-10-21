from odoo import models
import logging
import requests

logger = logging.getLogger(__name__)
info_path = '/info'
status_path = '/status'

class CaPuntoAccesso(models.Model):
    _inherit = 'ca.punto_accesso'

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
            info_request = requests.post(info_url, headers=header, json=body, verify=False)
            if info_request.status_code == 200:
                logger.info(f"{info_url}, Status Code: {info_request.status_code}")
                self.post_rfid_info(device, info_request.json())
            else:
                logger.info(f"{info_url}, Status Code: {info_request.status_code}")
            status_request = requests.post(status_url, headers=header, json=body, verify=False)
            if status_request.status_code == 200:
                logger.info(f"{status_url}, Status Code: {status_request.status_code}")
                self.post_rfid_status(device, status_request.json())
                self.env.cr.commit()
            else:
                logger.info(f"{status_url}, Status Code: {status_request.status_code}")
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"Error: {e}")