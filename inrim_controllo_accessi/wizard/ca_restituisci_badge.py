import logging

from odoo import models, fields, api

logger = logging.getLogger(__name__)


class CaRestituisciBadge(models.TransientModel):
    _name = 'ca.restituisci_badge'
    _description = 'Restituisci Badge'

    ca_tag_id = fields.Many2one('ca.tag', required=True)
    temp = fields.Boolean()
    tag_ids = fields.Many2many('ca.tag', compute="_compute_tag_ids")
    persona_id = fields.Many2one("ca.persona")

    @api.depends('temp')
    def _compute_tag_ids(self):
        tag_model = self.env['ca.tag']
        for record in self:
            ids = []
            domain = [('in_use', '=', True)]
            if record.temp:
                domain.append(('temp', '=', record.temp))
            ids.append(
                tag_model.search(domain).ids
            )
            record.tag_ids = [(6, 0, ids)]

    @api.onchange('ca_tag_id')
    def _onchange_tag_id(self):
        for record in self:
            tag_persona = self.env['ca.tag_persona'].get_current_by_tag(record.ca_tag_id)
            self.persona_id = tag_persona.ca_persona_id

    def action_confirm(self):
        tag_persona = self.env['ca.tag_persona'].get_current_by_tag(self.ca_tag_id)
        logger.info(f"wizard eval detach {tag_persona}")
        for access_point_group in self.env['ca.punto_accesso_category'].search([]):
            for access_point in access_point_group.ca_access_point_ids:
                access_point.check_and_detach(tag_persona)
        tag_persona.set_retuned()
        return True
