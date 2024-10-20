from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import random
import string

class CaRichiestaAccesso(models.Model):
    _name = 'ca.richiesta_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Richiesta Accesso'
    _rec_name = 'token'

    token = fields.Char(required=True, readonly=True, copy=False, default=lambda self:self.get_token())
    ca_categoria_richiesta_id = fields.Many2one('ca.categoria_richiesta', string="Category Activity")
    ca_categoria_tipo_richiesta_id = fields.Many2one('ca.categoria_tipo_richiesta', string="Activity Type")
    categoria_richiesta_id = fields.Many2one('ca.categoria_richiesta', string="Activity Title")
    ca_persona_id = fields.Many2one('ca.persona', string="Referent", required=True)
    type_ids = fields.Many2many('ca.tipo_persona', default=lambda self:self.default_type_ids())
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled')
    ], required=True, default="new")
    ca_anag_avanzamento_rich_id = fields.Many2one('ca.anag_avanzamento_rich',
                                                  readonly=True, 
                                                  string="Advancement")
    expiring = fields.Boolean(readonly=True)
    note = fields.Html()
    ca_richiesta_accesso_persona_ids = fields.One2many(
        'ca.richiesta_accesso_persona', 'ca_richiesta_accesso_id')
    anag_tipologie_istanze_id = fields.Many2one('ca.anag_tipologie_istanze',
                                                string="Application Act")
    act_application_code = fields.Text()

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def aggiorna_stato_richiesta(self, stato=None):
        for record in self:
            if (
                self.env.user.has_group('controllo_accessi.ca_ca') or
                self.env.user.has_group('controllo_accessi.ca_ru') or
                self.env.user.has_group('controllo_accessi.ca_spp')
            ):
                today = fields.date.today()
                if stato:
                    record.state = stato
                for line in record.ca_richiesta_accesso_persona_ids:
                    line.aggiorna_stato_richiesta(stato)
                if (
                    record.date_start > today
                    and record.state == 'approved'
                    and not stato
                ):
                    record.state = 'scheduled'
                    record.ca_anag_avanzamento_rich_id = self.env.ref(
                        'inrim_controllo_accessi_richieste_accesso.ca_anag_avanzamento_rich_attesa_in_attivazione').id
                    break
                if (
                    record.date_start <= today <= record.date_end
                    and record.state in ['approved', 'scheduled']
                    and not stato
                ):
                    record.state = 'valid'
                    record.ca_anag_avanzamento_rich_id = self.env.ref(
                        'inrim_controllo_accessi_richieste_accesso.ca_anag_avanzamento_rich_attesa_attiva').id
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
                        'inrim_controllo_accessi_richieste_accesso.ca_anag_avanzamento_rich_attesa_conclusa').id
                    record.expiring = False
                    break
            else:
                raise UserError(_('Errore utente non abilitato'))
            
    def default_type_ids(self):
        type_ids = [(6, 0, [
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
            self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
        ])]
        return type_ids
    
    @api.model_create_multi
    def create(self, vals):
        res = super(CaRichiestaAccesso, self).create(vals)
        for record in res:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
        return res
    
    def write(self, vals_list):
        res = super(CaRichiestaAccesso, self).write(vals_list)
        for record in self:
            vals_list['type_ids'] = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id, 
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
            ])]
        return res

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        richiesta_accesso_id = self.env['ca.richiesta_accesso'].search([('token', '=', token)])
        if richiesta_accesso_id:
            self.get_token()    
        return token