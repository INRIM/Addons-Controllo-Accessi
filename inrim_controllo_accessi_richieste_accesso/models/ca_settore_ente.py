from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class CaSettoreEnte(models.Model):
    _name = 'ca.settore_ente'
    _inherit = "ca.model.base.mixin"
    _description = 'Settore Ente'

    name = fields.Char(required=True)
    abbreviation = fields.Char(compute="_compute_abbreviation", store=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent", required=True)
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef")
    ca_ente_azienda_id = fields.Many2one('ca.ente_azienda', string="Position", required=True)
    date_start = fields.Date()
    date_end = fields.Date()
    type_ids = fields.Many2many('ca.tipo_persona', default=lambda self:self.default_type_ids())
    tipo_ente_azienda_ids = fields.Many2many('ca.tipo_ente_azienda', 
                        compute="_compute_tipo_ente_azienda_ids")
    
    def rest_boby_hint(self):
        return {
            "name": "",
            "ca_persona_id": "",
            "ca_ente_azienda_id": ""
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'ca_persona_id': self.f_m2o(self.ca_persona_id),
            'description': self.description,
            'cod_ref': self.cod_ref,
            'ca_ente_azienda_id': self.f_m2o(self.ca_ente_azienda_id),
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end),
            'type_ids': self.f_m2m(self.type_ids),
            'tipo_ente_azienda_ids': self.f_m2m(self.tipo_ente_azienda_ids)
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'ca_persona_id', 'ca_ente_azienda_id'
            ])
        return body, msg
    
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

    def default_type_ids(self):
        type_ids = [(6, 0, [
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
        ])]
        return type_ids

    @api.model_create_multi
    def create(self, vals):
        res = super(CaSettoreEnte, self).create(vals)
        for record in res:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res
    
    def write(self, vals):
        res = super(CaSettoreEnte, self).write(vals)
        for record in self:
            vals['type_ids'] = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res