from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class CaSettoreEnte(models.Model):
    _name = 'ca.settore_ente'
    _description = 'Settore Ente'

    name = fields.Char(required=True)
    abbreviation = fields.Char(compute="_compute_abbreviation", store=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent")
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef")
    ca_ente_azienda_id = fields.Many2one('ca.ente_azienda', string="Position", required=True)
    date_start = fields.Date()
    date_end = fields.Date()
    type_ids = fields.Many2many('ca.tipo_persona', compute="_compute_type_ids")
    tipo_ente_azienda_ids = fields.Many2many('ca.tipo_ente_azienda', 
                        compute="_compute_tipo_ente_azienda_ids")
    
    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def _compute_tipo_ente_azienda_ids(self):
        for record in self:
            record.tipo_ente_azienda_ids = [(6, 0, [
                    self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id, 
                    self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id
                ])]

    @api.depends('name')
    def _compute_abbreviation(self):
        for record in self:
            record.abbreviation = False
            if record.name:
                words = record.name.split()
                record.abbreviation = ''.join([word[0] for word in words if word[0].isupper()])

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