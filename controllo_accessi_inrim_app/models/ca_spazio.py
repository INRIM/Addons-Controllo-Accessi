import logging

import requests
from odoo import models

logger = logging.getLogger(__name__)
get_rooms_path = '/api/get_rooms'


class CaSpazio(models.Model):
    _inherit = 'ca.spazio'

    def _cron_people_get_rooms(self):
        people_x_key = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.key')
        header = {
            'x-key': people_x_key
        }
        people_url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.url')
        url = f'{people_url}{get_rooms_path}'
        try:
            request = requests.get(url, headers=header)
            if request.status_code == 200:
                logger.info(f"{url}, Status Code: {request.status_code}")
                data = request.json()
                self.get_rooms_data(data)
            else:
                logger.info(f"{url}, Status Code: {request.status_code}")
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{url}, Status Code: {request.status_code}")
            logger.info(e)
            return False

    def get_rooms_data(self, data):
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
                elif dt.get('type_name'):
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
                    else:
                        vals['ente_azienda_id'] = self.env.ref(
                            "controllo_accessi_inrim_app.inrim_campus_cacce").id
                    if vals.get('tipo_spazio_id') and vals.get('ente_azienda_id'):
                        self.create(vals)
