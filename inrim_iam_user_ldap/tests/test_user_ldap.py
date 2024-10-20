# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


class PatchLDAPConnection(object):
    def __init__(self, results):
        self.results = results

    def simple_bind_s(self, user, password):
        return True

    def search_st(self, base, scope, ldap_filter, attributes, timeout=None):
        if ldap_filter == "(uid=*)":
            return self.results
        else:
            return []

    def unbind(self):
        return True


@contextmanager
def patch_ldap(self, results):
    """defuse ldap functions to return fake entries instead of talking to a
    server. Use this in your own ldap related tests"""
    import ldap

    original_initialize = ldap.initialize

    def initialize(uri):
        return PatchLDAPConnection(results)

    ldap.initialize = initialize
    yield
    ldap.initialize = original_initialize


def get_fake_ldap(self):
    company = self.env.ref("base.main_company")
    company.write(
        {
            "ldaps": [
                (
                    0,
                    0,
                    {
                        "ldap_server": "fake",
                        "ldap_server_port": 389,
                        "ldap_binddn":"service",
                        "ldap_password":"test",
                        "ldap_filter": "(uid=%s)",
                        "ldap_base": "fake"
                    },
                )
            ],
        }
    )
    return company.ldaps.filtered(lambda x: x.ldap_server == "fake")

@tagged("post_install", "-at_install", "inrim")
class TestUsersLdapPopulate(TransactionCase):
    def test_users_ldap_populate(self):
        with patch_ldap(
            self,
            [
                (
                    "DN=fake",
                    {"cn": ["fake"], "uid": ["fake"], "mail": ["fake@fakery.com"]},
                )
            ],
        ):
            ldap = get_fake_ldap(self)
            conf = ldap._get_ldap_dicts(idres=ldap.id)
            results = ldap.get_ldap_users_dicts(conf)
            self.assertEqual(len(results), 1)
            res = ldap.action_populate()
            self.assertEqual(res, 1)
            self.assertTrue(self.env.ref("base.user_admin").active)
            self.assertTrue(self.env["res.users"].search([("login", "=", "fake")]))
            fake_user =self.env["res.users"].search([("login", "=", "fake")])[0]
            self.assertTrue(fake_user.active)

