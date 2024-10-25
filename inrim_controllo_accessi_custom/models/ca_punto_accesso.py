from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaPuntoAccesso(models.Model):
    _inherit = "ca.punto_accesso"

    codice_lettore_grum = fields.Integer(
        string='Codice Lettore GRUM',
    )

    @api.constrains('codice_lettore_grum', 'typology')
    def _check_codice_lettore_grum(self):
        for record in self:
            if record.typology == 'stamping' and not record.codice_lettore_grum:
                raise UserError("Il codice lettore GRUM è obbligatorio se la tipologia è: Timbratura.")
            if record.codice_lettore_grum:
                if not (20 <= record.codice_lettore_grum <= 999):
                    raise UserError("Il codice lettore GRUM deve essere compreso tra 20 e 999.")