from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import string
from datetime import timedelta

class CaRichiestaAccessoPersona(models.Model):
    _name = 'ca.richiesta_accesso_persona'
    _description = 'Richiesta Accesso Persona'
    _rec_name = 'token'

    token = fields.Char(required=True, readonly=True, copy=False,
                        default=lambda self:self.get_token())
    ca_persona_id = fields.Many2one('ca.persona', string="Referent", required=True)
    type_ids = fields.Many2many('ca.tipo_persona', default=lambda self:self.default_type_ids())
    persona_id = fields.Many2one('ca.persona')
    freshman = fields.Char(related='persona_id.freshman')
    external_freshman = fields.Char()
    external_companies = fields.Boolean(compute="_compute_external_companies", store=True)
    anag_tipologie_istanze_id = fields.Many2one('ca.anag_tipologie_istanze',
                                                required=True, 
                                                string="Application Act")
    act_application_code = fields.Text(required=True)
    ca_categoria_richiesta_id = fields.Many2one('ca.categoria_richiesta', string="Category")
    ca_categoria_tipo_richiesta_id = fields.Many2one('ca.categoria_tipo_richiesta', string="Request Type")
    categoria_richiesta_id = fields.Many2one('ca.categoria_richiesta', string="Activity Title")
    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled')
    ], required=True, readonly=True, default="new")
    ca_anag_avanzamento_rich_id = fields.Many2one('ca.anag_avanzamento_rich',
                                                  readonly=True, 
                                                  string="Advancement")
    expiring = fields.Boolean(readonly=True)
    note = fields.Html()
    ca_richiesta_servizi_persona_ids = fields.One2many(
        'ca.richiesta_servizi_persona', 'ca_richiesta_accesso_persona_id')
    ca_richiesta_accesso_id = fields.Many2one('ca.richiesta_accesso')
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    @api.constrains('persona_id', 'date_start', 'date_end', 'active')
    def _check_unique(self):
        for record in self:
            richiesta_accesso_persona_id = self.env['ca.richiesta_accesso_persona'].search([
                ('id', '!=', record.id),
                ('persona_id', '=', record.persona_id.id),
                ('date_start', '=', record.date_start),
                ('date_end', '=', record.date_end)
            ])
            if richiesta_accesso_persona_id:
                raise UserError(_('Esiste già un record per questa persona in questo periodo di validità'))
            
    @api.depends('ca_categoria_tipo_richiesta_id')
    def _compute_external_companies(self):
        for record in self:
            record.external_companies = False
            if (
                record.ca_categoria_tipo_richiesta_id == self.env.ref(
                'inrim_anagrafiche.ca_categoria_tipo_richiesta_ditte_esterne')
            ):
                record.external_companies = True

    def default_type_ids(self):
        type_ids = [(6, 0, [
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
        ])]
        return type_ids
    
    @api.model_create_multi
    def create(self, vals):
        res = super(CaRichiestaAccessoPersona, self).create(vals)
        for record in res:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
        return res
    
    def write(self, vals_list):
        res = super(CaRichiestaAccessoPersona, self).write(vals_list)
        for record in self:
            vals_list['type_ids'] = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
        return res

    def aggiorna_stato_richiesta(self, stato=None):
        for record in self:
            if (
                self.env.user.has_group('inrim_controllo_accessi_base.ca_ca') or
                self.env.user.has_group('inrim_controllo_accessi_base.ca_ru') or
                self.env.user.has_group('inrim_controllo_accessi_base.ca_spp')
            ):
                today = fields.datetime.now()
                if stato:
                    record.state = stato
                for line in record.ca_richiesta_servizi_persona_ids:
                    line.aggiorna_stato_richiesta(stato)
                if (
                    record.date_start > today
                    and record.state == 'approved'
                    and not stato
                ):
                    record.state = 'scheduled'
                    record.ca_anag_avanzamento_rich_id = self.env.ref(
                        'inrim_controllo_accessi.ca_anag_avanzamento_rich_attesa_in_attivazione').id
                    break
                if (
                    record.date_start <= today <= record.date_end
                    and record.state in ['approved', 'scheduled']
                    and not stato
                ):
                    record.state = 'valid'
                    record.ca_anag_avanzamento_rich_id = self.env.ref(
                        'inrim_controllo_accessi.ca_anag_avanzamento_rich_attesa_attiva').id
                    record.expiring = False
                    break
                expire_days = self.env[
                    'ir.config_parameter'
                ].sudo().get_param('date_end.expiredays')
                if record.date_end - today <= timedelta(days=int(expire_days)):
                    record.expiring = True
                if (
                    record.date_end < today
                    and not stato
                ):
                    record.state = 'expired'
                    record.ca_anag_avanzamento_rich_id = self.env.ref(
                        'inrim_controllo_accessi.ca_anag_avanzamento_rich_attesa_conclusa').id
                    record.expiring = False
                    break
            else:
                raise UserError(_('Errore utente non abilitato'))

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        richiesta_accesso_persona_id = self.env[
            'ca.richiesta_accesso_persona'
        ].search([('token', '=', token)])
        if richiesta_accesso_persona_id:
            self.get_token()
        return token