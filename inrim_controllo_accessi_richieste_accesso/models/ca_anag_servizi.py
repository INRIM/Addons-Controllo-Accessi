from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class CaAnagServizi(models.Model):
    _name = 'ca.anag_servizi'
    _inherit = "ca.model.base.mixin"
    _description = 'Anagrafica Servizi'

    name = fields.Char(required=True)
    ca_settore_ente_id = fields.Many2one('ca.settore_ente')
    ca_settore_persona_id = fields.Many2one(related="ca_settore_ente_id.ca_persona_id")
    settore_ente_name = fields.Char(related='ca_settore_ente_id.name', store=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent", required=True)
    type_ids = fields.Many2many('ca.tipo_persona', default=lambda self:self.default_type_ids())
    virtual = fields.Boolean()
    ca_ente_azienda_id = fields.Many2one('ca.ente_azienda', string="Position")
    generic = fields.Boolean()
    spazio_id = fields.Many2one('ca.spazio')
    tipo_spazio_id = fields.Many2one(related="spazio_id.tipo_spazio_id", store=True)
    abbreviation = fields.Char()
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef", compute="_compute_cod_ref", store=True)
    date_start = fields.Date()
    date_end = fields.Date()
    tipo_ente_azienda_ids = fields.Many2many('ca.tipo_ente_azienda', 
                        compute="_compute_tipo_ente_azienda_ids")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('cod_ref', 'UNIQUE(cod_ref)',
         'This CodRef already exists.')
    ]

    def rest_boby_hint(self):
        return {
            "name": "",
            "ca_persona_id": "",
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'ca_settore_ente_id': self.f_m2o(self.ca_settore_ente_id),
            'ca_settore_persona_id': self.f_m2o(self.ca_settore_persona_id),
            'settore_ente_name': self.settore_ente_name,
            'ca_persona_id': self.f_m2o(self.ca_persona_id),
            'type_ids': self.f_m2m(self.type_ids),
            'virtual': self.virtual,
            'ca_ente_azienda_id': self.f_m2o(self.ca_ente_azienda_id),
            'generic': self.generic,
            'spazio_id': self.f_m2o(self.spazio_id),
            'tipo_spazio_id': self.f_m2o(self.tipo_spazio_id),
            'abbreviation': self.abbreviation,
            'description': self.description,
            'cod_ref': self.cod_ref,
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end),
            'tipo_ente_azienda_ids': self.f_m2m(self.tipo_ente_azienda_ids)
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'ca_persona_id'
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

    @api.constrains('name', 'ca_settore_ente_id', 'active')
    def _check_unique(self):
        for record in self:
            anag_servizi_id = self.env['ca.anag_servizi'].search([
                ('id', '!=', record.id),
                ('name', '=', record.name),
                ('ca_settore_ente_id', '=', record.ca_settore_ente_id.id)
            ])
            if anag_servizi_id:
                raise UserError(_('Esiste già un altro servizio con stesso nome e settore'))
            
    @api.onchange('ca_settore_ente_id')
    def _onchange_ca_settore_ente_id(self):
        for record in self:
            if record.ca_settore_ente_id:
                record.ca_persona_id = record.ca_settore_ente_id.ca_persona_id
    
    def get_by_codref(self, cod_ref):
        anag_servizi_id = self.env['ca.anag_servizi'].search([
            ('cod_ref', '=', cod_ref)
        ], limit=1)
        if anag_servizi_id:
            return anag_servizi_id
        else:
            return None
        
    def get_by_nome_settore(self, name=None, nome_settore=None):
        anag_servizi_ids = self.env['ca.anag_servizi'].search([
            ('name', '=', name),
            ('settore_ente_name', '=', nome_settore)
        ])
        res = []
        for anag in anag_servizi_ids:
            res.append(anag)
        return res

    @api.depends('name', 'ca_settore_ente_id')
    def _compute_cod_ref(self):
        for record in self:
            record.cod_ref = False
            if record.name and record.ca_settore_ente_id:
                record.cod_ref = (record.ca_settore_ente_id.name + '_' + record.name).lower()

    def default_type_ids(self):
        type_ids = [(6, 0, [
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
        ])]
        return type_ids

    @api.model_create_multi
    def create(self, vals):
        res = super(CaAnagServizi, self).create(vals)
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
        res = super(CaAnagServizi, self).write(vals)
        for record in self:
            vals['type_ids']= [(6, 0, [
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