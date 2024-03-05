from odoo import models, fields, api
from datetime import datetime

class CaSettoreEnte(models.Model):
    _name = 'ca.settore_ente'
    _description = 'Settore Ente'

    name = fields.Char(required=True)
    abbreviation = fields.Char()
    ca_persona_id = fields.Many2one('ca.persona', string="Referent")
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef")
    ca_spazio_id = fields.Many2one('ca.spazio', string="Position", required=True)
    date_start = fields.Date()
    date_end = fields.Date()
    type_ids = fields.Many2many('ca.tipo_persona', compute="_compute_type_ids")

    def _compute_type_ids(self):
        for record in self:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]

    def create(self, vals):
        res = super(CaSettoreEnte, self).create(vals)
        for record in res:
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res
    
    def write(self, vals):
        res = super(CaSettoreEnte, self).write(vals)
        for record in self:
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res