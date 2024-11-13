import random
import string

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaTagPersona(models.Model):
    _name = 'ca.tag_persona'
    _inherit = "ca.model.base.mixin"
    _description = 'Tag Persona'
    _rec_name = 'tag_name'

    token = fields.Char(
        required=True, readonly=True,
        default=lambda self: self.get_token())
    ca_persona_id = fields.Many2one('ca.persona', required=True)
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    tag_name = fields.Char(related="ca_tag_id.name", store=True)
    tag_in_use = fields.Boolean(related="ca_tag_id.in_use", store=True)
    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)
    temp = fields.Boolean(related="ca_tag_id.temp", store=True)
    state = fields.Selection(
        [
            ('to_give_back', 'To Give Back'),
            ('returned', 'Returned'),
            ('scheduled', 'Secheduled'),
        ], default='returned',
        string='State', readonly=True)
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

    def set_retuned(self):
        self.date_end = fields.Datetime.now()
        self.ca_tag_id.in_use = False
        self.state = 'returned'

    @api.onchange('date_start', 'date_end')
    def check_date(self):
        for record in self:
            record.check_update_record_by_date_valididty()


    def check_update_record_by_date_valididty(self):
        now = fields.Datetime.now()
        self.ensure_one()
        if self.date_start <= now <= self.date_end:
            self.ca_tag_id.in_use = True
            self.state = 'to_give_back'
        elif self.date_start > now:
            self.ca_tag_id.in_use = True
            self.state = 'scheduled'
        else:
            self.ca_tag_id.in_use = False
            self.state = 'returned'

    def check_update_by_date_valididty(self):
        for tag_persona in self.search([]):
            if tag_persona:
                tag_persona.check_update_record_by_date_valididty()

    def _cron_check_validity_tag(self):
        self.check_update_by_date_valididty()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('ca_tag_id'):
                ca_tag_id = self.env['ca.tag'].browse(val.get('ca_tag_id'))
                if ca_tag_id.temp:
                    val['temp'] = ca_tag_id.temp
        res = super(CaTagPersona, self).create(vals)
        res.check_update_record_by_date_valididty()
        return res

    def write(self, vals_list):
        if self.ca_tag_id:
            if self.ca_tag_id.temp:
                vals_list['temp'] = self.ca_tag_id.temp
        res = super(CaTagPersona, self).write(vals_list)
        return res

    def unlink(self):
        for record in self:
            if record.ca_tag_id:
                record.ca_tag_id.in_use = False
        res = super(CaTagPersona, self).unlink()
        return res

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        tag_persona_id = self.env['ca.tag_persona'].search([('token', '=', token)])
        if tag_persona_id:
            self.get_token()
        return token

    @api.model
    def get_current_by_tag(self, tag):
        now = fields.Datetime.now()
        return self.env['ca.tag_persona'].search([
            ('ca_tag_id', '=', tag.id),
            ('date_start', '<=', now),
            ('date_end', '>=', now),
            ('state', '=', 'to_give_back')
        ], limit=1)
