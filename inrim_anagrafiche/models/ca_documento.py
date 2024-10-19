from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaTipoDocIdent(models.Model):
    _name = 'ca.tipo_doc_ident'
    _inherit = "ca.model.base.mixin"
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

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'date_start': self.f_date(self.date_start),
            'date_end': self.f_date(self.date_end)
        }

    def rest_boby_hint(self):
        return {
            'name': "name",
            'description': "description",
            'date_start': '2024-01-01',
            'date_end': '2024-01-02'
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'date_start', 'date_end'
            ])
        if not res:
            return res, msg


class CaStatoDocumento(models.Model):
    _name = 'ca.stato_documento'
    _inherit = "ca.model.base.mixin"
    _description = 'Stato Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)

    def rest_boby_hint(self):
        return {
            'name': 'name',
            'description': 'description'
        }

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name'
            ])
        return body, msg


class CaImgDocumento(models.Model):
    _name = 'ca.img_documento'
    _inherit = "ca.model.base.mixin"
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

    def rest_boby_hint(self):
        return {
            'ca_persona_id': 'ca_persona_id',
            'tipo_documento_id': 'tipo_documento_id',
            'side': "'fronte', 'retro','pagina' ",
            'validity_start_date': '2024-01-01',
            'validity_end_date': '2024-06-20',
            'issued_by': 'Comune',
            'document_code': 'Codice Doc Persona 1',
            "ca_documento_id": "ca_documento_id"
        }

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'ca_tipo_documento_id': self.f_o2m(self.ca_tipo_documento_id),
            'side': self.f_selection("side", self.side),
            'image': self.f_img(self.image),
            'filename': self.filename,
            'ca_documento_id': self.f_o2m(self.ca_documento_id, 'tipo_documento_name')
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'ca_tipo_documento_id', 'side',
                'image', 'filename', 'ca_documento_id'
            ])
        return body, msg


class CaDocumento(models.Model):
    _name = 'ca.documento'
    _description = 'Documenti'
    _inherit = "ca.model.base.mixin"
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

    def rest_get_record(self):
        images = []
        for image in self.image_ids:
            images.append(image.rest_get_record())
        return {
            'id': self.id,
            'ca_persona_id': self.f_o2m(self.ca_persona_id, "display_name"),
            'tipo_documento_id': self.f_o2m(self.tipo_documento_id),
            'validity_start_date': self.f_date(self.validity_start_date),
            'validity_end_date': self.f_date(self.validity_end_date),
            'image_ids': images,
            'issued_by': self.issued_by,
            'document_code': self.document_code,
            'ca_stato_documento_id': self.ca_stato_documento_id.name
        }

    def rest_boby_hint(self):
        return {
            'ca_persona_id': 'ca_persona_id',
            'tipo_documento_id': 'tipo_documento_id',
            'validity_start_date': '2024-01-01',
            'validity_end_date': '2024-06-20',
            'issued_by': 'Carta D’identita',
            'document_code': 'Doc num',
            'ca_stato_documento_id': "ca_stato_documento_id"
        }

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'ca_persona_id', 'tipo_documento_id',
                'validity_start_date', 'validity_end_date',
                'issued_by', 'document_code'
            ])
        if not body:
            return body, msg

        ca_persona = self.env['ca.persona'].get_by_id(
            body.get('ca_persona_id'))
        tipo_documento = self.env['ca.tipo_doc_ident'].get_by_id(
            body.get('tipo_documento_id'))

        if not ca_persona:
            return False, f"La persona con token '{check_required}' non esiste"
        if not tipo_documento:
            return False, f"Tipo documento '{tipo_documento_id}' non valido"
        return {
            'ca_persona_id': ca_persona.id,
            'tipo_documento_id': tipo_documento.id,
            'validity_start_date': body.get('validity_start_date'),
            'validity_end_date': body.get('validity_end_date'),
            'issued_by': body.get('issued_by'),
            'document_code': body.get('document_code')
        }, ""

    def rest_post(self, body: dict):
        doc, msg = super().rest_post(body)
        if doc:
            doc._onchange_validity_end_date()
        return doc, msg

    def rest_put(self, body: dict):
        doc, msg = super().rest_put(body)
        if doc:
            doc._onchange_validity_end_date()
        return doc, msg
