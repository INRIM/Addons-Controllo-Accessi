from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound
from .common import check_access_permission


class PortalBadgeReturn(http.Controller):

    def _get_badge_return_tags(self, env, temp_only=False):
        jolly_property = env.ref('inrim_anagrafiche.proprieta_tag_jolly')
        records = env['ca.tag_persona'].search([
            ('state', '=', "to_give_back"),
            ('ca_tag_id.in_use', '=', True),
        ])

        ret = []
        for record in records:
            is_jolly = jolly_property in record.ca_tag_id.ca_proprieta_tag_ids
            if temp_only and not (record.temp or is_jolly):
                continue

            data = record.read(['ca_persona_id', 'ca_tag_id', 'temp', 'display_name'])[0]
            data['tag_code'] = record.ca_tag_id.tag_code
            data['is_jolly'] = is_jolly
            ret.append(data)
        return ret

    @http.route('/badge_return', type='http', auth='user', website=True)
    def portal_badge_return(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise NotFound()
        return request.render('controllo_accessi_portale.badge_return_view', {})

    @http.route('/badge_return/submit', auth='user', type='http', website=True, methods=['POST'], csrf=False)
    def badge_return_submit(self, **kwargs):
        tag_persona_id = int(kwargs['tag_id'])
        tag_persona = request.env['ca.tag_persona'].browse(tag_persona_id)
        if not tag_persona.exists():
             return request.redirect('/badge_return')

        vals = {'ca_tag_id': tag_persona.id}
        wiz = request.env['ca.restituisci_badge'].create(vals)
        wiz.action_confirm()
        return request.redirect('/badge_return')

    @http.route('/get/badge_return/tags', auth='user', type='json', website=True)
    def badge_return_tags(self, **kwargs):
        user = request.env.user
        if not check_access_permission(user):
            raise Forbidden()
        return self._get_badge_return_tags(request.env)
