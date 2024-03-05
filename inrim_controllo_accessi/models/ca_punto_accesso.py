from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaPuntoAccesso(models.Model):
    _name = 'ca.punto_accesso'
    _description = 'Punto Accesso'

    name = fields.Char(compute="_compute_name", store=True)
    ca_spazio_id = fields.Many2one('ca.spazio', required=True, string="Position")
    tipo_spazio_id = fields.Many2one(related='ca_spazio_id.tipo_spazio_id', string="Position Type")
    ente_azienda_id = fields.Many2one(related='ca_spazio_id.ente_azienda_id', string="Headquarters Location")
    ca_lettore_id = fields.Many2one('ca.lettore', required=True)
    system_error = fields.Boolean(related="ca_lettore_id.system_error", store=True, string="Reader Error")
    direction = fields.Selection(related="ca_lettore_id.direction")
    typology = fields.Selection([
        ('stamping', 'Stamping'),
        ('local_access', 'Local Access')
    ], required=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent")
    type_ids = fields.Many2many('ca.tipo_persona', compute="_compute_type_ids")
    last_update_reader = fields.Datetime()
    last_reading_events = fields.Datetime()
    events_to_read_num = fields.Integer(string="Number of Events To Read")
    events_read_num = fields.Integer(string="Number of Events Read")
    enable_sync = fields.Boolean(
        string="Enabled",
        help="Enable/Disable remote player synchronization"
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    ca_tag_lettore_ids = fields.One2many('ca.tag_lettore', 'ca_punto_accesso_id')
    active = fields.Boolean(default=True)

    def _compute_type_ids(self):
        for record in self:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id
            ])]

    @api.depends('ca_spazio_id', 'ca_lettore_id')
    def _compute_name(self):
        for record in self:
            record.name = '/'
            if record.ca_spazio_id and record.ca_lettore_id:
                record.name = record.ca_spazio_id.name + ' ' + record.ca_lettore_id.name

    @api.constrains('ca_lettore_id', 'active')
    def _check_ca_lettore_id(self):
        for record in self:
            punto_accesso_ids = self.search([
                ('ca_lettore_id', '=', record.ca_lettore_id.id),
                ('id', '!=', record.id)
            ])
            if punto_accesso_ids:
                raise UserError(_('Reader already in use in another location'))
            
    def commuta_abilitazione(self):
        for record in self:
            if record.enable_sync:
                record.enable_sync = False
            else:
                record.enable_sync = True
            
    def action_sposta_punto_accesso(self):
        self.ensure_one()
        return {
            'name': _('Sposta Punto Accesso'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ca.sposta_punto_accesso',
            'target': 'new',
            'context': {
                'default_old_ca_spazio_id': self.ca_spazio_id.id,
                'default_ca_punto_accesso_id': self.id
            }
        }
    
    def persone_abilitate(self):
        return {
            'name': _('Qualified People'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.punto_accesso_persona',
            'domain': [('date', '=', fields.date.today())],
        }