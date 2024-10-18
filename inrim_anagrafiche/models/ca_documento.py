from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

from odoo import models, fields, api, _


class CaTipoDocIdent(models.Model):
    _name = 'ca.tipo_doc_ident'
    _description = 'Tipo Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'date_start': self.date_start.strftime("%Y-%m-%d"),
            'date_end': self.date_end.strftime("%Y-%m-%d"),
        }


class CaStatoDocumento(models.Model):
    _name = 'ca.stato_documento'
    _description = 'Stato Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)

    def get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
        }


class CaImgDocumento(models.Model):
    _name = 'ca.img_documento'
    _description = 'Img Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    ca_tipo_documento_id = fields.Many2one('ca.tipo_doc_ident')
    side = fields.Selection([
        ('fronte', 'Fronte'),
        ('retro', 'Retro'),
        ('pagina', 'Pagina')
    ], required=True)
    image = fields.Binary(required=True, string="Immagine")
    filename = fields.Char()
    ca_documento_id = fields.Many2one('ca.documento')

    def rest_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'ca_tipo_documento_id': self.ca_tipo_documento_id.name,
            'side': dict(self._fields['side'].selection).get(image.side),
            'image': str(self.image),
            'filename': self.filename,
            'ca_documento_id': self.ca_documento_id.id
        }

    def rest_get(self, domain: list = None, offset=None, limit=None, order=None,
                 count=None):
        if not domain:
            domain = []
        ca_documento_ids = self.search(domain, limit="")


class CaDocumento(models.Model):
    _name = 'ca.documento'
    _description = 'Documenti'
    _rec_name = 'ca_persona_id'

    ca_persona_id = fields.Many2one('ca.persona')
    tipo_documento_id = fields.Many2one('ca.tipo_doc_ident', required=True)
    tipo_documento_name = fields.Char(related="tipo_documento_id.name")
    validity_start_date = fields.Date(required=True)
    validity_end_date = fields.Date(required=True)
    image_ids = fields.One2many('ca.img_documento', 'ca_documento_id', required=True)
    document_code = fields.Char(required=True)
    ca_stato_documento_id = fields.Many2one('ca.stato_documento', readonly=True)
    ca_stato_documento_name = fields.Char(related="ca_stato_documento_id.name")
    issued_by = fields.Char(required=True)

    @api.constrains('validity_start_date', 'validity_end_date')
    def _check_date(self):
        for record in self:
            if record.validity_end_date and record.validity_start_date:
                if record.validity_end_date <= record.validity_start_date:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def _cron_check_ca_stato_documento_id(self):
        today = fields.Date.today()
        two_months_later = today + relativedelta(months=2)
        for record in self.env['ca.documento'].search(
                [('validity_end_date', '!=', False)]):
            record.ca_stato_documento_id = False
            if record.validity_end_date:
                if record.validity_end_date > two_months_later:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_valido').id
                elif record.validity_end_date > today:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_in_scadenza').id
                else:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_scaduto').id

    @api.onchange('validity_end_date')
    def _onchange_validity_end_date(self):
        today = fields.Date.today()
        two_months_later = today + relativedelta(months=2)
        for record in self:
            record.ca_stato_documento_id = False
            if record.validity_end_date:
                if record.validity_end_date > two_months_later:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_valido').id
                elif record.validity_end_date > today:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_in_scadenza').id
                else:
                    record.ca_stato_documento_id = self.env.ref(
                        'inrim_anagrafiche.ca_stato_documento_scaduto').id

    def rest_record(self):
        images = []
        for image in self.image_ids:
            images.append(image.get_record())
        return {
            'id': self.id,
            'ca_persona_id': self.ca_persona_id.token,
            'tipo_documento_id': self.tipo_documento_id.name,
            'validity_start_date': self.validity_start_date.strftime("%Y-%m-%d"),
            'validity_end_date': self.validity_end_date.strftime("%Y-%m-%d"),
            'image_ids': images,
            'issued_by': self.issued_by,
            'document_code': self.document_code,
            'ca_stato_documento_id': self.ca_stato_documento_id.name
        }

    def rest_get(self, domain: list = None, limit=None):
        if not domain:
            domain = []
        ca_documento_ids = self.search(domain)
        res = []
        for documento in ca_documento_ids:
            res.append(documento.rest_record())
        return res

    def rest_post(self, body):
        {
            'ca_persona_token': 'dUqwMV0tTL',
            'tipo_documento_id': 'Carta D’identita',
            'validity_start_date': '2024-01-01',
            'validity_end_date': '2024-06-20',
            'issued_by': 'Comune',
            'document_code': 'Codice Doc Persona 1',
        }
