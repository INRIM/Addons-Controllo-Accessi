import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CompanyLDAP(models.Model):
    _inherit = "res.company.ldap"


    user = fields.Many2one(
        'res.users', string='Template User',
        default=lambda self: self.env.ref('base.default_user').id,
        help="User to copy when creating new users"
    )
