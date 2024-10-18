from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from odoo.tools import config

from odoo import api, fields, models, _

get_addressbook_path = '/api/get_addressbook'


class CaPersona(models.Model):
    _inherit = 'ca.persona'

    domicile_partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    domicile_partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    domicile_date_localization = fields.Date(string='Geolocation Date')
    residence_partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    residence_partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    residence_date_localization = fields.Date(string='Geolocation Date')

    def write(self, vals):
        # Reset latitude/longitude in case we modify the address without
        # updating the related geolocation fields
        if any(field in vals for field in [
            'domicile_street', 'domicile_zip', 'domicile_city',
            'domicile_state_id', 'domicile_country_id'
        ]) \
                and not all(
            'partner_%s' % field in vals for field in ['latitude', 'longitude']):
            vals.update({
                'domicile_partner_latitude': 0.0,
                'domicile_partner_longitude': 0.0,
            })
        if any(field in vals for field in [
            'residence_street', 'residence_zip', 'residence_city',
            'residence_state_id', 'residence_country_id'
        ]) \
                and not all(
            'partner_%s' % field in vals for field in ['latitude', 'longitude']):
            vals.update({
                'residence_partner_latitude': 0.0,
                'residence_partner_longitude': 0.0,
            })
        return super(CaPersona, self).write(vals)

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city,
                                           state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        # We need country names in English below
        if not self._context.get('force_geo_localize') \
                and (self._context.get('import_file') \
                     or any(config[key] for key in
                            ['test_enable', 'test_file', 'init', 'update'])):
            return False
        partners_not_geo_localized = self.env['ca.persona']
        address_type = self._context.get('address_type')
        if address_type in ['domicile', 'residence']:
            for partner in self.with_context(lang='en_US'):
                if address_type == 'domicile':
                    result = self._geo_localize(partner.domicile_street,
                                                partner.domicile_zip,
                                                partner.domicile_city,
                                                partner.domicile_state_id.name,
                                                partner.domicile_country_id.name)
                elif address_type == 'residence':
                    result = self._geo_localize(partner.residence_street,
                                                partner.residence_zip,
                                                partner.residence_city,
                                                partner.residence_state_id.name,
                                                partner.residence_country_id.name)
                if result:
                    partner.write({
                        f'{address_type}_partner_latitude': result[0],
                        f'{address_type}_partner_longitude': result[1],
                        f'{address_type}_date_localization': fields.Date.context_today(
                            partner)
                    })
                else:
                    partners_not_geo_localized |= partner
        if partners_not_geo_localized:
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification',
                                         {
                                             'title': _("Warning"),
                                             'message': _(
                                                 'No match found for %(partner_names)s address(es).',
                                                 partner_names=', '.join(
                                                     partners_not_geo_localized.mapped(
                                                         'display_name')))
                                         })
        return True

    def _cron_people_get_addressbook(self):
        people_x_key = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.key')
        header = {
            'x-key': people_x_key
        }
        people_url = self.env[
            'ir.config_parameter'
        ].sudo().get_param('people.url')
        url = f'{people_url}{get_addressbook_path}'
        try:
            request = requests.get(url, headers=header)
            if request.status_code == 200:
                logger.info(f"{url}, Status Code: {request.status_code}")
                data = request.json()
                self.get_addressbook_data(data)
            else:
                logger.info(f"{url}, Status Code: {request.status_code}")
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{url}, Status Code: {request.status_code}")
            logger.info(e)
            return False

    def get_addressbook_data(self, data):
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
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"Error: {e}")
