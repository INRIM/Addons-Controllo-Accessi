from odoo import models
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class CaSpazio(models.Model):
    _inherit = 'ca.spazio'

    def _cron_people_get_rooms(self):
        if self.env.company.enable_people:
            people_x_key = self.env.company.people_x_key
            header = {
                'x-key': people_x_key
            }
            people_url = self.env.company.people_url
            get_rooms_path = self.env.company.get_rooms_path
            url = f'{people_url}{get_rooms_path}'
            try:
                request = requests.get(url, headers=header)
                if request.status_code == 200:
                    logger.info(f"{url}, Status Code: {request.status_code}")
                    data = request.json()
                    for dt in data:
                        if dt.get('name'):
                            spazio_id = self.search([
                                ('name', '=', dt['name'])
                            ], limit=1)
                            if spazio_id:
                                if dt.get('type_name'):
                                    tipo_spazio_id = self.env['ca.tipo_spazio'].search([
                                        ('name', '=', dt['type_name'])
                                    ], limit=1)
                                    if tipo_spazio_id:
                                        spazio_id.tipo_spazio_id = tipo_spazio_id.id
                                if dt.get('institution_address_ref'):
                                    ente_azienda_id = self.env['ca.ente_azienda'].search([
                                        ('ref', '=', dt['institution_address_ref'])
                                    ], limit=1)
                                    if ente_azienda_id:
                                        spazio_id.ente_azienda_id = ente_azienda_id.id
                            elif dt.get('institution_address_ref') and dt.get('type_name'):
                                vals = {
                                    'name': dt['name']
                                }
                                tipo_spazio_id = self.env['ca.tipo_spazio'].search([
                                    ('name', '=', dt['type_name'])
                                ], limit=1)
                                if tipo_spazio_id:
                                    vals['tipo_spazio_id'] = tipo_spazio_id.id
                                ente_azienda_id = self.env['ca.ente_azienda'].search([
                                    ('ref', '=', dt['institution_address_ref'])
                                ], limit=1)
                                if ente_azienda_id:
                                    vals['ente_azienda_id'] = ente_azienda_id.id
                                if vals.get('tipo_spazio_id') and vals.get('ente_azienda_id'):
                                    self.create(vals)
                else:
                    logger.info(f"{url}, Status Code: {request.status_code}")
            except Exception as e:
                self.env.cr.rollback()
                logger.info(f"{url}, Status Code: {request.status_code}")
                logger.info(e)