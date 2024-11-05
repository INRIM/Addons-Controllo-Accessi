from odoo import models


class CaTag(models.Model):
    _inherit = 'ca.tag'

    def compute_properties(self):
        super().compute_properties()
        record.revoked = False
        record.temp = False
        if self.ca_proprieta_tag_ids:
            if self.env.ref(
                    'inrim_anagrafiche.proprieta_tag_valido') in record.ca_proprieta_tag_ids:
                ...
