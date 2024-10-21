from odoo import models, fields, api

class CaAnagTipologieIstanze(models.Model):
    _name = 'ca.anag_tipologie_istanze'
    _description = 'Anagrafica Tipologie Istanze'

    name = fields.Char(required=True)