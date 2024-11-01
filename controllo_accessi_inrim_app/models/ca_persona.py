import logging
from datetime import datetime

import requests
from odoo import models, api

logger = logging.getLogger(__name__)

get_addressbook_path = "/api/get_addressbook"
get_personal_types = "/api/getpersonaltypes"


class CaPersona(models.Model):
    _inherit = 'ca.persona'

    def get_people_data(self, url_path):
        people_x_key = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.key')
        header = {
            'x-key': people_x_key
        }
        people_url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.url')
        url = f'{people_url}{url_path}'
        try:
            request = requests.get(url, headers=header)
            if request.status_code == 200:
                logger.info(f"{url}, Status Code: {request.status_code}")
                data = request.json()
                return data
            else:
                logger.info(f"{url}, Status Code: {request.status_code}")
                return False
        except Exception as e:
            logger.error(
                f"{url}, Status Code: {request.status_code}, {e}", exc_info=True)
            return False

    @api.model
    def _cron_people_get_addressbook(self):
        with self.env.cr.savepoint():
            tipo_data = self.get_people_data(get_personal_types)
            if tipo_data:
                self.update_tipo_persona(tipo_data)
            data = self.get_people_data(get_addressbook_path)
            if data:
                self.get_addressbook_data(data)

    def update_tipo_persona(self, data):
        logger.info("Update tipo persona")
        with self.env.cr.savepoint():
            try:
                for dt in data:
                    if dt.get('code') and dt.get('name'):
                        tipo_persona_id = self.env['ca.tipo_persona'].search([
                            ('code', '=', dt.get('code'))
                        ])
                        if not tipo_persona_id:
                            vals = {
                                'name': dt['name'],
                                'code': dt['code'],
                                'structured': True
                            }
                            self.create(vals)
                        else:
                            tipo_persona_id.name = dt['name']
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)

    def get_addressbook_data(self, data):
        logger.info("Update persona")
        with self.env.cr.savepoint():
            try:
                for dt in data:
                    if dt.get('uid') and dt.get('name'):
                        user_id = self.env['res.users'].search([
                            ('login', '=', dt['uid'])
                        ])
                        if not user_id:
                            user_id = self.env['res.users'].create({
                                'name': dt['name'],
                                'login': dt['uid'],
                                'company_id': self.env.company.id
                            })
                        persona_id = self.env['ca.persona'].search([
                            ('freshman', '=', dt['matricola']),
                            ('fiscalcode', '=', dt['codicefiscale'])
                        ])
                        if not persona_id:
                            birth_date = ''
                            if dt.get('data_di_nascita'):
                                birth_date = datetime.strptime(
                                    dt['data_di_nascita'], '%Y-%m-%d').date()
                            if dt.get('nome') and dt.get('cognome'):
                                vals = {
                                    'name': dt['nome'],
                                    'lastname': dt['cognome'],
                                    'type_ids': self.env.ref(
                                        'inrim_anagrafiche.tipo_persona_interno').ids,
                                    'birth_date': birth_date,
                                    'associated_user_id': user_id.id,
                                }
                                if dt.get('matricola'):
                                    vals['freshman'] = dt['matricola']
                                if dt.get('codicefiscale'):
                                    vals['fiscalcode'] = dt['codicefiscale']
                                persona_id = self.create(vals)
                                persona_id.action_completed()
                        else:
                            tipo_persona_id = self.env['ca.tipo_persona'].search([
                                ('name', '=', dt.get('tipo_personale'))
                            ])
                            if tipo_persona_id:
                                persona_id.type_ids = [
                                    self.env.ref('inrim_anagrafiche.tipo_persona_interno').id,
                                    tipo_persona_id.id
                                ]
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
