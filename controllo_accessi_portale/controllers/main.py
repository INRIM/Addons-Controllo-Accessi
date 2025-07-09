from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request


class CustomHome(Home):

    def _get_redirect_url(self, user):
        """ Metodo unico per determinare la pagina di destinazione in base al gruppo dell'utente. """
        if user.has_group('base.group_system'):  # Se è admin
            return "/web"
        elif user.has_group(
                'controllo_accessi_portale.inrim_access_portal'):  # Se appartiene al gruppo portale
            return "/anagrafiche"
        return "/web"  # Default: home page standard

    def _login_redirect(self, uid, redirect=None):
        """ Override del reindirizzamento post-login """
        user = request.env['res.users'].sudo().browse(uid)
        return self._get_redirect_url(user)  # ✅ Ora restituisce solo un URL (stringa)

    @http.route('/web/login', type='http', auth="public", website=True)
    def web_login(self, redirect=None, **kw):
        """ Override di `web_login` per personalizzare il reindirizzamento """
        response = super().web_login(redirect, **kw)
        if request.params.get('login_success'):
            user = request.env.user
            return request.redirect(
                self._get_redirect_url(user))  # ✅ Ora reindirizza correttamente
        return response

    @http.route('/', type='http', auth="user", website=True)
    def home_redirect(self, **kwargs):
        """ Override della home `/` per gestire utenti con sessione attiva. """
        return request.redirect(self._get_redirect_url(request.env.user))
