from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CaRighePersona(models.Model):
    _name = 'ca.righe_persona'
    _inherit = "ca.model.base.mixin"
    _description = 'Righe Persona'

    spazio_id = fields.Many2one('ca.spazio')
    tag_persona_id = fields.Many2one('ca.tag_persona')
    date_start = fields.Date(string='Valid Access From')
    date_end = fields.Date(string='Valid Access To')
    suspended = fields.Boolean()

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))