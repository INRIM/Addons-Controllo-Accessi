import json
import logging
from datetime import datetime

import requests
from odoo import models, api, fields

logger = logging.getLogger(__name__)

# get_addressbook_path = "/api/get_addressbook"
get_personal_types = "/api/getpersonaltypes"
get_job_titles = "/api/get_job_titles"
get_users = "/api/pf/elaboraFileCF"

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
        request = None
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
                f"{url}, Status Code: {request.status_code if request else ''}, {e}", exc_info=True)
            return False

    def get_syncusers(self, url_path):
        token = self.env[
            'ir.config_parameter'
        ].sudo().get_param('syncusers_service_token')
        base_url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('syncusers_service_url')
        headers = {
            'xdvr': token
        }
        url = f'{base_url}{url_path}'
        request = None
        try:
            request = requests.get(url, headers=headers)
            if request.status_code == 200:
                logger.info(f"{url}, Status Code: {request.status_code}")
                data = request.json()
                return data
            else:
                logger.info(f"{url}, Status Code: {request.status_code}")
                return []
        except Exception as e:
            logger.error(
                f"{url}, Status Code: {request.status_code if request else ''}, {e}", exc_info=True)
            return []

    @api.model
    def _cron_people_get_addressbook(self):
        with self.env.cr.savepoint():
            for upath in [get_personal_types, get_job_titles]:
                data = self.get_people_data(upath)
                if data and upath == get_personal_types:
                    self.update_work_info_type(data)
                if data and upath == get_job_titles:
                    self.update_titolo_persona(data)
            for xpath in [get_users]:
                data = self.get_syncusers(xpath)
                if data and xpath == get_users:
                    ...

    def update_work_info_type(self, data):
        logger.info("Update tipo persona work_info_type")
        payrolls = json.loads(self.env['ir.config_parameter'].sudo().get_param(
            'inrim_payroll_types'))
        with self.env.cr.savepoint():
            try:
                for dt in data:
                    if dt.get('code') and dt.get('name'):
                        work_info_type_id = self.env['ca.work_info_type'].search([
                            ('code', '=', dt.get('code'))
                        ], limit=1)
                        if not work_info_type_id:
                            vals = {
                                'name': dt['name'],
                                'code': dt['code'],
                                'structured': dt['code'] not in payrolls
                            }
                            res = self.env['ca.work_info_type'].create(vals)
                        else:
                            work_info_type_id.name = dt['name']
                            work_info_type_id.structured = dt['code'] in payrolls
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)

    def update_titolo_persona(self, data):
        logger.info("Update titolo persona")
        with self.env.cr.savepoint():
            try:
                for dt in data:
                    if dt.get('code') and dt.get('name'):
                        titolo_persona_id = self.env['ca.titolo_persona'].search([
                            ('code', '=', dt.get('code'))
                        ], limit=1)
                        if not titolo_persona_id:
                            vals = {
                                'name': dt['name'],
                                'code': dt['code'],
                                'structured': True
                            }
                            self.env['ca.titolo_persona'].create(vals)
                        else:
                            titolo_persona_id.name = dt['name']
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)

    def get_addressbook_data(self, data):
        logger.info("Update persona")
        # internal_types = self.env.ref('default_ca.internal_people_types')

        internal_types = json.loads(self.env['ir.config_parameter'].sudo().get_param(
            'default_ca.inrim_payroll_types'))
        ext_company = 'ditteesterne_tipopersonale'
        ext_entity = 'entiesterni_tipopersonale'
        base_institute = self.env.ref(
            'controllo_accessi_inrim_app.inrim_campus_cacce')
        base_default_ente_todo = self.env.ref(
            'controllo_accessi_inrim_app.inrim_ente_esterno_da_gestire')
        base_default_azienda_todo = self.env.ref(
            'controllo_accessi_inrim_app.inrim_azienda_esterna_da_gestire')
        interno = self.env.ref(
            'inrim_anagrafiche.tipo_persona_interno').id
        esterno = self.env.ref(
            'inrim_anagrafiche.tipo_persona_esterno').id
        date_end_forever = self.env.ref(
            'inrim_controllo_accessi.inrim_ir_config_parameter_forever').value
        with self.env.cr.savepoint():
            for dt in data:
                try:
                    azienda_ids = []
                    if dt.get('uid') and dt.get('name') and dt.get(
                            'tipo_personale') != "":
                        user_id = self.env['res.users'].search([
                            ('login', '=', dt['uid'])
                        ], limit=1)
                        type_ids = []
                        title_ids = []

                        if not user_id:
                            user_id = self.env['res.users'].create({
                                'name': dt['name'],
                                'login': dt['uid'],
                                'company_id': self.env.company.id,
                                'lang': 'it_IT',
                                "tz": "Europe/Rome"
                            })
                        work_info_type_id = self.env['ca.work_info_type'].get_by_name(
                            dt.get('tipo_personale'))

                        persona_id = self.env['ca.persona'].with_context(
                            massive_create=True).search([
                            ('fiscalcode', '=', dt['codicefiscale'])
                        ], limit=1)
                        resp_id = self.get_by_login_uid(dt.get("referente_uid"))
                        if not resp_id:
                            resp_id = self.with_context(
                                massive_create=True).get_by_login_uid(
                                dt.get("responsabile_uid"))
                        if work_info_type_id:
                            if work_info_type_id.code in internal_types:
                                type_ids.append(interno)
                                azienda_ids.append(base_institute.id)
                            else:
                                type_ids.append(esterno)
                                if work_info_type_id.code == ext_company:
                                    azienda_ids.append(base_default_azienda_todo.id)
                                elif work_info_type_id.code == ext_entity:
                                    azienda_ids.append(base_default_ente_todo.id)

                        if not persona_id:
                            birth_date = ''
                            if dt.get('data_di_nascita'):
                                birth_date = datetime.strptime(
                                    dt['data_di_nascita'], '%Y-%m-%d').date()
                            if dt.get('nome') and dt.get('cognome'):
                                vals = {
                                    'uid': dt['uid'],
                                    'name': dt['nome'],
                                    'lastname': dt['cognome'],
                                    'email': dt['mail'],
                                    'mobile': dt['cell_phone_service'],
                                    'private_mobile': dt['private_cell_phone'],
                                    'phone': dt['telephonNumber'],
                                    'type_ids': type_ids,
                                    'birth_date': birth_date,
                                    'ca_ente_azienda_ids': azienda_ids,
                                    'associated_user_id': user_id.id,
                                    'parent_id': resp_id.id if resp_id else False
                                }
                                if dt.get('matricola'):
                                    vals['freshman'] = dt['matricola']
                                if dt.get('codicefiscale'):
                                    vals['fiscalcode'] = dt['codicefiscale']
                                persona_id = self.with_context(
                                    massive_create=True).create(vals)
                                persona_id.action_completed()

                        else:
                            if not persona_id.parent_id:
                                resp_id = self.with_context(
                                    massive_create=True).get_by_login_uid(
                                    dt.get("referente_uid"))
                                if not resp_id:
                                    resp_id = self.with_context(
                                        massive_create=True).get_by_login_uid(
                                        dt.get("responsabile_uid"))
                                persona_id.parent_id = resp_id.id if resp_id else False
                        title_id = self.env['ca.titolo_persona'].get_by_name(
                            dt.get('qualifica'))
                        vals = {
                            'ca_persona_id': persona_id.id,
                            'work_id_number': dt['matricola'],
                            'ca_div_uo_code': dt['divisione_code'],
                            'ca_work_info_type_id': work_info_type_id.id if work_info_type_id else False,
                            'ca_title_id': title_id.id if title_id else False,
                        }
                        if dt.get('data_inizio'):
                            vals['date_start'] = fields.Date.to_date(
                                dt['data_inizio'])
                        if not dt.get('data_fine'):
                            vals['date_end'] = fields.Date.to_date(
                                date_end_forever.split(" ")[0])
                        else:
                            vals['date_end'] = fields.Date.to_date(
                                dt['data_fine'])
                        curr_winfo = persona_id.get_current_winfo()
                        if (
                                not curr_winfo or
                                not curr_winfo.ca_work_info_type_id.id == work_info_type_id.id or
                                not curr_winfo.ca_title_id.id == title_id.id
                        ):
                            persona_id.with_context(
                                massive_create=True).update_work_info(vals)
                except Exception as e:
                    logger.error(
                        f"Error Skip {dt.get('uid')}: {e}", exc_info=True)
