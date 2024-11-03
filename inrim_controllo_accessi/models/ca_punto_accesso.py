from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaPuntoAccesso(models.Model):
    _name = 'ca.punto_accesso'
    _inherit = "ca.model.base.mixin"
    _description = 'Punto Accesso'

    name = fields.Char(compute="_compute_name", store=True)
    ca_spazio_id = fields.Many2one('ca.spazio', required=True, string="Position",
                                   ondelete='cascade')
    tipo_spazio_id = fields.Many2one(related='ca_spazio_id.tipo_spazio_id',
                                     string="Position Type")
    ente_azienda_id = fields.Many2one(
        related='ca_spazio_id.ente_azienda_id',
        string="Headquarters Location"
    )
    ca_lettore_id = fields.Many2one('ca.lettore', required=True)
    system_error = fields.Boolean(related="ca_lettore_id.system_error", store=True,
                                  string="Reader Error")
    direction = fields.Selection(related="ca_lettore_id.direction")
    typology = fields.Selection([
        ('stamping', 'Stamping'),
        ('local_access', 'Local Access')
    ], required=True)
    ca_persona_id = fields.Many2one('ca.persona', string="Referent")
    type_ids = fields.Many2many('ca.tipo_persona', compute="_compute_type_ids")
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
        'ca.tag_lettore', 'ca_punto_accesso_id')
    ca_tag_lettore_persona_ids = fields.One2many(
        'ca.lettore_persona', 'ca_lettore_id')
    remote_update = fields.Boolean(readonly=True)
    active = fields.Boolean(default=True)
    recursive_read_events = fields.Boolean(string='Recursive Read Events', default=False)
    tz = fields.Selection(
        related='ente_azienda_id.tz', store=True, string="Timezone", readonly=True)

    # TODO: typology = stamping carica sul lettore tutti i TAG e lavora solo TAG <-> Persona
    #      ( se persona ospite o tag jlly) se tag viene restituito il Tag.in_suo = False
    # TODO: typology = local_access associa un tag al lettore e lo disassocia e aggiorna il flag enable_sync
    # TODO: Aggiungere la categoria per raggruppare i Punti Accesso

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

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
            'name': _('Accessi Rifiutati Oggi'),
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
            'name': _('Accessi Oggi'),
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
            ].elabora_persone_lettore(record.ca_lettore_id.name)

    def elabora_persone_abilitate_view(self):
        self.elabora_persone_abilitate()
        return {
            'name': _('Lettore Persona'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.lettore_persona',
            'domain': [
                ('date', '=', fields.date.today()),
                ('ca_tag_lettore_id', 'in', self.ca_tag_lettore_ids.ids),
                ('state', '=', 'active')

            ],
        }

    def _compute_type_ids(self):
        for record in self:
            record.type_ids = [(6, 0, [
                self.env.ref('inrim_anagrafiche.tipo_persona_interno').id,
                self.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id
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
                self.stamping_attach()

    def local_access_detach(self, persona):
        """
        Rimuovo Lettore-Persona
        Impost Tag_persona --> restituito o scaduto
        rimuove link tag - lettore
        sync
        """
        persona.set_tag_returned()
        lettore_persona = self.ca_tag_lettore_persona_ids.filtered(
            lambda x: x.ca_persona_id.id == persona.id
        )
        lettore_persona.ca_tag_lettore_id.unlink()
        lettore_persona.unlink()

    def local_access_attach(self, tag):
        """
        Aggiungo Tag - Lettore
        Aggiungo Tag-Persona --> Da restituire
        Aggiungo Lettore-Persona
        :return:
        """
        self.ensure_one()
        tag_lettore = self.env['ca.tag_lettore'].search(
            [('ca_tag_id', '=', tag)], limit=1)
        if not tag_lettore:
            self.env['ca.tag_lettore'].create({
                'ca_lettore_id': self.lettore_id.id,
                'ca_tag_id': tag.id,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'punto_accesso_id': self.id
            })
        self.env['ca.lettore_persona'].elabora_persone(self.ca_lettore_id)

    def stamping_detach(self, persona):
        """
        Impost Tag_persona --> restituito o scaduto
        Rimuovo Lettore-Persona

        :return:
        """
        tag = persona.get_current_tag()
        lettore_persona = self.ca_tag_lettore_persona_ids.filtered(
            lambda x: x.ca_persona_id.id == persona.id
        )
        lettore_persona.expired = True
        lettore_persona.active = False

    def stamping_attach(self):
        """
        Caso di punto accesso timbratura generale
        - estraggo tutti i tag validi
        - se il tag non e' collegato ad un lettore lo collego ( questo attiva il flag di sync)
        - aggiorno l'elenco delle persone collegate al lettore e quindi al punto accesso
        :return:
        """
        self.ensure_one()
        tags = self.env['ca.tag'].search([
            ('name', 'in', [self.env.ref('inrim_anagrafiche.proprieta_tag_valido')])
        ])
        for tag in tags:
            tag_lettore = self.env['ca.tag_lettore'].search(
                [('ca_tag_id', '=', tag.id)], limit=1)
            if not tag_lettore:
                self.env['ca.tag_lettore'].create({
                    'ca_lettore_id': self.lettore_id.id,
                    'ca_tag_id': tag.id,
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'punto_accesso_id': self.id
                })
        self.env['ca.lettore_persona'].elabora_persone(self.ca_lettore_id)

    def check_and_attach(self):
        if self.typology == 'stamping':
            self.stamping_attach_tags_readers()
        elif self.typology == 'local_access':
            self.local_access_attach()

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
            'domain': [('date', '=', fields.date.today())],
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
