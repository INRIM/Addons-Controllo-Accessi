from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaProprietaTag(models.Model):
    _name = 'ca.proprieta_tag'
    _inherit = "ca.model.base.mixin"
    _description = 'Proprietà Tag'
    _rec_names_search = ['name', 'description']

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('End date must be greater than start date'))

    def rest_boby_hint(self):
        return {
            "name": "Temporaneo"
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end)
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name'
            ])
        return body, msg


class CaTag(models.Model):
    _name = 'ca.tag'
    _description = 'Tag'
    _inherit = "ca.model.base.mixin"
    _rec_names_search = ['name', 'tag_code']

    name = fields.Char(required=True)
    tag_code = fields.Char(required=True)
    ca_proprieta_tag_ids = fields.Many2many('ca.proprieta_tag',
        string="Tag Properties")
    in_use = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)
    default_id_number = fields.Char()
    temp = fields.Boolean(compute="_compute_properties", store=True)
    revoked = fields.Boolean(compute="_compute_properties", store=True)

    def compute_properties(self):
        self.ensure_one()
        self.revoked = False
        self.temp = False
        if self.ca_proprieta_tag_ids:
            if self.env.ref(
                    'inrim_anagrafiche.proprieta_tag_revocato') in self.ca_proprieta_tag_ids:
                self.revoked = True
        if self.ca_proprieta_tag_ids:
            if self.env.ref(
                    'inrim_anagrafiche.proprieta_tag_temporaneo') in self.ca_proprieta_tag_ids:
                self.temp = True

    @api.depends('ca_proprieta_tag_ids')
    def _compute_properties(self):
        for record in self:
            record.compute_properties()

    @api.constrains('tag_code', 'active')
    def _check_unique_tag(self):
        for record in self:
            if record.tag_code:
                tags = self.env['ca.tag'].with_context(
                    active_test=False).search(
                    [
                        ('id', '!=', record.id),
                        ('tag_code', '=', record.tag_code)
                    ]
                )
                if tags:
                    msg = _(f'Esiste già questo Tag: {record.tag_code} in {record.name}')
                    if not record.active:
                        msg = _(f"{record.tag_code} Risulta disattivato, riattivare per utilizzare")
                    raise UserError(
                        _(msg))

    @api.constrains('default_id_number', 'active')
    def _check_unique_default_id_number(self):
        for record in self:
            if record.default_id_number:
                tags = self.env['ca.tag'].with_context(
                    active_test=False).search(
                    [
                        ('id', '!=', record.id),
                        ('default_id_number', '=', record.default_id_number)
                    ]
                )
                if tags:
                    msg = _(f'Esiste già questo Seriale: {record.default_id_number} {record.name}')
                    if not record.active:
                        msg = _(f"{record.name} Risulta disattivato, riattivare per utilizzare")
                    raise UserError(
                        _(msg))

    def rest_boby_hint(self):
        return {
            "name": "Temporaneo",
            "tag_code": "E0010150AD255C11",
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'tag_code': self.tag_code,
            'ca_proprieta_tag_ids': self.f_m2m(self.ca_proprieta_tag_ids),
            'in_use': self.in_use,
            'temp': self.temp,
            'revoked': self.revoked,
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'tag_code'
            ])
        return body, msg
