from odoo import models, fields

class CaAnagServizi(models.Model):
    _name = 'ca.anag_servizi'
    _description = 'Anagrafica Servizi'

    name = fields.Char(required=True)
    ca_settore_ente_id = fields.Many2one('ca.settore_ente')
    ca_persona_id = fields.Many2one('ca.persona', string="Referent", domain="[('type_ids', '=', type_ids)]")
    type_ids = fields.Many2many('ca.tipo_persona', compute="_compute_type_ids")
    virtual = fields.Boolean()
    ca_spazio_id = fields.Many2one('ca.spazio', string="Position")
    generic = fields.Boolean()
    spazio_id = fields.Many2one('ca.spazio', required=True)
    tipo_spazio_id = fields.Many2one(related="spazio_id.tipo_spazio_id", store=True)
    abbreviation = fields.Char()
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef")
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    def _compute_type_ids(self):
        for record in self:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]