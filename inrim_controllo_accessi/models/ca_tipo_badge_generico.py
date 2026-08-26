import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

# Nome badge generico: 'Visiting - 12'
BADGE_NAME_RE = re.compile(r'^(?P<prefix>.+?)\s+-\s+(?P<num>\d+)$')
# I codici scritti sui lettori sono 16 caratteri esadecimali
TAG_CODE_RE = re.compile(r'^[0-9A-F]{16}$')


class CaTipoBadgeGenerico(models.Model):
    _name = 'ca.tipo_badge_generico'
    _inherit = "ca.model.base.mixin"
    _description = 'Tipo Badge Generico'
    _order = 'sequence, name'
    _rec_names_search = ['name', 'ca_proprieta_tag_id']

    name = fields.Char(required=True)
    badge_prefix = fields.Char(
        string="Badge Name Prefix",
        help="Prefix used to propose the name of a new badge of this type, "
             "the name is built as '<prefix> - <progressive>'. "
             "Empty means the type name is used")
    sequence = fields.Integer(default=10)
    description = fields.Char()
    ca_proprieta_tag_id = fields.Many2one(
        'ca.proprieta_tag', required=True, string="Tag Property",
        help="Property written on the tag to mark it as this generic badge type")
    ca_proprieta_tag_default_ids = fields.Many2many(
        'ca.proprieta_tag', 'ca_tipo_badge_generico_proprieta_default_rel',
        'tipo_badge_generico_id', 'proprieta_tag_id',
        string="Default Tag Properties",
        help="Properties added to every tag created with this type "
             "(Valido is always added)")
    person_type = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal'),
        ('both', 'Both')
    ], default='external', required=True,
        help="People allowed to get a badge of this type")
    same_day_default = fields.Boolean(
        string="Same Day Assignment", default=True,
        help="When assigning this badge to a person the wizard proposes "
             "an assignment ending the same day at 19:30. Disable it for "
             "long stay badges, the dates are then left to the operator")
    active = fields.Boolean(default=True)

    @api.constrains('ca_proprieta_tag_id', 'active')
    def _check_unique_proprieta(self):
        for record in self:
            tipo_id = self.search([
                ('id', '!=', record.id),
                ('ca_proprieta_tag_id', '=', record.ca_proprieta_tag_id.id)
            ])
            if tipo_id:
                raise UserError(
                    _('A generic badge type already exists with this tag property'))

    @api.model
    def normalize_tag_code(self, code):
        """Codice badge ripulito: senza spazi e maiuscolo."""
        return (code or '').strip().upper()

    @api.model
    def is_valid_tag_code(self, code):
        """Un codice valido e' di 16 caratteri esadecimali.

        Intercetta i codici rovinati da Excel (notazione scientifica,
        zeri iniziali persi) prima che finiscano sui lettori fisici.
        """
        return bool(TAG_CODE_RE.match(self.normalize_tag_code(code)))

    def get_badge_prefix(self):
        """Prefisso usato per comporre il nome dei badge del tipo."""
        self.ensure_one()
        return (self.badge_prefix or self.name or '').strip()

    def get_next_badge_names(self, count=1):
        """Nomi progressivi proposti per i prossimi `count` badge del tipo.

        La numerazione tiene conto anche dei badge revocati o disattivati:
        un nome gia' usato non viene riproposto, altrimenti nei log accessi
        lo stesso nome indicherebbe badge fisici diversi.
        """
        self.ensure_one()
        prefix = self.get_badge_prefix()
        if not prefix:
            return []
        tags = self.env['ca.tag'].with_context(active_test=False).search([
            ('name', 'like', prefix)
        ])
        last = 0
        for tag in tags:
            match = BADGE_NAME_RE.match((tag.name or '').strip())
            if match and match.group('prefix') == prefix:
                last = max(last, int(match.group('num')))
        return [f"{prefix} - {num}"
                for num in range(last + 1, last + 1 + count)]

    def _get_stamping_access_points(self):
        access_points = self.env['ca.punto_accesso'].sudo().search([
            ('typology', '=', 'stamping')
        ])
        if not access_points:
            raise UserError(_('No stamping access point configured'))
        return access_points

    def create_badges(self, badge_vals):
        """Crea i badge generici del tipo e li scrive sui lettori di sede.

        badge_vals: lista di dict con le chiavi name, tag_code e
        opzionalmente default_id_number.
        """
        self.ensure_one()
        access_points = self._get_stamping_access_points()
        badge_vals = [dict(
            vals, tag_code=self.normalize_tag_code(vals.get('tag_code')))
            for vals in badge_vals]
        invalid_codes = [vals['tag_code'] for vals in badge_vals
                         if not self.is_valid_tag_code(vals['tag_code'])]
        if invalid_codes:
            raise UserError(
                _('These badge codes are not 16 hexadecimal characters: %s')
                % ', '.join(invalid_codes))
        # ca.tag non ha un vincolo sul nome: due badge con lo stesso nome
        # renderebbero ambigui i log accessi
        existing = self.env['ca.tag'].with_context(active_test=False).search([
            ('name', 'in', [vals['name'] for vals in badge_vals])
        ])
        if existing:
            raise UserError(
                _('These badge names already exist: %s') % ', '.join(
                    existing.mapped('name')))
        proprieta_ids = self.get_tag_proprieta_ids()
        tags = self.env['ca.tag'].sudo().create([{
            'name': vals['name'],
            'tag_code': vals['tag_code'],
            'default_id_number': vals.get('default_id_number'),
            'ca_proprieta_tag_ids': [(6, 0, proprieta_ids)],
        } for vals in badge_vals])
        for access_point in access_points:
            for tag in tags:
                access_point.generic_tag_attach(tag)
        logger.info(
            f"{len(tags)} generic badges {self.name} added on "
            f"{len(access_points)} stamping access points")
        return tags

    def get_tag_proprieta_ids(self):
        """Tag properties to set on a new generic badge of this type."""
        self.ensure_one()
        proprieta = (
            self.ca_proprieta_tag_default_ids |
            self.ca_proprieta_tag_id |
            self.env.ref('inrim_anagrafiche.proprieta_tag_valido')
        )
        return proprieta.ids

    @api.model
    def get_tipo_by_tag(self, tag):
        """Generic badge type of `tag`, empty recordset if not generic."""
        if not tag or not tag.ca_proprieta_tag_ids:
            return self.browse()
        return self.search([
            ('ca_proprieta_tag_id', 'in', tag.ca_proprieta_tag_ids.ids)
        ], limit=1)

    @api.model
    def get_proprieta_tag_ids(self, person_type=None):
        """Tag properties identifying a generic badge, optionally restricted
        to the ones usable by `person_type` ('internal' / 'external')."""
        domain = []
        if person_type:
            domain = [('person_type', 'in', ['both', person_type])]
        return self.search(domain).mapped('ca_proprieta_tag_id').ids

    def rest_boby_hint(self):
        return {
            "name": "Visiting",
            "ca_proprieta_tag_id": 1
        }

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'badge_prefix': self.badge_prefix,
            'ca_proprieta_tag_id': self.f_m2o(self.ca_proprieta_tag_id),
            'ca_proprieta_tag_default_ids': self.f_m2m(
                self.ca_proprieta_tag_default_ids),
            'person_type': self.f_selection("person_type", self.person_type),
            'same_day_default': self.same_day_default,
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'ca_proprieta_tag_id.id'
            ])
        return body, msg
