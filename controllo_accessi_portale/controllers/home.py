from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request


class CustomHome(Home):

    def _get_redirect_url(self, user):
        """ Metodo unico per determinare la pagina di destinazione """
        if user.has_group('base.group_system'):
            return "/web"
        elif user.has_group('controllo_accessi_portale.inrim_access_portal'):
            return "/anagrafiche"
        return "/web"

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        return self._get_redirect_url(user)

    @http.route('/web/login', type='http', auth="public", website=True)
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect, **kw)
        if request.params.get('login_success'):
            user = request.env.user
            return request.redirect(self._get_redirect_url(user))
        return response

    @http.route('/', type='http', auth="user", website=True)
    def home_redirect(self, **kwargs):
        return request.redirect(self._get_redirect_url(request.env.user))