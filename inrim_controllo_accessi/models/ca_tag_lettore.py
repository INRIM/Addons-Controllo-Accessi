from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaTagLettore(models.Model):
    _name = 'ca.tag_lettore'
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

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

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
                record.name = record.ca_lettore_id.name + ' ' + record.ca_tag_id.name

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