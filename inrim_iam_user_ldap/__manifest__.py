# -*- coding: utf-8 -*-

{
    "name": "Inrim Iam User Ldap",
    "summary": "Iam Tools",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/INRIM",
    "author": "Alessio Gerace - Inrim",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allows to use LDAP over SSL authentication and set email entry",
    "depends": ["auth_ldap"],
    "data": [
        "views/res_company_ldap_views.xml",
        'data/ir.cron.xml',
    ],
    "external_dependencies": {"python": ["python-ldap"]},
}
