from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaPuntoAccesso(models.Model):
    _inherit = "ca.punto_accesso"

    codice_lettore_grum = fields.Integer(
        string='GRUM Reader Code',
    )

    def rest_get_record(self):
        vals = super().rest_get_record()
        vals["codice_lettore_grum"] = self.codice_lettore_grum
        return vals

    @api.constrains('codice_lettore_grum', 'typology')
    def _check_codice_lettore_grum(self):
        for record in self:
            # if record.typology == 'stamping' and not record.codice_lettore_grum:
            #     raise UserError("Il codice lettore GRUM è obbligatorio se la tipologia è: Timbratura.")
            if record.codice_lettore_grum:
                if not (20 <= record.codice_lettore_grum <= 999):
                    raise UserError(_("The GRUM reader code must be between 20 and 999."))