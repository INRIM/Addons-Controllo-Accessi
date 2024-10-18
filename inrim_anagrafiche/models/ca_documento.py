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
            'date_start': self.date_start.strftime("%Y-%m-%d"),
            'date_end': self.date_end.strftime("%Y-%m-%d"),
        }


class CaStatoDocumento(models.Model):
    _name = 'ca.stato_documento'
    _inherit = "ca.model.base.mixin"
    _description = 'Stato Documento'

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
        }


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

    def rest_get_record(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or "",
            'ca_tipo_documento_id': self.ca_tipo_documento_id.name,
            'side': dict(self._fields['side'].selection).get(self.side),
            'image': str(self.image),
            'filename': self.filename,
            'ca_documento_id': self.ca_documento_id.id
        }


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
            'ca_persona_id': self.ca_persona_id.token,
            'tipo_documento_id': self.tipo_documento_id.name,
            'validity_start_date': self.validity_start_date.strftime("%Y-%m-%d"),
            'validity_end_date': self.validity_end_date.strftime("%Y-%m-%d"),
            'image_ids': images,
            'issued_by': self.issued_by,
            'document_code': self.document_code,
            'ca_stato_documento_id': self.ca_stato_documento_id.name
        }

    def rest_eval_body(self, body):
        ca_persona_token = body.get('ca_persona_token', "")
        ca_persona = self.env['ca.persona'].get_by_key(
            'token', body.get('ca_persona_token'))
        tipo_documento = self.env['ca.tipo_doc_ident'].get_by_id(
            body.get('tipo_documento_id'))

        if not ca_persona:
            return False, f"La persona con token '{ca_persona_token}' non esiste"
        if not tipo_documento:
            return False, f"Tipo documento '{tipo_documento_id}' non valido"
        validity_start_date = body.get('validity_start_date')
        validity_end_date = body.get('validity_end_date')
        issued_by = body.get('issued_by')
        document_code = body.get('document_code')
        if not validity_start_date:
            return False, "Campo obbligatorio mancante 'validity_start_date'"
        if not validity_end_date:
            return False, "Campo obbligatorio mancante 'validity_end_date'"
        if not issued_by:
            return False, "Campo obbligatorio mancante 'issued_by'"
        if not document_code:
            return False, "Campo obbligatorio mancante 'document_code'"
        return {
            'ca_persona_id': ca_persona.id,
            'tipo_documento_id': tipo_documento.id,
            'validity_start_date': validity_start_date,
            'validity_end_date': validity_end_date,
            'issued_by': issued_by,
            'document_code': document_code
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
