from odoo import models, fields

class CaRigheAccesso(models.Model):
    _name = 'ca.righe_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Righe Accesso'

    registro_accesso_id = fields.Many2one('ca.anag_registro_accesso')
    persona_id = fields.Many2one('ca.persona')
    spazio_id = fields.Many2one('ca.spazio')
    tipo_spazio_id = fields.Many2one('ca.tipo_spazio')
    tag_persona_id = fields.Many2one('ca.tag_persona')
    datetime = fields.Datetime(string="Date/Time")
    management = fields.Text()