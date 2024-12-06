import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class CaRegistraDocPersona(models.TransientModel):
    _name = 'ca.registra_doc_persona'
    _description = 'Registra Doc Persona'

    persona_id = fields.Many2one("ca.persona", readonly=True)
    tipo_documento_id = fields.Many2one('ca.tipo_doc_ident')
    validity_start_date = fields.Date()
    validity_end_date = fields.Date()
    document_code = fields.Char()
    issued_by = fields.Char()

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def action_confirm(self):
        res = self.env['ca.documento'].create({
            'ca_persona_id': self.persona_id.id,
            'tipo_documento_id': self.tipo_documento_id.id,
            'validity_start_date': self.validity_start_date,
            'validity_end_date': self.validity_end_date,
            'document_code': self.document_code,
            'issued_by': self.issued_by
        })
        return {'type': 'ir.actions.act_window_close'}
