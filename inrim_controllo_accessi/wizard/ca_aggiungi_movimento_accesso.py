from odoo import models, fields, api

class CaAggiungiMovimentoAccesso(models.TransientModel):
    _name = 'ca.aggiungi_movimento_accesso'
    _description = 'Aggiungi Movimento Accesso'

    anag_registro_accesso_id = fields.Many2one('ca.anag_registro_accesso')
    ca_ente_azienda_id = fields.Many2one('ca.ente_azienda', string="Position")
    ca_punto_accesso = fields.Many2one('ca.punto_accesso', required=True)
    ca_tag_persona_id = fields.Many2one('ca.tag_persona', required=True)
    ca_tag_persona_ids = fields.Many2many('ca.tag_persona', 
                                        compute="_compute_ca_tag_persona_ids",
                                        store=True)
    datetime = fields.Datetime(required=True)
    tipo_ente_azienda_ids = fields.Many2many('ca.tipo_ente_azienda',
                    default=lambda self: self.default_tipo_ente_azienda_ids())

    def default_tipo_ente_azienda_ids(self):
        return [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id, 
                self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
            ])]

    @api.depends('ca_punto_accesso')
    def _compute_ca_tag_persona_ids(self):
        self.ca_tag_persona_ids = False
        if self.ca_punto_accesso:
            for tag in self.ca_punto_accesso.ca_spazio_id.righe_persona_ids:
                if tag.tag_persona_id:
                    self.ca_tag_persona_ids += tag.tag_persona_id

    @api.onchange('ca_ente_azienda_id')
    def _onchange_ca_ente_azienda_id(self):
        if self.ca_ente_azienda_id:
            if self.ca_punto_accesso.ente_azienda_id != self.ca_ente_azienda_id:
                self.ca_punto_accesso = False
                self.ca_tag_persona_id = False

    def action_done(self):
        return self.anag_registro_accesso_id.aggiungi_riga_accesso(
            self.ca_punto_accesso, self.ca_tag_persona_id, self.datetime
        )