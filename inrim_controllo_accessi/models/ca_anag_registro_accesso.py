from odoo import models, fields, api

class CaAnagRegistroAccesso(models.Model):
    _name = 'ca.anag_registro_accesso'
    _description = 'Anagrafica Registro Accesso'
    _rec_name = 'ca_punto_accesso_id'

    ca_punto_accesso_id = fields.Many2one('ca.punto_accesso')
    # tag_id = fields.Many2one(related="ca_tag_persona.ca_tag_id")
    # person_lastname = fields.Char(related="ca_tag_persona.ca_persona_id.lastname")
    # person_name = fields.Char(related="ca_tag_persona.ca_persona_id.name")
    # ca_ente_azienda_ids = fields.Many2many(related="ca_tag_persona.ca_persona_id.ca_ente_azienda_ids")
    # person_freshman = fields.Char(related="ca_tag_persona.ca_persona_id.freshman")
    ca_lettore_id = fields.Many2one(related="ca_punto_accesso_id.ca_lettore_id", store=True)
    ca_spazio_id = fields.Many2one(related="ca_punto_accesso_id.ca_spazio_id", store=True)
    ca_tipo_spazio_id = fields.Many2one(related="ca_punto_accesso_id.tipo_spazio_id", store=True)
    ca_ente_azienda_id = fields.Many2one(related="ca_punto_accesso_id.ente_azienda_id", store=True)
    datetime_event = fields.Datetime(default=fields.datetime.now())
    typology = fields.Char(related="ca_punto_accesso_id.ca_lettore_id.type", string="Configuration Type")
    direction = fields.Selection(related="ca_punto_accesso_id.ca_lettore_id.direction")
    access_allowed = fields.Boolean()
    system_error = fields.Boolean(related="ca_punto_accesso_id.ca_lettore_id.system_error")