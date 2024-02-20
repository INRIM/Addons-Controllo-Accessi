from odoo import models, fields, api, _

class CaStatoAnag(models.Model):
    _name = 'ca.stato_anag'
    _description = 'Stato Anagrafica'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)