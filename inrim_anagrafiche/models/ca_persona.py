from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import string

class CaPersona(models.Model):
    _name = 'ca.persona'
    _description = 'Persona'
    _rec_name = "display_name"
    _rec_names_search = ['display_name', 'token']
   
    name = fields.Char(required=True)
    lastname = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    associated_user_id = fields.Many2one('res.users')
    fiscalcode = fields.Char(groups="inrim_controllo_accessi_base.ca_gdpr")
    vat = fields.Char()
    type_ids = fields.Many2many('ca.tipo_persona')
    freshman = fields.Char(groups="inrim_controllo_accessi_base.ca_gdpr")
    nationality = fields.Many2one('res.country', groups="inrim_controllo_accessi_base.ca_gdpr")
    birth_date = fields.Date(groups="inrim_controllo_accessi_base.ca_gdpr")
    birth_place = fields.Char(groups="inrim_controllo_accessi_base.ca_gdpr")
    istat_code = fields.Char(groups="inrim_controllo_accessi_base.ca_gdpr")
    parent_id = fields.Many2one('ca.persona', string='Father Contact', index=True)
    child_ids = fields.One2many('ca.persona', 'parent_id', string='Contact', domain=[('active', '=', True)])
    residence_street = fields.Char()
    residence_street2 = fields.Char()
    residence_city = fields.Char()
    residence_state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', residence_country_id)]")
    residence_zip = fields.Char()
    residence_country_id = fields.Many2one('res.country')
    domicile_street = fields.Char()
    domicile_street2 = fields.Char()
    domicile_city = fields.Char()
    domicile_state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', domicile_country_id)]")
    domicile_zip = fields.Char()
    domicile_country_id = fields.Many2one('res.country')
    domicile_other_than_residence = fields.Boolean()
    ca_documento_ids = fields.One2many('ca.documento', 'ca_persona_id')
    ca_stato_anag_id = fields.Many2one('ca.stato_anag', default=lambda self:self.default_ca_stato_anag_id(), required=True)
    ca_ente_azienda_ids = fields.Many2many('ca.ente_azienda')
    token = fields.Char(required=True, readonly=True, copy=False, default=lambda self:self.get_token())
    present = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], readonly=True)
    uid = fields.Char()
    is_external = fields.Boolean(compute="_compute_bool", store=True)
    is_internal = fields.Boolean(compute="_compute_bool", store=True)
    active = fields.Boolean(default=True)

    @api.constrains('fiscalcode', 'active')
    def _check_unique_fiscalcode(self):
        for record in self:
            if record.fiscalcode:
                persona_id = self.env['ca.persona'].search([
                    ('id', '!=', record.id),
                    ('fiscalcode', '=', record.fiscalcode)
                ])
                if persona_id:
                    raise UserError(_('Esiste già una persona con questo codice fiscale'))
    
    @api.constrains('freshman', 'active')
    def _check_unique_freshman(self):
        for record in self:
            if record.freshman:
                persona_id = self.env['ca.persona'].search([
                    ('id', '!=', record.id),
                    ('freshman', '=', record.freshman)
                ])
                if persona_id:
                    raise UserError(_('Esiste già una persona con questa matricola'))
    
    @api.constrains('ca_documento_ids')
    def _check_external_documento_ids(self):
        for record in self:
            if len(record.ca_documento_ids) == 0 and record.is_external:
                raise UserError(_(
                    'Per una persona esterna è obbligatorio caricare i documenti'))

    @api.onchange('domicile_state_id')
    def _onchange_domicile_state_id(self):
        if self.domicile_state_id.country_id:
            self.domicile_country_id = self.domicile_state_id.country_id

    @api.onchange('residence_state_id')
    def _onchange_residence_state_id(self):
        if self.residence_state_id.country_id:
            self.residence_country_id = self.residence_state_id.country_id

    @api.depends('type_ids')
    def _compute_bool(self):
        for record in self:
            record.is_external = False
            record.is_internal = False
            if self.env.ref('inrim_anagrafiche.tipo_persona_interno').id in record.type_ids.ids:
                record.is_internal = True
            if self.env.ref('inrim_anagrafiche.tipo_persona_esterno').id in record.type_ids.ids:
                record.is_external = True

    @api.depends('name', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = False
            if record.name and record.lastname:
                record.display_name = record.name + ' ' + record.lastname

    def default_ca_stato_anag_id(self):
        return self.env.ref('inrim_anagrafiche.ca_stato_anag_bozza').id

    def action_draft(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_bozza').id

    def action_documents(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_in_attesa_documenti').id

    def action_expired(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_scaduto').id

    def action_in_update(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_in_aggiornamento').id

    def action_checks_in_progress(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_verifiche_in_corso').id

    def action_completed(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref('inrim_anagrafiche.ca_stato_anag_completata').id

    def action_attendance_today(self):
        return {
            'name': _('Access Log'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.anag_registro_accesso',
            'domain': [('ca_ente_azienda_id', 'in', self.ca_ente_azienda_ids.ids)],
        }

    @api.model_create_multi
    def create(self, vals):
        res = super(CaPersona, self).create(vals)
        self._check_external_documento_ids()
        return res
    
    def write(self, vals_list):
        res = super(CaPersona, self).write(vals_list)
        self._check_external_documento_ids()
        return res

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        persona_id = self.env['ca.persona'].search([('token', '=', token)])
        if persona_id:
            self.get_token()
        return token