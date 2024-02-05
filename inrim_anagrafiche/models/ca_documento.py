from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class CaTipoDocIdent(models.Model):
    _name = 'ca.tipo_doc_ident'
    _description = 'Tipo Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

class CaCodiceDocumento(models.Model):
    _name = 'ca.codice_documento'
    _description = 'Codice Documento'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

class CaDocumento(models.Model):
    _name = 'ca.documento'
    _description = 'Documenti'

    ca_persona_id = fields.Many2one('ca.persona')
    tipo_documento_id = fields.Many2one('ca.tipo_doc_ident', required=True)
    validity_start_date = fields.Date(required=True)
    validity_end_date = fields.Date(required=True)
    image_ids = fields.Many2many('ir.attachment', required=True)
    document_code_id = fields.Many2one('ca.codice_documento', required=True)
    document_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring'),
        ('expired', 'Expired')
    ], readonly=True)

    def _cron_check_document_status(self):
        today = fields.Date.today()
        two_months_later = today + relativedelta(months = 2)
        for record in self.env['ca.documento'].search([('validity_end_date', '!=', False)]):
            record.document_status = False
            if record.validity_end_date > two_months_later:
                record.document_status = 'valid'
            elif record.validity_end_date > today:
                record.document_status = 'expiring'
            else:
                record.document_status = 'expired'
    
    @api.onchange('validity_end_date')
    def _onchange_validity_end_date(self):
        today = fields.Date.today()
        two_months_later = today + relativedelta(months = 2)
        for record in self:
                record.document_status = False
                if record.validity_end_date:
                    if record.validity_end_date > two_months_later:
                        record.document_status = 'valid'
                    elif record.validity_end_date > today:
                        record.document_status = 'expiring'
                    else:
                        record.document_status = 'expired'