import json
import logging
from datetime import datetime, timedelta

import requests
from odoo import models, api, fields
from odoo.addons.test_convert.tests.test_env import record

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
                f"{url}, Status Code: {request.status_code if request else ''}, {e}",
                exc_info=True)
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
                f"{url}, Status Code: {request.status_code if request else ''}, {e}",
                exc_info=True)
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
                    if len(data) > 0:
                        for item in data:
                            for k in item:
                                records = item[k]
                                if records:
                                    self.fetch_users_data(records)

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

    def fetch_users_data(self, items):
        logger.info(f"decode_users_data {len(items)}")
        no_match = []
        errors = []
        complete = []
        for elem in items:
            if elem.get('pf') and elem.get('people'):
                res = self.eval_user_data(elem)
                if res:
                    complete.append(elem.get('matricola'))
                else:
                    errors.append(elem.get('matricola'))
            else:
                self.make_user_todo(elem)
                no_match.append(elem.get('matricola'))
        logger.info(f"decode_users_data Recap:")
        logger.info(f"{len(no_match)} in progress")
        logger.info(f"{len(errors)} in errors")
        logger.info(f"{len(complete)} complete")
        logger.info(f"-------------------------")
        logger.info(f"errors serials: {errors}")
        logger.info(f"-------------------------")
        logger.info(f"no match serials: {no_match}")
        logger.info(f"-------------------------")

    def eval_user_data(self, item):
        logger.info(f"eval_user_data {item.get('matricola')}")
        try:
            person_data = {}
            codice_fiscale = self.get_from_record(
                item, ['codiceFiscale', 'codiceFiscaleEstero', 'codicefiscale'], ""
            )
            if not codice_fiscale:
                return False
            self.make_user(item)
            return True
        except Exception as e:
            logger.error(
                f" {item.get('matricola')}, {e}",
                exc_info=True)
            return False

    def to_date(self, val, default=None):
        try:
            return datetime.fromisoformat(val).date()
        except Exception as e:
            return default

    def decode_cadaster(self, record, key, keyret, default=None):
        pf = record.get('pf', {})
        comuni = record.get('comune', {})
        if comuni and pf:
            value = pf.get(key)
            for c in comuni:
                dtc = self.to_date(c.get('dataCessazione'), datetime.today().date())
                if dtc > datetime.today().date() and c.get('codCatasto', "") == value:
                    if keyret == 'city':
                        return c.get('denominazione', default).capitalize()
                    elif keyret == 'province':
                        return c.get('provincia', {}).get(
                            'denominazione', default).capitalize()
                    elif keyret == 'region':
                        return c.get('regione', {}).get(
                            'denominazione', default).capitalize()
                    else:
                        return default

        return default

    def get_from_record(self, record, pkeys: list, defautlres):
        resall = [False]
        pf = record.get('pf', {})
        people = record.get('people', {})
        [resall.append(pf.get(k, False)) for k in pkeys]
        [resall.append(people.get(k, False)) for k in pkeys]
        res = next((item for item in resall if item), defautlres)
        return res

    def get_or_create_odoo_user(self, record, create=False):
        user_id = None
        uid = self.get_from_record(
            record, ['uid'], "")
        tipo_personale = self.get_from_record(
            record, ['tipo_personale'], "")
        full_name = self.get_from_record(
            record, ['full_name'], "")
        if uid != "" and full_name != "" and tipo_personale != "":
            user_id = self.env['res.users'].search([
                ('login', '=', uid)
            ], limit=1)

            if not user_id and create:
                user_id = self.env['res.users'].create({
                    'name': full_name,
                    'login': uid,
                    'company_id': self.env.company.id,
                    'lang': 'it_IT',
                    "tz": "Europe/Rome"
                })
        return user_id

    def make_user_todo(self, record):
        logger.info(f" make persona {record.get('matricola')} In progress ")
        esterno = self.env.ref(
            'inrim_anagrafiche.tipo_persona_esterno').id
        ext_entity = 'entiesterni_tipopersonale'
        ext_winfo_type = self.env['ca.work_info_type'].get_by_code(
            ext_entity)
        ext_job_title_code = "esterno_jobtitles"
        ext_job_title = self.env['ca.titolo_persona'].get_by_code(
            ext_job_title_code)
        default_date_start = fields.Date.today().strftime('%Y-%m-%d')
        date_end = fields.Date.today() + timedelta(days=365)
        base_default_azienda_todo = self.env.ref(
            'controllo_accessi_inrim_app.inrim_azienda_esterna_da_gestire')
        base_default_ente_todo = self.env.ref(
            'controllo_accessi_inrim_app.inrim_ente_esterno_da_gestire')
        codice_fiscale = record.get('cf')
        azienda_ids = [base_default_ente_todo.id]
        type_ids = [esterno]
        persona_id = self.env['ca.persona'].with_context(
            massive_create=True).search([
            ('fiscalcode', '=', codice_fiscale)
        ], limit=1)

        if not persona_id:
            vals = {
                'name': record.get('nome').capitalize(),
                'lastname': record.get('cognome').capitalize(),
                'freshman': record.get('matricola'),
                'fiscalcode': codice_fiscale,
                'type_ids': type_ids,
                'ca_ente_azienda_ids': azienda_ids,
                "send_to_payroll_system": record['sync'] == 'y'
            }
            persona_id = self.with_context(
                massive_create=True).create(vals)
            persona_id.action_checks_in_progress()

        curr_winfo = persona_id.get_current_winfo()

        vals = {
            'ca_persona_id': persona_id.id,
            'work_id_number': record.get('matricola'),
            'ca_work_info_type_id': ext_winfo_type.id,
            'ca_title_id': ext_job_title.id,
            'date_start': self.to_date(default_date_start),
            'date_end': date_end
        }

        if (
                not curr_winfo
        ):
            persona_id.with_context(
                massive_create=True).update_work_info(vals)

    def make_user(self, record):
        logger.info(f"make persona {record.get('matricola')} ")
        # internal_types = self.env.ref('default_ca.internal_people_types')

        internal_types = json.loads(self.env.ref(
            'controllo_accessi_inrim_app.inrim_ir_config_parameter_default_payroll_types').value)
        ext_company = 'ditteesterne_tipopersonale'
        ext_entity = 'entiesterni_tipopersonale'
        ext_job_title_code = "esterno_jobtitles"
        ext_job_title = self.env['ca.titolo_persona'].get_by_code(
            ext_job_title_code)
        ext_winfo_type = self.env['ca.work_info_type'].get_by_code(
            ext_entity)
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
        default_date_start = fields.Date.today().strftime('%Y-%m-%d')
        with self.env.cr.savepoint():
            try:
                azienda_ids = []
                type_ids = []
                user_id = None
                resp_id = None
                title_id = None
                codice_fiscale = ""
                work_info_type_id = None
                is_intenal = False
                birth_date = ''
                tipo_personale = self.get_from_record(
                    record, ['tipo_personale'], "")

                work_info_type_id = self.env['ca.work_info_type'].get_by_name(
                    tipo_personale)
                if not work_info_type_id:
                    work_info_type_id = ext_winfo_type

                is_intenal = work_info_type_id.code in internal_types

                codice_fiscale = self.get_from_record(
                    record, ['codiceFiscale', 'codiceFiscaleEstero', 'codicefiscale'], ""
                )

                user_id = self.get_or_create_odoo_user(
                    record, is_intenal)

                persona_id = self.env['ca.persona'].with_context(
                    massive_create=True).search([
                    ('fiscalcode', '=', codice_fiscale)
                ], limit=1)

                resp_id = self.env['ca.persona'].get_by_login_uid(
                    self.get_from_record(
                        record, ['responsabile_uid', 'referente_uid'], "")
                )
                title_id = self.env['ca.titolo_persona'].get_by_name(
                    self.get_from_record(
                        record, ['qualifica'], "")
                )
                if not title_id:
                    title_id = ext_job_title

                birth_date = self.to_date(self.get_from_record(
                    record, ['dataNascita', 'data_di_nascita'], "1970-01-01"),
                )

                uid = self.get_from_record(
                    record, ['username', 'uid'], "")
                nome = self.get_from_record(
                    record, ['nome', 'nome'], "").capitalize()
                cognome = self.get_from_record(
                    record, ['cognome', 'cognome'], "").capitalize()
                if is_intenal:
                    type_ids.append(interno)
                    azienda_ids.append(base_institute.id)
                else:
                    type_ids.append(esterno)
                    if work_info_type_id.code == ext_company:
                        azienda_ids.append(base_default_azienda_todo.id)
                    elif work_info_type_id.code == ext_entity:
                        azienda_ids.append(base_default_ente_todo.id)

                if not persona_id:
                    if nome and cognome:
                        capRes = self.get_from_record(
                            record, ['capResidenza'], "")
                        capDom = self.get_from_record(
                            record, ['capDomFiscale'], "")

                        cittad = self.get_from_record(
                            record, ['codNazioneCittadinanza'], "")

                        vals = {
                            'uid': uid,
                            'name': nome,
                            'lastname': cognome,
                            'freshman': record.get('matricola'),
                            'email': self.get_from_record(
                                record, ['EMail', 'mail'], ""),
                            'mobile': self.get_from_record(
                                record, ['cell_phone_service'], ""),
                            'private_mobile': self.get_from_record(
                                record, ['cellPersonale', 'private_cell_phone'], ""),
                            'phone': self.get_from_record(
                                record, ['telephonNumber', 'telUfficio'], ""),
                            'fiscalcode': codice_fiscale,
                            'type_ids': type_ids,
                            'nationality': cittad,
                            'birth_date': birth_date,
                            'birth_place': self.decode_cadaster(
                                record, 'codComuneNascita', 'city', ""),
                            'istat_code': self.get_from_record(
                                record, ['codComuneNascita'], ""),
                            'ca_ente_azienda_ids': azienda_ids,
                            'associated_user_id': user_id.id,
                            'parent_id': resp_id.id if resp_id else False,
                            'residence_zip': capRes,
                            'residence_city': self.decode_cadaster(
                                record, 'codComuneResidenza', 'city', ""),
                            'residence_street': self.get_from_record(
                                record, ['indirizzoResidenza'], ""),
                            'domicile_other_than_residence': capRes != capDom,
                            'domicile_zip': capDom,
                            'domicile_city': self.decode_cadaster(
                                record, 'codComuneDomFiscale', 'city', ""),
                            'domicile_street': self.get_from_record(
                                record, ['indirizzoDomFiscale'], ""),
                            "send_to_payroll_system": record['sync'] == 'y'
                        }
                        logger.info(f"insert persona {record.get('matricola')} ")
                        persona_id = self.with_context(
                            massive_create=True).create(vals)
                        persona_id.action_completed()

                else:
                    if resp_id and (
                            not persona_id.parent_id or
                            persona_id.parent_id.freshman != resp_id.freshman
                    ):
                        logger.info(f"update persona {record.get('matricola')} ")
                        persona_id.parent_id = resp_id.id if resp_id else False

                curr_winfo = persona_id.get_current_winfo()

                vals = {
                    'ca_persona_id': persona_id.id,
                    'work_id_number': record.get('matricola'),
                    'ca_div_uo_code': self.get_from_record(
                        record, ['divisione_code'], ""),
                    'ca_work_info_type_id': work_info_type_id.id if work_info_type_id else False,
                    'ca_title_id': title_id.id if title_id else False,
                    'date_start': self.to_date(
                        self.get_from_record(
                            record, ['data_inizio'], default_date_start)
                    ),
                    'date_end': self.to_date(
                        self.get_from_record(record, ['data_fine'], date_end_forever)
                    )
                }

                if (
                        not curr_winfo or
                        not curr_winfo.ca_work_info_type_id.id == work_info_type_id.id or
                        not curr_winfo.ca_title_id.id == title_id.id
                ):
                    persona_id.with_context(
                        massive_create=True).update_work_info(vals)
            except Exception as e:
                logger.error(
                    f"Error Skip {record.get('matricola')}: {e}", exc_info=True)

    def open_wizard_modifica_matricola_registro_accessi(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "controllo_accessi_inrim_app.ca_modifica_matricola_registro_accesso_action")
        action['context'] = {
                'default_ca_persona_id': self.id,
        }
        return action