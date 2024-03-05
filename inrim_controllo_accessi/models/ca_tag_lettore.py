from odoo import models, fields, api

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
