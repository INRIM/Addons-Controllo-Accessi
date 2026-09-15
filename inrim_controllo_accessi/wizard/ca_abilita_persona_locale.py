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
        'ca.tag_persona', compute="_compute_tag_persona")
    allowed_date_start = fields.Datetime(
        related="ca_tag_persona_id.date_start", readonly=True)
    allowed_date_end = fields.Datetime(
        related="ca_tag_persona_id.date_end", readonly=True)
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(required=True)

    @api.depends('persona_id')
    def _compute_tag_persona(self):
        for record in self:
            record.ca_tag_persona_id = self.env['ca.tag_persona'].get_current_by_pesona(
                record.persona_id
            ) if record.persona_id else False

    @api.onchange('persona_id')
    def _onchange_persona_id(self):
        for record in self:
            if not record.persona_id or not record.ca_tag_persona_id:
                continue
            lettore_persona = self.env['ca.tag_lettore'].search([
                ('ca_lettore_id', "=", record.punto_accesso_id.ca_lettore_id.id),
                ('ca_tag_id', '=', record.ca_tag_persona_id.ca_tag_id.id)
            ], limit=1)
            if lettore_persona:
                raise UserError(
                    _('Person alredy allowed to access'))

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
