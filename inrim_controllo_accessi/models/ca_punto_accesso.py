import logging
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CaPuntoAccessoCategory(models.Model):
    _name = 'ca.punto_accesso_category'
    _inherit = "ca.model.base.mixin"
    _description = 'Punto Accesso Category'
    _rec_names_search = ['name', 'code']

    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Char()
    ca_access_point_ids = fields.One2many(
        'ca.punto_accesso', 'ca_category',
        string="Access Point")
    ca_tag_persona_ids = fields.Many2many(
        'ca.tag_persona', compute="compute_ca_tag_persona_ids")
    allowed_users = fields.Many2many(
        'res.users',
        string="Allowed Users",
        store=True,
        groups="controllo_accessi.ca_config_tech"
    )
    active = fields.Boolean(default=True)

    def action_add_person(self):
        return {
            'name': _('Add Card Person'),
            'type': 'ir.actions.act_window',
            'res_model': 'ca.registra_persona',
            'view_id': self.env.ref(
                'inrim_controllo_accessi.ca_registra_persona_form').id,
            'target': 'new',
            'view_mode': "form",
            'context': {
                'default_record_id': self.id  # Passiamo l'ID del record corrente
            },

        }

    def action_restituisci_badge(self):
        return {
            'name': _('Give Back Badge'),
            'type': 'ir.actions.act_window',
            'res_model': 'ca.restituisci_badge',
            'view_id': self.env.ref(
                'inrim_controllo_accessi.ca_restituisci_badge_form').id,
            'target': 'new',
            'view_mode': "form",
            'context': {
                'default_record_id': self.id  # Passiamo l'ID del record corrente
            },

        }

    @api.depends('ca_access_point_ids')
    def compute_ca_tag_persona_ids(self):
        for record in self:
            access_point_ids = record.ca_access_point_ids
            tag_persona_ids = access_point_ids.mapped(
                'ca_tag_lettore_persona_ids.ca_tag_persona').ids

            record.ca_tag_persona_ids = [(6, 0, tag_persona_ids)]

    def write(self, vals):
        res = super().write(vals)
        if 'allowed_users' in vals:
            for record in self:
                if record.ca_access_point_ids:
                    record.ca_access_point_ids.write(
                        {'allowed_users': [(6, 0, record.allowed_users.ids)]})
        return res


