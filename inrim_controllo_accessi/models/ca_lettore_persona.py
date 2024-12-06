from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaLettorePersona(models.Model):
    _name = 'ca.lettore_persona'
    _inherit = "ca.model.base.mixin"
    _description = 'Lettore Persona'
    _rec_name = 'ca_lettore_id'

    ca_tag_lettore_id = fields.Many2one(
        'ca.tag_lettore', required=True, readonly=True)
    ca_lettore_id = fields.Many2one(
        related="ca_tag_lettore_id.ca_lettore_id", store=True, index=True)
    ca_punto_accesso_id = fields.Many2one(
        related="ca_tag_lettore_id.ca_punto_accesso_id", store=True, index=True)
    ca_tag_persona = fields.Many2one(
        'ca.tag_persona', ondelete='cascade', required=True,
        readonly=True)
    ca_persona_id = fields.Many2one(
        related="ca_tag_persona.ca_persona_id", store=True, readonly=True)

    date_start = fields.Datetime(
        related="ca_tag_persona.date_start", readonly=True, store=True)
    date_end = fields.Datetime(
        related="ca_tag_persona.date_end", readonly=True, store=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('scheduled', 'Scheduled')
    ], readonly=True)

    active = fields.Boolean(default=True)

    @api.constrains(
        'ca_tag_lettore_id', 'ca_tag_persona', 'state', 'active')
    def _check_unique(self):
        for record in self:
            punto_accesso_persona_id = self.env[
                'ca.lettore_persona'
            ].search([
                ('id', '!=', record.id),
                ('ca_tag_lettore_id', '=', record.ca_tag_lettore_id.id),
                ('ca_tag_persona', '=', record.ca_tag_persona.id),
                ('date_start', '<=', record.date_start),
                ('date_end', '>=', record.date_end),
                ('state', 'not in', ['expired'])
            ])
            if punto_accesso_persona_id:
                raise UserError(
                    _('Puo’ esistere solo una configurazione per tag lettore, tag persona, data, in stato attivo'))

    @api.onchange('date_start', 'date_end')
    def _compute_expired(self):
        for record in self:
            record.check_update_state()

    def elabora_persone(self, lettore_id):
        vals = []
        ca_tag_lettore_ids = self.env['ca.tag_lettore'].search([
            ('ca_lettore_id', '=', lettore_id.id), ('state', 'not in', ['expired']),
        ])

        if ca_tag_lettore_ids:
            for tag_lettore in ca_tag_lettore_ids:
                tag_lettore.check_update_state()
                if tag_lettore.state == 'active':
                    now = fields.Datetime.now()
                    tag_persona_id = self.env['ca.tag_persona'].get_current_by_tag(
                        tag_lettore.ca_tag_id)
                    if tag_persona_id:
                        lettore_persona_id = self.env[
                            'ca.lettore_persona'
                        ].search([
                            ('ca_tag_lettore_id', '=', tag_lettore.id),
                            ('ca_tag_persona', '=', tag_persona_id.id),
                            ('state', 'not in', ['expired'])
                        ])
                        if not lettore_persona_id:
                            new_lettore_persona_id = self.env[
                                'ca.lettore_persona'
                            ].create({
                                'ca_tag_lettore_id': tag_lettore.id,
                                'ca_tag_persona': tag_persona_id.id
                            })
                            new_lettore_persona_id.check_update_state()
                            vals.append(new_lettore_persona_id)
        return vals

    def elabora_persone_lettore(self, nome_lettore):
        lettore_id = self.env['ca.lettore'].search([
            ('name', '=', nome_lettore)
        ], limit=1)
        if lettore_id:
            return self.elabora_persone(lettore_id)
        else:
            return None

    def check_update_state(self):
        now = fields.Datetime.now()
        self.ensure_one()
        if self.date_start <= now <= self.date_end:
            self.state = 'active'
        elif self.date_start > now:
            self.state = 'scheduled'
        elif self.date_end <= now:
            self.state = 'expired'

    def check_update_by_date_valididty(self):
        for person_reader in self.env['ca.lettore_persona'].search(
                [('state', 'not in', ['expired'])]):
            if person_reader:
                person_reader.check_update_state()

    def _cron_check_validity_person_reader(self):
        self.check_update_by_date_valididty()
