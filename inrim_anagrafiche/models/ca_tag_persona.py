import random
import string

from odoo.exceptions import UserError

from odoo import models, fields, api, _


class CaTagPersona(models.Model):
    _name = 'ca.tag_persona'
    _description = 'Tag Persona'
    _rec_name = 'token'

    token = fields.Char(required=True, readonly=True,
                        default=lambda self: self.get_token())
    ca_persona_id = fields.Many2one('ca.persona', required=True)
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    temp = fields.Boolean()
    active = fields.Boolean(default=True)

    @api.constrains('ca_persona_id', 'ca_tag_id', 'date_start', 'date_end')
    def _check_duplicate(self):
        for record in self:
            if (
                    record.ca_tag_id and record.ca_persona_id and
                    record.date_start and record.date_end
            ):
                tag_persona_id = self.env['ca.tag_persona'].search([
                    ('ca_persona_id', '=', record.ca_persona_id.id),
                    ('ca_tag_id', '=', record.ca_tag_id.id),
                    ('date_start', '<=', record.date_end),
                    ('date_end', '>=', record.date_start),
                    ('id', '!=', record.id),
                    ('active', '=', record.active)
                ])
                if tag_persona_id:
                    raise UserError(
                        _("Esiste già un'altro tag persona per questa persona in questo periodo"))

    @api.constrains('ca_persona_id', 'temp')
    def _check_temp_tag_persona(self):
        for record in self:
            if record.ca_persona_id:
                if record.ca_persona_id.is_external and not record.temp:
                    raise UserError(
                        _('Ad un esterno possono essere assegnati solo tag di tipo temporaneo'))

    @api.constrains('ca_tag_id')
    def _check_tag_revocato(self):
        for record in self:
            if self.env.ref(
                    'inrim_anagrafiche.proprieta_tag_revocato') in record.ca_tag_id.ca_proprieta_tag_ids:
                raise UserError(_('Il tag ' + str(
                    record.ca_tag_id.name) + ' risulta revocato'))

    def check_update_record_by_date_valididty(
            self, record):
        if record.ca_tag_id:
            record.ca_tag_id.in_use = False
            if record.date_start and record.date_end:
                today = fields.Date.today()
                if record.date_start <= today and record.date_end >= today:
                    record.ca_tag_id.in_use = True

    def create(self, vals):
        if vals.get('ca_tag_id'):
            ca_tag_id = self.env['ca.tag'].browse(vals.get('ca_tag_id'))
            if ca_tag_id.temp:
                vals['temp'] = ca_tag_id.temp
        res = super(CaTagPersona, self).create(vals)
        for record in res:
            self.check_update_record_by_date_valididty(record)
        return res

    def write(self, vals_list):
        if self.ca_tag_id:
            if self.ca_tag_id.temp:
                vals_list['temp'] = self.ca_tag_id.temp
        res = super(CaTagPersona, self).write(vals_list)
        for record in self:
            self.check_update_record_by_date_valididty(record)
        return res

    def _cron_check_validity_tag(self):
        ca_tag_persona_ids = self.env['ca.tag_persona'].search([])
        if ca_tag_persona_ids:
            for tag in ca_tag_persona_ids:
                self.check_update_record_by_date_valididty(tag)
        else:
            for tag in self.env['ca.tag'].search([]):
                tag.in_use = False

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        persona_id = self.env['ca.tag_persona'].search([('token', '=', token)])
        if persona_id:
            self.get_token()
        return token
