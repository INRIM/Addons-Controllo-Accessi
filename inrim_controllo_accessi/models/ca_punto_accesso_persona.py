from odoo import models, fields

class CaPuntoAccessoPersona(models.Model):
    _name = 'ca.punto_accesso_persona'
    _description = 'Punto Accesso Persona'

    ca_lettore_id = fields.Many2one(related="ca_tag_lettore_id.ca_lettore_id", required=True)
    ca_tag_lettore_id = fields.Many2one('ca.tag_lettore', required=True, readonly=True)
    ca_tag_persona = fields.Many2one('ca.tag_persona', required=True, readonly=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ], readonly=True)
    date = fields.Date(default=fields.date.today(), readonly=True)
    active = fields.Boolean(default=True)