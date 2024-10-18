from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import random
import string

class CaRichiestaServiziPersona(models.Model):
    _name = 'ca.richiesta_servizi_persona'
    _description = 'Richiesta Servizi Persona'
    _rec_name = 'token'

    token = fields.Char(required=True, readonly=True, copy=False, default=lambda self:self.get_token())
    ca_richiesta_accesso_persona_id = fields.Many2one('ca.richiesta_accesso_persona')
    persona_id = fields.Many2one(related="ca_richiesta_accesso_persona_id.persona_id", store=True)
    ca_anag_servizi_id = fields.Many2one('ca.anag_servizi')
    ca_ente_azienda_id = fields.Many2one(related="ca_anag_servizi_id.ca_ente_azienda_id", store=True)
    ca_settore_ente_id = fields.Many2one(related="ca_anag_servizi_id.ca_settore_ente_id", store=True)
    spazio_id = fields.Many2one(related="ca_anag_servizi_id.spazio_id", store=True)
    ca_persona_id = fields.Many2one(related="ca_anag_servizi_id.ca_persona_id")
    ca_categoria_richiesta_id = fields.Many2one('ca.categoria_richiesta', string="Category")
    ca_categoria_tipo_richiesta_id = fields.Many2one('ca.categoria_tipo_richiesta', string="Request Type")
    ca_anag_tipologie_istanze_id = fields.Many2one(related="ca_richiesta_accesso_persona_id.anag_tipologie_istanze_id", required=True)
    act_application_code = fields.Text()
    act_date = fields.Date()
    description = fields.Text()
    cod_ref = fields.Char(string="CodRef")
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], default="new", required=True, readonly=True)
    ca_anag_avanzamento_rich_id = fields.Many2one('ca.anag_avanzamento_rich',
                                                  readonly=True, 
                                                  string="Advancement")
    expiring = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)

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

    @api.constrains('persona_id', 'date_start', 'date_end', 'ca_anag_servizi_id', 'active')
    def _check_unique(self):
        for record in self:
            richiesta_servizi_persona_id = self.env[
                'ca.richiesta_servizi_persona'
            ].search([
                ('id', '!=', record.id),
                ('persona_id', '=', record.persona_id.id),
                ('date_start', '=', record.date_start),
                ('date_end', '=', record.date_end),
                ('ca_anag_servizi_id', '=', record.ca_anag_servizi_id.id)
            ])
            if richiesta_servizi_persona_id:
                raise UserError(_('Esiste già un record con stesso servizio e persona in questo periodo di validità'))

    def create(self, vals):
        res = super(CaRichiestaServiziPersona, self).create(vals)
        for record in res:
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res
    
    def write(self, vals):
        res = super(CaRichiestaServiziPersona, self).write(vals)
        for record in self:
            if not record.date_start:
                record.date_start = fields.date.today()
            if not record.date_end:
                date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
                record.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return res

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        richiesta_servizi_persona_id = self.env['ca.richiesta_servizi_persona'].search([('token', '=', token)])
        if richiesta_servizi_persona_id:
            self.get_token()    
        return token