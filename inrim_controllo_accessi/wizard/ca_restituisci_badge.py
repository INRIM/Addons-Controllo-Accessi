import logging

from odoo import models, fields

logger = logging.getLogger(__name__)


class CaRestituisciBadge(models.TransientModel):
    _name = 'ca.restituisci_badge'
    _description = 'Restituisci Badge'

    ca_tag_id = fields.Many2one('ca.tag', required=True)

    def action_confirm(self):
        tag_persona = self.env['ca.tag_persona'].get_current_by_tag(self.ca_tag_id)
        logger.info(f"wizard eval detach {tag_persona}")
        for access_point_group in self.env['ca.punto_accesso_category'].search([]):
            for access_point in access_point_group.ca_access_point_ids:
                access_point.check_and_detach(tag_persona)
        tag_persona.set_retuned()
        return res
