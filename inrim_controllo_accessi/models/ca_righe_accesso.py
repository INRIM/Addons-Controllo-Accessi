from odoo import models, fields

class CaRigheAccesso(models.Model):
    _name = 'ca.righe_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Righe Accesso'

    registro_accesso_id = fields.Many2one('ca.anag_registro_accesso',
        string="Access Register")
    persona_id = fields.Many2one('ca.persona')
    spazio_id = fields.Many2one('ca.spazio', string="Space")
    tipo_spazio_id = fields.Many2one('ca.tipo_spazio', string="Space Type")
    tag_persona_id = fields.Many2one('ca.tag_persona', string="Tag Person")
    datetime = fields.Datetime(string="Date/Time")
    management = fields.Text()