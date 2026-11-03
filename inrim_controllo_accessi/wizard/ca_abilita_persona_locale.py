import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CaAbilitaPersonaLocale(models.TransientModel):
    _name = 'ca.abilita_persona_locale'
    _description = 'Abilita Persona locale'

    punto_accesso_id = fields.Many2one(
        "ca.punto_accesso", required=True,
        domain=[('typology', '=', 'local_access')],
        string="Access Point"
    )
    persona_id = fields.Many2one("ca.persona")
    referente_id = fields.Many2one(
        'ca.persona', string='Reference person', index=True,
        domain=[('is_internal', '=', True), ("present", "=", "yes")]
    )
    ca_tag_persona_id = fields.Many2one(
        'ca.tag_persona', string="Person Tag",
        compute="_compute_tag_persona", store=True, readonly=False,
        domain="[('ca_persona_id', '=', persona_id), "
               "('state', '=', 'to_give_back')]")
    allowed_date_start = fields.Datetime(
        related="ca_tag_persona_id.date_start", readonly=True)
    allowed_date_end = fields.Datetime(
        related="ca_tag_persona_id.date_end", readonly=True)
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(required=True)

    def _get_tag_lettore_attivo(self, tag_persona):
        """Abilitazione gia' presente per questo tag sul lettore del punto
        accesso. Una persona puo' avere piu' tag validi: il controllo va fatto
        sul tag, non sulla persona."""
        self.ensure_one()
        if not tag_persona or not self.punto_accesso_id.ca_lettore_id:
            return self.env['ca.tag_lettore']
        return self.env['ca.tag_lettore'].search([
            ('ca_lettore_id', '=', self.punto_accesso_id.ca_lettore_id.id),
            ('ca_tag_id', '=', tag_persona.ca_tag_id.id),
            ('state', 'not in', ['expired']),
            ('active', '=', True),
        ], limit=1)

    @api.depends('persona_id', 'punto_accesso_id')
    def _compute_tag_persona(self):
        for record in self:
            if not record.persona_id:
                record.ca_tag_persona_id = False
                continue
            tag_persona_ids = self.env['ca.tag_persona'].search([
                ('ca_persona_id', '=', record.persona_id.id),
                ('state', '=', 'to_give_back'),
            ])
            # propone il primo tag della persona non ancora abilitato
            record.ca_tag_persona_id = next(
                (tp for tp in tag_persona_ids
                 if not record._get_tag_lettore_attivo(tp)),
                tag_persona_ids[:1]
            )

    @api.onchange('ca_tag_persona_id', 'punto_accesso_id')
    def _onchange_tag_persona_id(self):
        for record in self:
            if record._get_tag_lettore_attivo(record.ca_tag_persona_id):
                return {'warning': {
                    'title': _('Warning'),
                    'message': _(
                        'Tag %s already allowed on this access point, '
                        'select another tag of the person'
                    ) % record.ca_tag_persona_id.ca_tag_id.name,
                }}

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_start > record.date_end:
                    raise UserError(
                        _('Date end must be after date start'))
                if not record.allowed_date_start or not record.allowed_date_end:
                    continue
                if (
                        record.date_end < record.allowed_date_start or
                        record.date_start > record.allowed_date_end or
                        record.date_end > record.allowed_date_end
                ):
                    raise UserError(
                        _('Date start and date end must be beetween a valid period'))

    def action_confirm(self):
        self.ensure_one()
        if not self.ca_tag_persona_id:
            raise UserError(_('Select a valid tag for the person'))
        if self._get_tag_lettore_attivo(self.ca_tag_persona_id):
            raise UserError(_(
                'Tag %s already allowed on this access point'
            ) % self.ca_tag_persona_id.ca_tag_id.name)
        tag_lettore = self.env['ca.tag_lettore'].create({
            'ca_lettore_id': self.punto_accesso_id.ca_lettore_id.id,
            'ca_tag_id': self.ca_tag_persona_id.ca_tag_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'ca_punto_accesso_id': self.punto_accesso_id.id
        })
        self.env['ca.lettore_persona'].elabora_persone_tag_lettore(
            tag_lettore)
        return {'type': 'ir.actions.act_window_close'}
