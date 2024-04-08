from odoo import models, fields, api

class CaRegistroAccesso(models.Model):
    _name = 'ca.registro_accesso'
    _description = 'Registro Accesso'
    _rec_name = 'spazio_id'

    spazio_id = fields.Many2one('ca.spazio', required=True)
    ente_azienda_id = fields.Many2one(related='spazio_id.ente_azienda_id', store=True)
    righe_accesso_ids = fields.One2many('ca.righe_accesso', 'registro_accesso_id')
    active = fields.Boolean(default=True)