import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CompanyLDAP(models.Model):
    _inherit = "res.company.ldap"


    user = fields.Many2one(
        'res.users', string='Template User',
        help="User to copy when creating new users"
    )
