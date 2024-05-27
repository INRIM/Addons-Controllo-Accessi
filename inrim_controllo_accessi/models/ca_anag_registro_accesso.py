from odoo import models, fields, _
from odoo.exceptions import UserError

class CaAnagRegistroAccesso(models.Model):
    _name = 'ca.anag_registro_accesso'
    _description = 'Anagrafica Registro Accesso'
    _rec_name = 'ca_punto_accesso_id'

    ca_punto_accesso_id = fields.Many2one('ca.punto_accesso', string="Access", required=True)
    ca_tag_persona_id = fields.Many2one('ca.tag_persona', string="Tag", required=True)
    person_lastname = fields.Char(related="ca_tag_persona_id.ca_persona_id.lastname", string="Person Lastname")
    person_name = fields.Char(related="ca_tag_persona_id.ca_persona_id.name", string="Person Name")
    ca_ente_azienda_ids = fields.Many2many(related="ca_tag_persona_id.ca_persona_id.ca_ente_azienda_ids", string="Person Institution/Company")
    person_freshman = fields.Char(related="ca_tag_persona_id.ca_persona_id.freshman", string="Person Freshman")
    ca_lettore_id = fields.Many2one(related="ca_punto_accesso_id.ca_lettore_id", store=True)
    ca_spazio_id = fields.Many2one(related="ca_punto_accesso_id.ca_spazio_id", store=True, string="Space")
    ca_tipo_spazio_id = fields.Many2one(related="ca_punto_accesso_id.tipo_spazio_id", store=True, string="Space Type")
    ca_ente_azienda_id = fields.Many2one(related="ca_punto_accesso_id.ente_azienda_id", store=True, string="Space Office")
    datetime_event = fields.Datetime(default=fields.datetime.now())
    typology = fields.Char(related="ca_punto_accesso_id.ca_lettore_id.type", string="Configuration Type")
    direction = fields.Selection(related="ca_punto_accesso_id.ca_lettore_id.direction")
    access_allowed = fields.Boolean()
    system_error = fields.Boolean(related="ca_punto_accesso_id.ca_lettore_id.system_error")
    type = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Auto')
    ])
    active = fields.Boolean(default=True)

    def aggiungi_riga_accesso(
        self, ca_punto_accesso_id, 
        ca_tag_persona_id, datetime_event, type='manual'
    ):
        if (
            self.env.user.has_group('inrim_controllo_accessi_base.ca_ru') or
            self.env.user.has_group(
                'inrim_controllo_accessi_base.ca_portineria')
        ):
            if ca_punto_accesso_id.typology == 'stamping':
                if ca_punto_accesso_id.enable_sync:
                    return self.env['ca.anag_registro_accesso'].create({
                        'ca_punto_accesso_id': ca_punto_accesso_id.id,
                        'ca_tag_persona_id': ca_tag_persona_id.id,
                        'datetime_event': datetime_event,
                        'type': type
                    })
                else:
                    raise UserError(_('Errore punto accesso non attivo'))
            else:
                raise UserError(_(
                    'Errore punto accesso non ha tipologia timbratura'))
        else:
            raise UserError(_('Errore utente non abilitato'))