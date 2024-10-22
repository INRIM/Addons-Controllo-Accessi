from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaProprietaTag(models.Model):
    _name = 'ca.proprieta_tag'
    _inherit = "ca.model.base.mixin"
    _description = 'Proprietà Tag'

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
                        _('Data fine deve essere maggiore della data di inizio'))
                
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
    ca_proprieta_tag_ids = fields.Many2many('ca.proprieta_tag')
    in_use = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)
    temp = fields.Boolean(compute="_compute_temp", store=True)
    revoked = fields.Boolean(compute="_compute_revoked", store=True)

    @api.depends('ca_proprieta_tag_ids')
    def _compute_temp(self):
        for record in self:
            record.temp = False
            if record.ca_proprieta_tag_ids:
                if self.env.ref('inrim_anagrafiche.proprieta_tag_temporaneo') in record.ca_proprieta_tag_ids:
                    record.temp = True

    @api.depends('ca_proprieta_tag_ids')
    def _compute_revoked(self):
        for record in self:
            record.revoked = False
            if record.ca_proprieta_tag_ids:
                if self.env.ref('inrim_anagrafiche.proprieta_tag_revocato') in record.ca_proprieta_tag_ids:
                    record.revoked = True