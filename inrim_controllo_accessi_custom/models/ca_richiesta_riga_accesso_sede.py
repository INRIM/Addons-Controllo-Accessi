from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class CaRichiestaRigaAccessoSede(models.Model):
    _name = 'ca.richiesta_riga_accesso_sede'
    _description = 'Richiesta Riga Accesso Sede'
    _rec_name = 'display_name'

    persona_id = fields.Many2one('ca.persona', 
        default=lambda self:self._default_persona_id(), required=True)
    ente_azienda_id = fields.Many2one('ca.ente_azienda', required=True)
    punto_accesso_id = fields.Many2one('ca.punto_accesso', required=True, ondelete='cascade')
    direction = fields.Selection(related="punto_accesso_id.direction", required=True)
    datetime_event = fields.Datetime(required=True)
    display_name = fields.Char(compute='_compute_display_name')
    is_headquarters = fields.Many2one('ca.tipo_ente_azienda',
        compute="_compute_is_headquarters", 
        default=lambda self:self._default_is_headquarters())

    @api.onchange('persona_id', 'ente_azienda_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = False
            if record.persona_id and record.ente_azienda_id:
                record.display_name = (
                    f'''{record.persona_id.display_name} - 
                    {record.ente_azienda_id.display_name}'''
                )

    def _default_persona_id(self):
        user_id = self.env.user.id
        persona_id = self.env['ca.persona'].search([
            ('associated_user_id', '=', user_id)
        ], limit=1)
        if persona_id:
            return persona_id
    
    def _default_is_headquarters(self):
        return self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id

    def _compute_is_headquarters(self):
        self.is_headquarters = self.env.ref(
            'inrim_anagrafiche.tipo_ente_azienda_sede').id
        
    @api.constrains('datetime_event')
    def _check_datetime_event(self):
        delta_min_riga_accesso = float(
            self.env[
                'ir.config_parameter'
            ].sudo().get_param('ca.delta_min_riga_accesso', default=0.0))
        for record in self:
            delta_hours = timedelta(hours=delta_min_riga_accesso)
            min_datetime = record.datetime_event - delta_hours
            max_datetime = record.datetime_event + delta_hours
            richiesta_accesso_sede_id = self.search([
                ('persona_id', '=', record.persona_id.id),
                ('ente_azienda_id', '=', record.ente_azienda_id.id),
                ('direction', '=', record.direction),
                ('datetime_event', '>=', min_datetime),
                ('datetime_event', '<=', max_datetime),
                ('id', '!=', record.id)
            ])
            if richiesta_accesso_sede_id:
                raise ValidationError(_(f"Esiste già un altro record con data/ora evento con differenza di ore inferiore a {delta_min_riga_accesso} ore."))

    def elabora_richieste_registro_accesso(self):
        for record in self:
            today = fields.Date.today()
            tag_ids = self.env['ca.tag_persona'].search([
                ('ca_persona_id', '=', record.persona_id.id),
                ('date_start', '<=', today),
                ('date_end', '>=', today)
            ]).mapped('ca_tag_id')
            ca_tag_id = False
            if tag_ids:
                for tag_lettore in record.punto_accesso_id.ca_tag_lettore_ids:
                    if not ca_tag_id:
                        if tag_lettore.ca_tag_id in tag_ids:
                            ca_tag_id = tag_lettore.ca_tag_id
            else:
                raise ValidationError(_(f"Non ci sono tag persona in corso di validità per la persona '{record.persona_id.display_name}'"))
            if ca_tag_id:
                tag_persona_id = self.env['ca.tag_persona'].search([
                    ('ca_persona_id', '=', record.persona_id.id),
                    ('ca_tag_id', '=', ca_tag_id.id),
                    ('date_start', '<=', today),
                    ('date_end', '>=', today)
                ], limit=1)
                anag_registro_accesso_id = self.env['ca.anag_registro_accesso'].search([
                    ('ca_punto_accesso_id', '=', record.punto_accesso_id.id),
                    ('ca_tag_persona_id', '=', tag_persona_id.id),
                    ('direction', '=', record.direction),
                    ('datetime_event', '=', record.datetime_event)
                ])
                if not anag_registro_accesso_id:
                    anag_registro_accesso_id = self.env['ca.anag_registro_accesso'].create({
                        'ca_punto_accesso_id': record.punto_accesso_id.id,
                        'ca_tag_persona_id': tag_persona_id.id,
                        'direction': record.direction,
                        'datetime_event': record.datetime_event,
                        'type': 'manual',
                    })
            else:
                raise ValidationError(_(f"Non sono presenti tag in corso di validità per la persona '{record.persona_id.display_name}' nel punto accesso '{record.punto_accesso_id.display_name}'"))
            return {
                'name': _('Access Register'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'ca.anag_registro_accesso',
                'domain': [('id', '=', anag_registro_accesso_id.id)]
            }
                
