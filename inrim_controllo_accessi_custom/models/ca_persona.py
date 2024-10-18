from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from odoo.tools import config

class CaPersona(models.Model):
    _inherit = 'ca.persona'

    domicile_partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    domicile_partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    domicile_date_localization = fields.Date(string='Geolocation Date')
    residence_partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    residence_partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    residence_date_localization = fields.Date(string='Geolocation Date')
    # RESIDENCE
    residence_city = fields.Char(
        compute='_compute_residence_city', readonly=False, store=True
    )
    residence_state_id = fields.Many2one(
        'res.country.state',
        domain="[('country_id', '=?', residence_country_id)]",
        compute='_compute_residence_state_id', readonly=False, store=True
    )
    residence_zip = fields.Char(
        compute='_compute_residence_zip',
        readonly=False, store=True
    )
    residence_country_id = fields.Many2one(
        'res.country', compute='_compute_residence_country_id',
        readonly=False, store=True
    )
    residence_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_residence_zip_id",
        readonly=False,
        store=True,
    )
    residence_city_id = fields.Many2one(
        'res.city',
        index=True,
        compute="_compute_residence_city_id",
        readonly=False,
        store=True,
    )
    # DOMICILE
    domicile_city = fields.Char(
        compute='_compute_domicile_city', readonly=False, store=True
    )
    domicile_state_id = fields.Many2one(
        'res.country.state',
        domain="[('country_id', '=?', domicile_country_id)]",
        compute='_compute_domicile_state_id', readonly=False, store=True
    )
    domicile_zip = fields.Char(
        compute='_compute_domicile_zip',
        readonly=False, store=True
    )
    domicile_country_id = fields.Many2one(
        'res.country', compute='_compute_domicile_country_id',
        readonly=False, store=True
    )
    domicile_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_domicile_zip_id",
        readonly=False,
        store=True,
    )
    domicile_city_id = fields.Many2one(
        'res.city',
        index=True,
        compute="_compute_domicile_city_id",
        readonly=False,
        store=True,
    )

    # DOMICILE
    @api.depends("domicile_state_id", "domicile_country_id", "domicile_city_id", "domicile_zip")
    def _compute_domicile_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("domicile_zip_id"):
            fields_map = {
                "domicile_zip": "name",
                "domicile_city_id": "city_id",
                "domicile_state_id": "state_id",
                "domicile_country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                    record[rec_field]
                    and record[rec_field] != record._origin[rec_field]
                    and record[rec_field] != record.domicile_zip_id[zip_field]
                ):
                    record.domicile_zip_id = False
                    break

    @api.depends("domicile_zip_id")
    def _compute_domicile_city_id(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_city_id = record.domicile_zip_id.city_id

    @api.depends("domicile_zip_id")
    def _compute_domicile_city(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_city = record.domicile_zip_id.city_id.name

    @api.depends("domicile_zip_id")
    def _compute_domicile_zip(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_zip = record.domicile_zip_id.name
    
    @api.depends("domicile_zip_id", "domicile_state_id")
    def _compute_domicile_country_id(self):
        for record in self:
            if record.domicile_zip_id.city_id.country_id:
                record.domicile_country_id = record.domicile_zip_id.city_id.country_id
            elif record.domicile_state_id:
                record.domicile_country_id = record.domicile_state_id.country_id

    @api.depends("domicile_zip_id")
    def _compute_domicile_state_id(self):
        for record in self:
            state = record.domicile_zip_id.city_id.state_id
            if state and record.domicile_state_id != state:
                record.domicile_state_id = record.domicile_zip_id.city_id.state_id

    @api.constrains("domicile_zip_id", "domicile_country_id", "domicile_city_id", "domicile_state_id", "domicile_zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.domicile_zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.domicile_zip_id.name}
            if rec.domicile_zip_id.city_id.country_id != rec.domicile_country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.city_id.state_id != rec.domicile_state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.city_id != rec.domicile_city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.name != rec.domicile_zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
    
    # RESIDENCE
    @api.depends("residence_state_id", "residence_country_id", "residence_city_id", "residence_zip")
    def _compute_residence_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("residence_zip_id"):
            fields_map = {
                "residence_zip": "name",
                "residence_city_id": "city_id",
                "residence_state_id": "state_id",
                "residence_country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                    record[rec_field]
                    and record[rec_field] != record._origin[rec_field]
                    and record[rec_field] != record.residence_zip_id[zip_field]
                ):
                    record.residence_zip_id = False
                    break

    @api.depends("residence_zip_id")
    def _compute_residence_city_id(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_city_id = record.residence_zip_id.city_id

    @api.depends("residence_zip_id")
    def _compute_residence_city(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_city = record.residence_zip_id.city_id.name

    @api.depends("residence_zip_id")
    def _compute_residence_zip(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_zip = record.residence_zip_id.name
    
    @api.depends("residence_zip_id", "residence_state_id")
    def _compute_residence_country_id(self):
        for record in self:
            if record.residence_zip_id.city_id.country_id:
                record.residence_country_id = record.residence_zip_id.city_id.country_id
            elif record.residence_state_id:
                record.residence_country_id = record.residence_state_id.country_id

    @api.depends("residence_zip_id")
    def _compute_residence_state_id(self):
        for record in self:
            state = record.residence_zip_id.city_id.state_id
            if state and record.residence_state_id != state:
                record.residence_state_id = record.residence_zip_id.city_id.state_id

    @api.constrains("residence_zip_id", "residence_country_id", "residence_city_id", "residence_state_id", "residence_zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.residence_zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.residence_zip_id.name}
            if rec.residence_zip_id.city_id.country_id != rec.residence_country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.city_id.state_id != rec.residence_state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.city_id != rec.residence_city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.name != rec.residence_zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )

    def write(self, vals):
        # Reset latitude/longitude in case we modify the address without
        # updating the related geolocation fields
        if any(field in vals for field in [
                'domicile_street', 'domicile_zip','domicile_city',
                'domicile_state_id', 'domicile_country_id'
            ]) \
                and not all('partner_%s' % field in vals for field in ['latitude', 'longitude']):
            vals.update({
                'domicile_partner_latitude': 0.0,
                'domicile_partner_longitude': 0.0,
            })
        if any(field in vals for field in [
                'residence_street', 'residence_zip', 'residence_city',
                'residence_state_id', 'residence_country_id'
            ]) \
                and not all('partner_%s' % field in vals for field in ['latitude', 'longitude']):
            vals.update({
                'residence_partner_latitude': 0.0,
                'residence_partner_longitude': 0.0,
            })
        return super(CaPersona, self).write(vals)

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        # We need country names in English below
        if not self._context.get('force_geo_localize') \
                and (self._context.get('import_file') \
                     or any(config[key] for key in ['test_enable', 'test_file', 'init', 'update'])):
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
                        f'{address_type}_date_localization': fields.Date.context_today(partner)
                    })
                else:
                    partners_not_geo_localized |= partner
        if partners_not_geo_localized:
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'title': _("Warning"),
                'message': _('No match found for %(partner_names)s address(es).', partner_names=', '.join(partners_not_geo_localized.mapped('display_name')))
            })
        return True