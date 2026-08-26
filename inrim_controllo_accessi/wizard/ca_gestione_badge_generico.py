import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CaGestioneBadgeGenerico(models.TransientModel):
    _name = 'ca.gestione_badge_generico'
    _description = 'Manage Generic Badge'

    mode = fields.Selection([
        ('add', 'Add Generic Badge'),
        ('revoke', 'Revoke Generic Badge')
    ], default='add', required=True)

    # add
    tipo_badge_id = fields.Many2one(
        'ca.tipo_badge_generico', string="Generic Badge Type")
    name = fields.Char(string="Badge Name")
    tag_code = fields.Char(string="Tag Code")
    default_id_number = fields.Char(string="ID Number")

    # revoke
    ca_tag_id = fields.Many2one('ca.tag', string="Badge")
    revocable_tag_ids = fields.Many2many(
        'ca.tag', compute="_compute_revocable_tag_ids")
    ca_persona_id = fields.Many2one(
        'ca.persona', string="Currently Assigned To", readonly=True)

    punto_accesso_ids = fields.Many2many(
        'ca.punto_accesso', string="Stamping Access Points",
        compute="_compute_punto_accesso_ids")

    @api.depends('mode')
    def _compute_punto_accesso_ids(self):
        access_points = self.env['ca.punto_accesso'].sudo().search([
            ('typology', '=', 'stamping')
        ])
        for record in self:
            record.punto_accesso_ids = [(6, 0, access_points.ids)]

    @api.depends('mode', 'tipo_badge_id')
    def _compute_revocable_tag_ids(self):
        tipo_model = self.env['ca.tipo_badge_generico']
        for record in self:
            if record.tipo_badge_id:
                proprieta_ids = record.tipo_badge_id.ca_proprieta_tag_id.ids
            else:
                proprieta_ids = tipo_model.get_proprieta_tag_ids()
            ids = self.env['ca.tag'].search([
                ('revoked', '=', False),
                ('ca_proprieta_tag_ids', 'in', proprieta_ids)
            ]).ids
            record.revocable_tag_ids = [(6, 0, ids)]

    @api.onchange('mode')
    def _onchange_mode(self):
        for record in self:
            record.ca_tag_id = False
            record.ca_persona_id = False

    @api.onchange('ca_tag_id')
    def _onchange_ca_tag_id(self):
        for record in self:
            record.ca_persona_id = False
            if not record.ca_tag_id:
                continue
            tag_persona = self.env['ca.tag_persona'].get_current_by_tag(
                record.ca_tag_id)
            if tag_persona:
                record.ca_persona_id = tag_persona.ca_persona_id

    @api.onchange('tipo_badge_id')
    def _onchange_tipo_badge_id(self):
        """Propone il nome del prossimo badge del tipo, resta modificabile."""
        for record in self:
            if record.mode != 'add' or not record.tipo_badge_id:
                continue
            names = record.tipo_badge_id.get_next_badge_names(1)
            if names:
                record.name = names[0]

    @api.onchange('tag_code')
    def _onchange_tag_code(self):
        for record in self:
            if record.tag_code:
                record.tag_code = record.tag_code.strip().upper()

    def action_add(self):
        """Crea il badge generico e lo scrive su tutti i lettori di sede."""
        self.ensure_one()
        if not self.tipo_badge_id:
            raise UserError(_('Generic badge type is required'))
        if not self.name or not self.tag_code:
            raise UserError(_('Badge name and tag code are required'))
        self.tipo_badge_id.create_badges([{
            'name': self.name,
            'tag_code': self.tag_code,
            'default_id_number': self.default_id_number,
        }])
        return {'type': 'ir.actions.act_window_close'}

    def action_revoke(self):
        """Revoca il badge generico e lo rimuove da tutti i lettori."""
        self.ensure_one()
        if not self.ca_tag_id:
            raise UserError(_('Badge is required'))
        tag = self.ca_tag_id.sudo()
        access_points = self.env['ca.punto_accesso'].sudo().search([])
        tag_persona = self.env['ca.tag_persona'].sudo().get_current_by_tag(tag)
        if tag_persona:
            logger.info(f"Generic badge {tag.name} give back {tag_persona}")
            for access_point in access_points:
                access_point.check_and_detach(tag_persona)
            tag_persona.set_retuned()
        for access_point in access_points.filtered(
                lambda x: x.typology == 'stamping'):
            access_point.generic_tag_detach(tag)
        # revoca il tag per ultimo: ca.tag_persona vieta la scrittura
        # su un tag gia' revocato
        tag.write({
            'in_use': False,
            'ca_proprieta_tag_ids': [
                (3, self.env.ref('inrim_anagrafiche.proprieta_tag_valido').id),
                (4, self.env.ref('inrim_anagrafiche.proprieta_tag_revocato').id),
            ],
        })
        logger.info(f"Generic badge {tag.name} revoked")
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm(self):
        self.ensure_one()
        if self.mode == 'add':
            return self.action_add()
        return self.action_revoke()
