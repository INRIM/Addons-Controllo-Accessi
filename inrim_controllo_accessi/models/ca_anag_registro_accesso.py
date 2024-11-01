import pytz
from odoo import models, fields

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones,
                                  key=lambda tz: tz if not tz.startswith(
                                      'Etc/') else '_')]


def _tz_get(self):
    return _tzs


class CaAnagRegistroAccesso(models.Model):
    _name = 'ca.anag_registro_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Anagrafica Registro Accesso'
    _rec_name = 'ca_punto_accesso_id'

    ca_punto_accesso_id = fields.Many2one(
        'ca.punto_accesso', string="Access", required=True, ondelete='cascade')
    ca_tag_persona_id = fields.Many2one(
        'ca.tag_persona', string="Tag", required=True, ondelete='cascade')
    person_display_name = fields.Char(
        related="ca_tag_persona_id.ca_persona_id.display_name", string="Person Name")
    ca_ente_azienda_ids = fields.Many2many(
        related="ca_tag_persona_id.ca_persona_id.ca_ente_azienda_ids",
        string="Person Institution/Company")
    person_freshman = fields.Char(
        related="ca_tag_persona_id.ca_persona_id.freshman", string="Person Freshman")
    ca_lettore_id = fields.Many2one(
        related="ca_punto_accesso_id.ca_lettore_id", store=True)
    ca_spazio_id = fields.Many2one(
        related="ca_punto_accesso_id.ca_spazio_id", store=True, string="Space")
    ca_tipo_spazio_id = fields.Many2one(
        related="ca_punto_accesso_id.tipo_spazio_id", store=True, string="Space Type")
    ca_ente_azienda_id = fields.Many2one(
        related="ca_punto_accesso_id.ente_azienda_id", store=True, string="Space Office")
    datetime_event = fields.Datetime(default=fields.datetime.now(), required=True)
    typology = fields.Selection(
        related="ca_punto_accesso_id.typology", string="Ap Type")
    direction = fields.Selection(
        related="ca_punto_accesso_id.ca_lettore_id.direction")
    access_allowed = fields.Boolean()
    system_error = fields.Boolean(
        related="ca_punto_accesso_id.ca_lettore_id.system_error")
    type = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Auto')
    ], string="Insertion Type")
    tz = fields.Selection(
        _tz_get, string='Timezone',
        default=lambda self: self._context.get('tz'),
        help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
             "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
             "Anywhere else, time values are computed according to the time offset of your web client."
    )
    active = fields.Boolean(default=True)

    def aggiungi_riga_accesso(
            self, ca_punto_accesso_id,
            ca_tag_persona_id, datetime_event, type='manual', access_allowed=True,
            tz=""
    ):
        if not tz:
            tz = self._context.get('tz')
        vals = {
            'ca_punto_accesso_id': ca_punto_accesso_id.id,
            'ca_tag_persona_id': ca_tag_persona_id.id,
            'datetime_event': datetime_event,
            'type': type,
            'access_allowed': access_allowed,
            'tz': tz
        }
        return self.create(vals)
