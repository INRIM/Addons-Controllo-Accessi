import logging
import re

from odoo import SUPERUSER_ID, _, fields, models
from odoo.tools.pycompat import to_text

_logger = logging.getLogger(__name__)

try:
    import ldap
    from ldap.filter import filter_format
except ImportError:
    _logger.warning("Cannot import ldap.")


class CompanyLDAP(models.Model):
    _inherit = "res.company.ldap"
    _description = "Company LDAP configuration"

    is_ssl = fields.Boolean(string="Use LDAPS", default=True)
    email_entry = fields.Char(string="Ldap Email Entry", default="mail")
    skip_cert_validation = fields.Boolean(
        string="Skip certificate validation", default=True
    )

    def _map_ldap_attributes(self, conf, login, ldap_entry):
        """
        Compose values for a new resource of model res_users,
        based upon the retrieved ldap entry and the LDAP settings.
        :param dict conf: LDAP configuration
        :param login: the new user's login
        :param tuple ldap_entry: single LDAP result (dn, attrs)
        :return: parameters for a new resource of model res_users
        :rtype: dict
        """
        res = super(CompanyLDAP, self)._map_ldap_attributes(
            conf, login, ldap_entry)
        if conf["email_entry"] and conf["email_entry"] in ldap_entry[1]:
            res['email'] = to_text(ldap_entry[1][conf["email_entry"]][0])
        return res

    def _get_ldap_dicts(self, idres=0):
        res = super()._get_ldap_dicts()
        res_for_id = {}
        for rec in res:
            ldap = self.sudo().browse(rec["id"])
            rec["is_ssl"] = ldap.is_ssl or False
            rec["skip_cert_validation"] = ldap.skip_cert_validation or False
            rec["email_entry"] = ldap.email_entry or ""
            if 0 < idres == rec["id"]:
                res_for_id = rec.copy()
        if res_for_id:
            return res_for_id
        else:
            return res

    def _connect(self, conf):
        _logger.debug(f"_connect")
        """
        Connect to an LDAP server specified by an ldap
        configuration dictionary.

        :param dict conf: LDAP configuration
        :return: an LDAP object
        """
        if conf.get('is_ssl'):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
            uri = 'ldaps://%s:%d' % (
                conf['ldap_server'], conf['ldap_server_port'])

            connection = ldap.initialize(uri)
            return connection
        else:
            return super(CompanyLDAP, self)._connect(conf)

    def get_ldap_users_dicts(self, conf, user_name="*"):
        """
        Execute ldap query as defined in conf

        Don't call self.query because it supresses possible exceptions
        """
        ldap_filter = (
            filter_format(conf["ldap_filter"], (user_name,))
            if user_name != "*"
            else conf["ldap_filter"] % user_name
        )
        conn = self._connect(conf)
        conn.simple_bind_s(conf["ldap_binddn"] or "",
                           conf["ldap_password"] or "")
        results = conn.search_st(
            conf["ldap_base"], ldap.SCOPE_SUBTREE, ldap_filter, None,
            timeout=60
        )
        conn.unbind()
        return results


    def action_populate(self):
        """
        Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        _logger.debug("action_populate called on res.company.ldap ids %s",
                      self.ids)
        users_model = self.env["res.users"]
        users_count_before = users_model.search_count([])
        conf = self._get_ldap_dicts(idres=self.id)
        results = self.get_ldap_users_dicts(conf)
        for result in results:
            attribute_match = re.search(
                r"([a-zA-Z_]+)=\%s", conf["ldap_filter"])
            if attribute_match:
                login_attr = attribute_match.group(1)
            else:
                raise UserError(
                    _(
                        "No login attribute found: "
                        "Could not extract login attribute from filter %s"
                    )
                    % conf["ldap_filter"]
                )
            login = result[1][login_attr][0].lower().strip()
            user_id = self.with_context(
                no_reset_password=True
            )._get_or_create_user(conf, login, result)

        users_created = users_model.search_count([]) - users_count_before

        deactivated_users_count = 0

        _logger.debug("%d users created", users_created)
        return users_created

    def sync_users(self):
        ldaps = self.env['res.company.ldap'].search([])
        for ldap in ldaps:
            ldap.action_populate()
