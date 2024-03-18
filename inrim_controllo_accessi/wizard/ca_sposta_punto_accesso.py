from odoo import models, fields, _

class SpostaPuntoAccesso(models.TransientModel):
    _name = 'ca.sposta_punto_accesso'
    _description = 'Sposta Punto Accesso'

    old_ca_spazio_id = fields.Many2one('ca.spazio', 
        string="Old Position", readonly=True
    )
    new_ca_spazio_id = fields.Many2one('ca.spazio', string="New Position", 
        required=True, domain="[('id', '!=', old_ca_spazio_id)]"
    )
    ca_punto_accesso_id = fields.Many2one('ca.punto_accesso', readonly=True)

    def action_confirm(self):
        return self.ca_punto_accesso_id.sposta_punto_accesso(self.new_ca_spazio_id)