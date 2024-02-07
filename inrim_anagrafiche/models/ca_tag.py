from odoo import models, fields

class CaProprietaTag(models.Model):
    _name = 'ca.proprieta_tag'
    _description = 'Proprietà Tag'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

class CaTag(models.Model):
    _name = 'ca.tag'
    _description = 'Tag'
    _rec_names_search = ['name', 'tag_code']

    name = fields.Char(required=True)
    tag_code = fields.Char(required=True)
    ca_proprieta_tag_ids = fields.Many2many('ca.proprieta_tag')
    in_use = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)
    