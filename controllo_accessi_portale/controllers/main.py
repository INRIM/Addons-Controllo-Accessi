from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home


class CustomHome(Home):
    @http.route()
    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)

        # Riferimento ai gruppi
        group_portal = request.env.ref('controllo_accessi_portale.inrim_access_portal')
        group_admin = request.env.ref('base.group_system')

        # Se l'utente è amministratore, lo inviamo al backend
        if group_admin in user.groups_id:
            return super()._login_redirect(uid, redirect)

        # Se l'utente è nel gruppo "inrim_access_portal", lo inviamo alla pagina del portale
        if group_portal in user.groups_id:
            return "/anagrafiche"

        # Default: comportamento standard
        return super()._login_redirect(uid, redirect)