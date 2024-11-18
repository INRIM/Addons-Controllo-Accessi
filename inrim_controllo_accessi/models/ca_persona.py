import random
import string

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CaPersona(models.Model):
    _inherit = 'ca.persona'

    person_access_ids = fields.One2many('ca.anag_registro_accesso', 'ca_persona_id')