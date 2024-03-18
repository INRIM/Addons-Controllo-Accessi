from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaPuntoAccessoPersona(models.Model):
    _name = 'ca.punto_accesso_persona'
    _description = 'Punto Accesso Persona'
    _rec_name = 'ca_lettore_id'

    ca_lettore_id = fields.Many2one(related="ca_tag_lettore_id.ca_lettore_id", required=True)
    ca_tag_lettore_id = fields.Many2one('ca.tag_lettore', required=True, readonly=True)
    ca_tag_persona = fields.Many2one('ca.tag_persona', required=True, readonly=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ], readonly=True)
    date = fields.Date(readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains('ca_tag_lettore_id', 'ca_tag_persona', 'date', 'state', 'active')
    def _check_unique(self):
        for record in self:
            punto_accesso_persona_id = self.env[
                'ca.punto_accesso_persona'
            ].search([
                ('id', '!=', record.id),
                ('ca_tag_lettore_id', '=', record.ca_tag_lettore_id.id),
                ('ca_tag_persona', '=', record.ca_tag_persona.id),
                ('date', '=', record.date),
                ('state', '=', 'active')
            ])
            if punto_accesso_persona_id:
                raise UserError(_('Puo’ esistere solo una configurazione per tag lettore, tag persona, data, in stato attivo'))

    def elabora_persone(self, lettore_id):
        try:
            punto_accesso_id = self.env['ca.punto_accesso'].search([
                ('ca_lettore_id', '=', lettore_id.id)
            ])
            for tag in punto_accesso_id.ca_tag_lettore_ids:
                if tag.tag_in_use:
                    tag_persona_id = self.env['ca.tag_persona'].search([
                        ('ca_tag_id', '=', tag.ca_tag_id.id)
                    ])
                    old_punto_accesso_persona_id = self.env[
                        'ca.punto_accesso_persona'
                    ].search([
                        ('ca_tag_lettore_id', '=', tag.id),
                        ('ca_tag_persona', '=', tag_persona_id.id),
                        ('date', '=', fields.date.today()),
                        ('state', '=', 'active')
                    ])
                    if old_punto_accesso_persona_id and tag.temp:
                        old_punto_accesso_persona_id.state = 'expired'
                    new_punto_accesso_persona_id = self.env[
                        'ca.punto_accesso_persona'
                    ].create({
                        'ca_tag_lettore_id': tag.id,
                        'ca_tag_persona': tag_persona_id.id,
                        'state': 'active',
                        'date': fields.date.today()
                    })
                    return new_punto_accesso_persona_id
        except Exception as e:
            return None

    def elabora_persone_lettore(self, nome_lettore):
        lettore_id = self.env['ca.lettore'].search([
            ('name', '=', nome_lettore)
        ], limit=1)
        if lettore_id:
            return self.elabora_persone(lettore_id)
        else:
            return None