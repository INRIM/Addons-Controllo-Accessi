from odoo import models, fields, api

class CaRighePersona(models.Model):
    _name = 'ca.righe_persona'
    _description = 'Righe Persona'

    spazio_id = fields.Many2one('ca.spazio')
    tag_persona_id = fields.Many2one('ca.tag_persona')
    date_start = fields.Date(string='Valid Access From')
    date_end = fields.Date(string='Valid Access To')
    suspended = fields.Boolean()