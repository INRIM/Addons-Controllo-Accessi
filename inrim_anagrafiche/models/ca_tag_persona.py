import random
import string

from odoo.exceptions import UserError

from odoo import models, fields, api, _


class CaTagPersona(models.Model):
    _name = 'ca.tag_persona'
    _description = 'Tag Persona'
    _rec_name = 'tag_name'

    token = fields.Char(required=True, readonly=True,
                        default=lambda self: self.get_token())
    ca_persona_id = fields.Many2one('ca.persona', required=True)
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    tag_name = fields.Char(related="ca_tag_id.name", store=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    temp = fields.Boolean()
    available_tags_ids = fields.Many2many('ca.tag', compute="_compute_available_tags")
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    @api.constrains('ca_persona_id', 'ca_tag_id', 'date_start', 'date_end', 'active')
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

    @api.constrains('ca_persona_id', 'temp', 'active')
    def _check_temp_tag_persona(self):
        for record in self:
            if record.ca_persona_id:
                if record.ca_persona_id.is_external and not record.temp:
                    raise UserError(
                        _('Ad un esterno possono essere assegnati solo tag di tipo temporaneo'))

    @api.constrains('ca_tag_id', 'active')
    def _check_tag_revocato(self):
        for record in self:
            if record.ca_tag_id.revoked:
                raise UserError(_('Il tag ' + str(
                    record.ca_tag_id.name) + ' risulta revocato'))
            
    @api.onchange('ca_persona_id')
    def _compute_available_tags(self):
        for record in self:
            record.available_tags_ids = self.env['ca.tag'].search([
                        ('in_use', '=', False),
                        ('revoked', '=', False)
                    ])
            if record.ca_persona_id:
                if record.ca_persona_id.is_external:
                    record.available_tags_ids = self.env['ca.tag'].search([
                        ('in_use', '=', False),
                        ('revoked', '=', False),
                        ('temp', '=', True)
                    ])

    def check_update_record_by_date_valididty(self):
        today = fields.Date.today()
        for tag in self.env['ca.tag'].search([]):
            tag_persona = self.env['ca.tag_persona'].search([('ca_tag_id', '=', tag.id)])
            if tag_persona:
                for tp in tag_persona:
                    if tp.date_start <= today and tp.date_end >= today:
                        tag.in_use = True
                    else:
                        tag.in_use = False
            else:
                tag.in_use = False

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('ca_tag_id'):
                ca_tag_id = self.env['ca.tag'].browse(val.get('ca_tag_id'))
                if ca_tag_id.temp:
                    val['temp'] = ca_tag_id.temp
        res = super(CaTagPersona, self).create(vals)
        self.check_update_record_by_date_valididty()
        return res

    def write(self, vals_list):
        if self.ca_tag_id:
            if self.ca_tag_id.temp:
                vals_list['temp'] = self.ca_tag_id.temp
        res = super(CaTagPersona, self).write(vals_list)
        self.check_update_record_by_date_valididty()
        return res
    
    def unlink(self):
        for record in self:
            if record.ca_tag_id:
                record.ca_tag_id.in_use = False
        res = super(CaTagPersona, self).unlink()
        self.check_update_record_by_date_valididty()
        return res

    def _cron_check_validity_tag(self):
        self.check_update_record_by_date_valididty()

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        tag_persona_id = self.env['ca.tag_persona'].search([('token', '=', token)])
        if tag_persona_id:
            self.get_token()
        return token
