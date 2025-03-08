from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

class CustomHome(Home):

    def _get_redirect_url(self, user):
        """ Metodo unico per determinare la pagina di destinazione in base al gruppo dell'utente. """
        if user.has_group('base.group_system'):  # Se è admin
            return "/web"
        elif user.has_group('controllo_accessi_portale.inrim_access_portal'):  # Se appartiene al gruppo portale
            return "/anagrafiche"
        return "/"  # Default: home page standard

    @http.route()
    def _login_redirect(self, uid, redirect=None):
        """ Override del reindirizzamento post-login. """
        user = request.env['res.users'].sudo().browse(uid)
        return self._get_redirect_url(user)

    @http.route('/', type='http', auth="user", website=True)
    def home_redirect(self, **kwargs):
        """ Override della home `/` per gestire utenti con sessione attiva. """
        return request.redirect(self._get_redirect_url(request.env.user))

