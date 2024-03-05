from odoo import models, fields, _

class ModelName(models.TransientModel):
    _name = 'ca.sposta_punto_accesso'
    _description = 'Sposta Punto Accesso'

    old_ca_spazio_id = fields.Many2one('ca.spazio', 
        string="Old Position", readonly=True
    )
    new_ca_spazio_id = fields.Many2one('ca.spazio', string="New Position", 
        required=True, domain="[('id', '!=', old_ca_spazio_id)]"
    )
    ca_punto_accesso_id = fields.Many2one('ca.punto_accesso', readonly=True)

    def sposta_punto_accesso(self):
        self.ca_punto_accesso_id.active = False
        vals = {
            'ca_spazio_id': self.new_ca_spazio_id.id,
            'ca_lettore_id': self.ca_punto_accesso_id.ca_lettore_id.id,
            'typology': self.ca_punto_accesso_id.typology,
            'ca_persona_id': self.ca_punto_accesso_id.ca_persona_id.id 
                if self.ca_punto_accesso_id.ca_persona_id else False,
            'last_update_reader': self.ca_punto_accesso_id.last_update_reader,
            'last_reading_events': self.ca_punto_accesso_id.last_reading_events,
            'events_to_read_num': self.ca_punto_accesso_id.events_to_read_num,
            'events_read_num': self.ca_punto_accesso_id.events_read_num,
            'enable_sync': self.ca_punto_accesso_id.enable_sync,
            'date_start': self.ca_punto_accesso_id.date_start,
            'date_end': self.ca_punto_accesso_id.date_end,
            'ca_tag_lettore_ids': self.ca_punto_accesso_id.ca_tag_lettore_ids
        }
        new_ca_punto_accesso_id = self.env['ca.punto_accesso'].create(vals)
        return {
            'name': _(new_ca_punto_accesso_id.name),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ca.punto_accesso',
            'res_id': new_ca_punto_accesso_id.id
        }