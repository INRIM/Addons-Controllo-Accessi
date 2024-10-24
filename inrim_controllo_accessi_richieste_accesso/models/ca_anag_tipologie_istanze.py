from odoo import models, fields, api

class CaAnagTipologieIstanze(models.Model):
    _name = 'ca.anag_tipologie_istanze'
    _inherit = "ca.model.base.mixin"
    _description = 'Anagrafica Tipologie Istanze'

    name = fields.Char(required=True)

    def rest_boby_hint(self):
        return {
            "name": ""
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name'
            ])
        return body, msg