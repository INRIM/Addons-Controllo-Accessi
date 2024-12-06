import logging

from odoo import models, fields, api

logger = logging.getLogger(__name__)


class CaRestituisciBadge(models.TransientModel):
    _name = 'ca.restituisci_badge'
    _description = 'Restituisci Badge'

    ca_tag_id = fields.Many2one('ca.tag_persona', required=True)
    temp = fields.Boolean(default=True)
    tag_ids = fields.Many2many('ca.tag_persona', compute="_compute_tag_ids")
    persona_id = fields.Many2one("ca.persona")

    @api.depends('temp')
    def _compute_tag_ids(self):
        tag_model = self.env['ca.tag_persona']
        for record in self:
            ids = []
            domain = [('state', '=', "to_give_back"), ('ca_tag_id.in_use', '=', True )]
            if record.temp:
                domain.append(('ca_tag_id.temp', '=', record.temp))
            ids = tag_model.search(domain).ids

            record.tag_ids = [(6, 0, ids)]

    @api.onchange('ca_tag_id')
    def _onchange_tag_id(self):
        for record in self:
            tag_persona = record.ca_tag_id
            self.persona_id = tag_persona.ca_persona_id

    def action_confirm(self):
        tag_persona = self.ca_tag_id
        logger.info(f"wizard eval detach {tag_persona}")
        for access_point in self.env['ca.punto_accesso'].search([]):
            access_point.check_and_detach(tag_persona)
        tag_persona.set_retuned()
        return True
