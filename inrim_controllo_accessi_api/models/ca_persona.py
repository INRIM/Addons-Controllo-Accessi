from odoo import models
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class CaPersona(models.Model):
    _inherit = 'ca.persona'

    def _cron_people_get_addressbook(self):
        if self.env.company.enable_people:
            people_x_key = self.env.company.people_x_key
            header = {
                'x-key': people_x_key
            }
            people_url = self.env.company.people_url
            get_addressbook_path = self.env.company.get_addressbook_path
            url = f'{people_url}{get_addressbook_path}'
            try:
                request = requests.get(url, headers=header)
                if request.status_code == 200:
                    logger.info(f"{url}, Status Code: {request.status_code}")
                    data = request.json()
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
                    logger.info(f"{url}, Status Code: {request.status_code}")
            except Exception as e:
                self.env.cr.rollback()
                logger.info(f"{url}, Status Code: {request.status_code}")
                logger.info(e)