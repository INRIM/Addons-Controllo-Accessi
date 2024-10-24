from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CaLettore(models.Model):
    _inherit = 'ca.lettore'

    punto_accesso_ids = fields.One2many(
        'ca.tag_lettore', 'ca_lettore_id', readonly=True)

    @api.constrains('punto_accesso_ids')
    def _check_sale_lines(self):
        for record in self:
            if len(record.punto_accesso_ids) > 1:
                raise ValidationError(_('No more than 1 access point'))

    def rest_get_record(self):
        vals = super().rest_get_record()
        vals["punto_accesso_ids"] = self.f_o2m(self.punto_accesso_ids)
        return vals
