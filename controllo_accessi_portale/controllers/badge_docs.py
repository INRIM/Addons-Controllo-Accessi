from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound
from .common import check_access_permission


class PortalBadgeDocs(http.Controller):

    @http.route('/badge_release_docs/<int:persona_id>', auth='user', type='http', website=True)
    def badge_release_docs_form(self, persona_id, **post):
        user = request.env.user
        if not check_access_permission(user):
            raise NotFound()

        persona_obj = request.env['ca.persona'].browse(persona_id)
        if not persona_obj.exists():
            raise NotFound()

        if post and request.httprequest.method == 'POST':
            return self._handle_docs_post(persona_obj, post)

        return request.render('controllo_accessi_portale.badge_release_docs_view', {
            "persona_id": persona_obj.id, "errors": {}, "error_message": "", "values": {}
        })

    @http.route('/get/badge_release_docs/tipo_documento', auth='user', type='jsonrpc', website=True, csrf=False)
    def badge_release_tipo_documento(self, **kwargs):
        if not check_access_permission(request.env.user): raise Forbidden()
        return request.env['ca.tipo_doc_ident'].search([]).read()

    def _handle_docs_post(self, persona_obj, post):
        req_fields = ["tipo_documento_id", "validity_start_date", "validity_end_date", "document_code", "issued_by"]
        errors = {f: 'missing' for f in req_fields if not post.get(f)}
        
        values = {f: post.get(f) for f in req_fields}
        values['persona_id'] = persona_obj.id
        if values.get('tipo_documento_id'): values['tipo_documento_id'] = int(values['tipo_documento_id'])

        if errors:
            return request.render('controllo_accessi_portale.badge_release_docs_view', {
                "persona_id": persona_obj.id, "errors": errors, "error_message": _('Some required fields are empty.'), "values": values
            })

        request.env['ca.registra_doc_persona'].create(values).action_confirm()
        return request.redirect('/anagrafiche')