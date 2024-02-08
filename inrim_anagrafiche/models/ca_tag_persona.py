from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import string

class CaTagPersona(models.Model):
    _name = 'ca.tag_persona'
    _description = 'Tag Persona'
    _rec_name = 'token'

    token = fields.Char(required=True, readonly=True, default=lambda self:self.get_token())
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
                    raise UserError(_("Esiste già un'altro tag persona per questa persona in questo periodo"))

    @api.onchange('date_start', 'date_end', 'ca_tag_id')
    def _onchange_date(self):
        for record in self:
            if record.ca_tag_id:
                record.ca_tag_id.in_use = False
                if record.date_start and record.date_end:
                    today = fields.Date.today()
                    if record.date_start <= today and record.date_end >= today:
                        record.ca_tag_id.in_use = True
                
    def _cron_check_validity_tag(self):
        for record in self.env['ca.tag_persona'].search([]):
            if record.ca_tag_id:
                record.ca_tag_id.in_use = False
                if record.date_start and record.date_end:
                    today = fields.Date.today()
                    if record.date_start <= today and record.date_end >= today:
                        record.ca_tag_id.in_use = True

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        persona_id = self.env['ca.tag_persona'].search([('token', '=', token)])
        if persona_id:
            self.get_token()
        return token