class CaPuntoAccesso(models.Model):
    _name = 'ca.punto_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Punto Accesso'
    _rec_names_search = ['name']

    name = fields.Char(compute="_compute_name", store=True)
    ca_spazio_id = fields.Many2one('ca.spazio', required=True, string="Position",
                                   ondelete='cascade')
    tipo_spazio_id = fields.Many2one(related='ca_spazio_id.tipo_spazio_id',
                                     string="Position Type")
    ente_azienda_id = fields.Many2one(
        related='ca_spazio_id.ente_azienda_id',
        string="Headquarters Location"
    )
    ca_lettore_id = fields.Many2one('ca.lettore', required=True,
                                    string="Reader")
    ca_category = fields.Many2one('ca.punto_accesso_category', string="Cluster")
    system_error = fields.Boolean(related="ca_lettore_id.system_error", store=True,
                                  string="Reader Error")
    direction = fields.Selection(related="ca_lettore_id.direction")
    typology = fields.Selection([
        ('stamping', 'Stamping'),
        ('local_access', 'Local Access')
    ], required=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent")
    type_ids = fields.Many2many(
        'ca.tipo_persona', compute="_compute_type_ids")
    last_update_reader = fields.Datetime()
    last_reading_events = fields.Datetime()
    available_events = fields.Integer(
        related='ca_lettore_id.available_events', store=True, string="Available Events")
    events_to_read_num = fields.Integer(string="Number of Events To Read", default=5)
    events_read_num = fields.Integer(string="Number of Events Read")
    enable_sync = fields.Boolean(
        string="Enabled",
        help="Enable/Disable remote player synchronization"
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True, default=lambda self: self.default_date_end())
    ca_tag_lettore_ids = fields.One2many(
        'ca.tag_lettore', 'ca_punto_accesso_id', string="Reader Tag")
    ca_tag_lettore_persona_ids = fields.One2many(
        'ca.lettore_persona', 'ca_punto_accesso_id',
        string="Tag Reader Person")
    ca_tag_lettore_persona_view = fields.One2many(
        'ca.lettore_persona', 'ca_punto_accesso_id',
        domain=[("state", "in", ["active", "scheduled"])],
        string="Tag Reader Person View"
    )
    remote_update = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)
    recursive_read_events = fields.Boolean(string='Recursive Read Events', default=False)
    tz = fields.Selection(
        related='ente_azienda_id.tz', store=True, string="Timezone", readonly=True)
    allowed_users = fields.Many2many(
        'res.users', string="Allowed Users",
        groups="controllo_accessi.ca_config_tech"
    )

    ##TODO add cron to check and detach local_access  tags if expired
    def rest_get_record(self):
        vals = {
            "id": self.id,
            "name": self.name,
            "ca_lettore_id": self.ca_lettore_id.rest_get_record(),
            "ca_category": self.f_m2o(self.ca_category),
            "typology": self.f_selection("typology", self.typology),
            "direction": self.f_selection("direction", self.direction),
            "enable_sync": self.enable_sync,
            "remote_update": self.remote_update,
            "system_error": self.system_error
        }
        return vals

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('End date must be greater than start date'))

    def default_date_end(self):
        date_end = self.env['ir.config_parameter'].sudo().get_param('date_end.forever')
        date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S').date()
        return date_end

    def accessi_rifiutati_oggi(self):
        registro_accesso_ids = self.env['ca.anag_registro_accesso'].search([
            (
                'datetime_event', '>=',
                fields.datetime.now().strftime('%Y-%m-%d 00:00:00')),
            (
                'datetime_event', '<=',
                fields.datetime.now().strftime('%Y-%m-%d 23:59:59')),
            ('ca_lettore_id', '=', self.ca_lettore_id.id),
            ('access_allowed', '=', False)
        ], order="person_display_name, datetime_event asc")
        return {
            'name': _('Access Rejected Today'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.anag_registro_accesso',
            'domain': [('id', 'in', registro_accesso_ids.ids)],
        }

    def accessi_oggi(self):
        registro_accesso_ids = self.env['ca.anag_registro_accesso'].search([
            (
                'datetime_event', '>=',
                fields.datetime.now().strftime('%Y-%m-%d 00:00:00')),
            (
                'datetime_event', '<=',
                fields.datetime.now().strftime('%Y-%m-%d 23:59:59')),
            ('ca_lettore_id', '=', self.ca_lettore_id.id)
        ], order="person_display_name, datetime_event asc")
        return {
            'name': _('Accessed Today'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.anag_registro_accesso',
            'domain': [('id', 'in', registro_accesso_ids.ids)],
        }

    def elabora_persone_abilitate(self):
        for record in self:
            self.env[
                'ca.lettore_persona'
            ].elabora_persone(record.ca_lettore_id)
        return True

    def elabora_persone_abilitate_view(self):
        self.elabora_persone_abilitate()
        return {
            'name': _('Reader Person'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.lettore_persona',
            'domain': [
                ('date_start', '>=', fields.Datetime.now),
                ('date_end', '<=', fields.Datetime.now),
                ('ca_tag_lettore_id', 'in', self.ca_tag_lettore_ids.ids),
                ('state', '=', 'active')
            ],
        }

    def _compute_type_ids(self):
        for record in self:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id
            ])]

    @api.depends('ca_spazio_id', 'ca_lettore_id')
    def _compute_name(self):
        for record in self:
            record.name = '/'
            if record.ca_spazio_id and record.ca_lettore_id:
                record.name = record.ca_spazio_id.name + ' ' + record.ca_lettore_id.name

    @api.constrains('ca_lettore_id', 'active')
    def _check_ca_lettore_id(self):
        for record in self:
            punto_accesso_ids = self.search([
                ('ca_lettore_id', '=', record.ca_lettore_id.id),
                ('id', '!=', record.id)
            ])
            if punto_accesso_ids:
                raise UserError(_('Reader already in use in another location'))

    def commuta_abilitazione(self):
        for record in self:
            if record.enable_sync:
                record.enable_sync = False
            else:
                record.enable_sync = True
                self.check_and_attach()

    def local_access_detach(self, tag_persona):
        """
        Rimuovo Lettore-Persona
        Imposta Tag_persona --> restituito o scaduto
        rimuove link tag - lettore
        sync
        """
        logger.info("local_access_detach")
        lettore_persona = self.ca_tag_lettore_persona_ids.filtered(
            lambda x: x.ca_persona_id.id == tag_persona.ca_persona_id.id
        )
        if lettore_persona:
            lettore_persona.ca_tag_lettore_id.detach()
            logger.info(
                f"set  {lettore_persona.ca_tag_lettore_id} state {lettore_persona.ca_tag_lettore_id.state} ")
            logger.info(f"set {lettore_persona.ca_persona_id.name} set expired")
            lettore_persona.state = 'expired'
            lettore_persona.active = False
            self.env['ca.lettore_persona'].elabora_persone(self.ca_lettore_id)
            return True
        return True

    def local_access_attach(self, tag):
        """
        Deve esistere un record Tag/Persona
        Aggiungo Tag - Lettore
        Aggiungo Tag-Persona --> Da restituire
        Aggiungo Lettore-Persona
        :return:
        """
        self.ensure_one()
        tag_persona_id = self.env['ca.tag_persona'].get_current_by_tag(tag)
        if tag_persona_id:
            tag_lettore = self.env['ca.tag_lettore'].search(
                [
                    ('ca_tag_id', '=', tag.id),
                    ('ca_lettore_id', "=", self.ca_lettore_id.id)
                ], limit=1)
            if not tag_lettore:
                self.env['ca.tag_lettore'].create({
                    'ca_lettore_id': self.ca_lettore_id.id,
                    'ca_tag_id': tag.id,
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'ca_punto_accesso_id': self.id
                })
            self.env['ca.lettore_persona'].elabora_persone(self.ca_lettore_id)
            return True
        return False

    def local_access_attach_person(self, pesona):
        """
        Deve esistere un record Tag/Persona
        Aggiungo Tag - Lettore
        Aggiungo Tag-Persona --> Da restituire
        Aggiungo Lettore-Persona
        :return:
        """
        self.ensure_one()
        tag_persona_id = self.env['ca.tag_persona'].get_current_by_tag(pesona)
        if tag_persona_id:
            tag = tag_persona_id.ca_tag_id
            tag_lettore = self.env['ca.tag_lettore'].search(
                [
                    ('ca_tag_id', '=', tag.id),
                    ('ca_lettore_id', "=", self.ca_lettore_id.id)
                ], limit=1)
            if not tag_lettore:
                self.env['ca.tag_lettore'].create({
                    'ca_lettore_id': self.ca_lettore_id.id,
                    'ca_tag_id': tag.id,
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'ca_punto_accesso_id': self.id
                })
            self.env['ca.lettore_persona'].elabora_persone(self.ca_lettore_id)
            return True
        return False

    def stamping_detach(self, tag_persona):
        """
        Impost Tag_persona --> restituito o scaduto
        Rimuovo Lettore-Persona

        :return:
        """
        lettore_persona = self.ca_tag_lettore_persona_ids.filtered(
            lambda
                x: x.ca_persona_id.id == tag_persona.ca_persona_id.id and x.ca_tag_persona.id == tag_persona.id
        )
        logger.info(f"check tag is temp and remove from reader")
        if not tag_persona.ca_tag_id.temp:
            # imposta tag revocato
            logger.info(f"set {lettore_persona.ca_persona_id.display_name} expired")
            lettore_persona.ca_tag_lettore_id.detach()
        lettore_persona.state = 'expired'
        lettore_persona.active = False

    def stamping_attach(self):
        """
        Caso di punto accesso timbratura generale
        - estraggo tutti i tag validi
        - se il tag non e' collegato ad un lettore lo collego ( questo attiva il flag di sync)
        - aggiorno l'elenco delle persone collegate al lettore e quindi al punto accesso
        :return:
        """
        logger.info("Stamping Attach")
        self.ensure_one()
        tags = self.env['ca.tag'].search([
            ("ca_proprieta_tag_ids.name", "ilike", "valido")
        ])
        for tag in tags:
            tag_persona = self.env['ca.tag_persona'].get_current_by_tag(
                tag)
            if tag_persona:
                self.stamping_attach_tag_persona(tag_persona)

    def stamping_attach_tag_persona(self, tag_persona):
        """
        Caso di punto accesso timbratura generale
        - estraggo tutti i tag validi
        - se il tag non e' collegato ad un lettore lo collego ( questo attiva il flag di sync)
        - aggiorno l'elenco delle persone collegate al lettore e quindi al punto accesso
        :return:
        """
        logger.info("Stamping Attach Tag Persona ")
        self.ensure_one()
        tag = tag_persona.ca_tag_id
        tag_lettore = self.env['ca.tag_lettore'].search(
            [
                ('ca_tag_id', '=', tag.id),
                ('ca_lettore_id', "=", self.ca_lettore_id.id),
                ('state', 'not in', ['expired']),
                ('active', '=', True)
            ], limit=1)
        if not tag_lettore:
            tag_lettore = self.env['ca.tag_lettore'].create({
                'ca_lettore_id': self.ca_lettore_id.id,
                'ca_tag_id': tag.id,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'ca_punto_accesso_id': self.id
            })

        res = self.env['ca.lettore_persona'].elabora_persone_tag_lettore(tag_lettore)

    def check_and_attach_tag_persona(self, tag_persona):
        for record in self:
            if record.typology == 'stamping':
                record.stamping_attach_tag_persona(tag_persona)

    def check_and_attach(self):
        for record in self:
            if record.typology == 'stamping':
                record.stamping_attach()

    def add_persona_tag(self, body: dict):
        try:
            tag_persona = self.env['ca.tag_persona'].create({
                'ca_persona_id': body.get('ca_persona_id.id'),
                'ca_tag_id': body.get('ca_tag_id.id'),
                'date_start': body.get('date_start'),
                'date_end': body.get('date_end')
            })
            for record in self.search(["active", "=", True]):
                if record.typology == 'stamping':
                    record.stamping_attach_tag_persona(tag_persona)
            return {
                'success': True, "data": tag_persona,
                "message": ""
            }
        except Exception as e:
            logger.error(f"{str(e)} Error {e}", exc_info=True)
            return {'success': False, "data": {}, 'message': str(e)}

    def check_and_detach(self, tag_persona):
        if self.typology == 'stamping':
            self.stamping_detach(tag_persona)
        elif self.typology == 'local_access':
            self.local_access_detach(tag_persona)

    def sposta_punto_accesso(self, ca_spazio_id):
        self.active = False
        vals = {
            'ca_spazio_id': ca_spazio_id.id,
            'ca_lettore_id': self.ca_lettore_id.id,
            'typology': self.typology,
            'ca_persona_id': self.ca_persona_id.id if self.ca_persona_id else False,
            'last_update_reader': self.last_update_reader,
            'last_reading_events': self.last_reading_events,
            'events_to_read_num': self.events_to_read_num,
            'events_read_num': self.events_read_num,
            'enable_sync': self.enable_sync,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'ca_tag_lettore_ids': self.ca_tag_lettore_ids
        }
        new_ca_punto_accesso_id = self.env['ca.punto_accesso'].create(vals)
        return new_ca_punto_accesso_id

    def persone_abilitate(self):
        return {
            'name': _('Qualified People'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.lettore_persona',
            'domain': [
                ('date_start', '>=', fields.Datetime.now),
                ('date_end', '<=', fields.Datetime.now)
            ],
        }

    def check_readers(self):
        return True

    def load_readers_data(self):
        return True

    def eval_readers_data(self):
        return True

    def update_readers_data(self):
        return True

    def update_clock(self):
        return True

    def action_abilita_persona_locale(self):
        return {
            'name': _('Add person in local'),
            'type': 'ir.actions.act_window',
            'res_model': 'ca.abilita_persona_locale',
            'view_id': self.env.ref(
                'inrim_controllo_accessi.ca_abilita_persona_locale_form').id,
            'target': 'new',
            'view_mode': "form",
            'context': {
                'default_punto_accesso_id': self.id
            },

        }
