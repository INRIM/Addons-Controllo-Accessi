from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaTagLettore(models.Model):
    _name = 'ca.tag_lettore'
    _inherit = "ca.model.base.mixin"
    _description = 'Tag Lettore'

    name = fields.Char(compute="_compute_name", store=True)
    ca_lettore_id = fields.Many2one('ca.lettore', required=True)
    ca_tag_id = fields.Many2one('ca.tag', required=True)
    tag_in_use = fields.Boolean(related="ca_tag_id.in_use")
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    temp = fields.Boolean(related='ca_tag_id.temp')
    expired = fields.Boolean(compute="_compute_expired")
    active = fields.Boolean(default=True)
    ca_punto_accesso_id = fields.Many2one('ca.punto_accesso')

    def rest_boby_hint(self):
        return {
            "ca_lettore_id": 1,
            "ca_tag_id": 1,
            "date_start": "2024-01-01",
            "date_end": "2024-12-31"
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'ca_lettore_id': self.f_m2o(self.ca_lettore_id),
            'ca_tag_id': self.f_m2o(self.ca_tag_id),
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end),
            'temp': self.temp,
            'expired': self.expired,
            'ca_punto_accesso_id': self.f_m2o(self.ca_punto_accesso_id)
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'ca_lettore_id', 'ca_tag_id', 'date_start', 'date_end'
            ])
        return body, msg

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    @api.model_create_multi
    def create(self, vals):
        res = super(CaTagLettore, self).create(vals)
        for record in res:
            if record.ca_punto_accesso_id:
                record.ca_punto_accesso_id.remote_update = True
        return res

    def write(self, vals):
        res = super(CaTagLettore, self).write(vals)
        for record in self:
            if record.ca_punto_accesso_id:
                record.ca_punto_accesso_id.remote_update = True
        return res

    def unlink(self):
        for record in self:
            if record.ca_punto_accesso_id:
                record.ca_punto_accesso_id.remote_update = True
        return super(CaTagLettore, self).unlink()

    @api.onchange('ca_lettore_id')
    def _onchange_ca_lettore_id(self):
        for record in self:
            if record.ca_punto_accesso_id.ca_lettore_id != record.ca_lettore_id:
                record.ca_punto_accesso_id = False

    @api.onchange('ca_tag_id')
    def _onchange_ca_tag_id(self):
        for record in self:
            today = fields.Date.today()
            record.date_start = False
            record.date_end = False
            if record.ca_tag_id and record.tag_in_use:
                tag_persona_id = self.env['ca.tag_persona'].search([
                    ('ca_tag_id', '=', record.ca_tag_id.id),
                    ('date_start', '<=', today),
                    ('date_end', '>=', today)
                ], limit=1)
                if tag_persona_id:
                    record.date_start = tag_persona_id.date_start
                    record.date_end = tag_persona_id.date_end

    @api.onchange('date_end')
    def _compute_expired(self):
        for record in self:
            record.expired = False
            if record.date_end and fields.date.today() > record.date_end:
                record.expired = True

    @api.depends('ca_lettore_id', 'ca_tag_id')
    def _compute_name(self):
        for record in self:
            record.name = '/'
            if record.ca_lettore_id and record.ca_tag_id:
                record.name = f'{record.ca_lettore_id.name} {record.ca_tag_id.name}'

    @api.constrains('ca_tag_id', 'ca_lettore_id', 'active')
    def _check_unique(self):
        for record in self:
            tag_lettore_id = self.env['ca.tag_lettore'].search([
                ('id', '!=', record.id),
                ('ca_lettore_id', '=', record.ca_lettore_id.id),
                ('ca_tag_id', '=', record.ca_tag_id.id)
            ])
            if tag_lettore_id:
                raise UserError(_('Esiste già un tag lettore con stesso tag e lettore'))
    
    def collega_tag_lettore(self, nome_lettore, nome_tag, date_start, date_end):
        if nome_lettore and nome_tag and date_start and date_end:
            try:
                lettore_id = self.env['ca.lettore'].search([
                    ('name', '=', nome_lettore)
                ])
                tag_id = self.env['ca.tag'].search([
                    ('name', '=', nome_tag)
                ])
                if lettore_id and tag_id:
                    tag_lettore_id = self.env['ca.tag_lettore'].create({
                        'ca_lettore_id': lettore_id.id,
                        'ca_tag_id': tag_id.id,
                        'date_start': date_start,
                        'date_end': date_end
                    })
                    return tag_lettore_id
                else:
                    return None
            except Exception as e:
                raise UserError(e)
        else:
            return None