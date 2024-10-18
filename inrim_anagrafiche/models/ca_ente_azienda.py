from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class CaEnteAzienda(models.Model):
    _name = 'ca.ente_azienda'
    _inherit = "ca.model.base.mixin"
    _description = 'Ente Azienda'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one('ca.ente_azienda', string='Parent Company', index=True)
    child_ids = fields.One2many('ca.ente_azienda', 'parent_id', string='Branches')
    all_child_ids = fields.One2many('ca.ente_azienda', 'parent_id', context={'active_test': False})
    parent_path = fields.Char(index=True, unaccent=False)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(
        compute='_compute_zip',
        readonly=False, store=True
    )
    city = fields.Char(
        compute='_compute_city', readonly=False, store=True
    )
    state_id = fields.Many2one(
        'res.country.state', domain="[('country_id', '=?', country_id)]",
        compute='_compute_state_id', readonly=False, store=True
    )
    country_id = fields.Many2one(
        'res.country', compute='_compute_country_id',
        readonly=False, store=True
    )
    zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_zip_id",
        readonly=False,
        store=True,
    )
    city_id = fields.Many2one(
        'res.city',
        index=True,
        compute="_compute_city_id",
        readonly=False,
        store=True,
    )
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    website = fields.Char()
    vat = fields.Char()
    pec = fields.Char(required=True)
    tipo_ente_azienda_id = fields.Many2one('ca.tipo_ente_azienda', required=True)
    note = fields.Text()
    company_id = fields.Many2one('res.company')
    ca_persona_ids = fields.Many2many('ca.persona', string='People')

    @api.depends("state_id", "country_id", "city_id", "zip")
    def _compute_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("zip_id"):
            fields_map = {
                "zip": "name",
                "city_id": "city_id",
                "state_id": "state_id",
                "country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                    record[rec_field]
                    and record[rec_field] != record._origin[rec_field]
                    and record[rec_field] != record.zip_id[zip_field]
                ):
                    record.zip_id = False
                    break

    @api.depends("zip_id")
    def _compute_city_id(self):
        for record in self:
            if record.zip_id:
                record.city_id = record.zip_id.city_id

    @api.depends("zip_id")
    def _compute_city(self):
        for record in self:
            if record.zip_id:
                record.city = record.zip_id.city_id.name

    @api.depends("zip_id")
    def _compute_zip(self):
        for record in self:
            if record.zip_id:
                record.zip = record.zip_id.name
    
    @api.depends("zip_id", "state_id")
    def _compute_country_id(self):
        for record in self:
            if record.zip_id.city_id.country_id:
                record.country_id = record.zip_id.city_id.country_id
            elif record.state_id:
                record.country_id = record.state_id.country_id

    @api.depends("zip_id")
    def _compute_state_id(self):
        for record in self:
            state = record.zip_id.city_id.state_id
            if state and record.state_id != state:
                record.state_id = record.zip_id.city_id.state_id

    @api.constrains("zip_id", "country_id", "city_id", "state_id", "zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.zip_id.name}
            if rec.zip_id.city_id.country_id != rec.country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.city_id.state_id != rec.state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.city_id != rec.city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.name != rec.zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )

class CaTipoEnteAzienda(models.Model):
    _name = 'ca.tipo_ente_azienda'
    _inherit = "ca.model.base.mixin"
    _description = 'Tipo Ente Azienda'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    is_internal = fields.Boolean()
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))