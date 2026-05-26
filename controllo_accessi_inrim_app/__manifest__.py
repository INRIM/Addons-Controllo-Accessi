{
    'name': 'App Controllo Accessi INRIM',
    'version': '19.0.1.0.0',
    'description': "App Controllo Accessi INRIM",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'inrim_iam_user_ldap',
        'inrim_controllo_accessi_rfidglobal'
    ],
    'data': [
        'data/res_users.xml',
        'data/res_company_data.xml',
        'data/ente_azienda_inrim_data.xml',
        'data/ca_punto_accesso_category_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/ir_cron.xml',
        'views/users_ldap.xml',
        'views/ca_punto_accesso_views.xml',
        'views/ca_registro_accesso_views.xml',
        'views/webclient_templates.xml',
    ],
    'demo': [
        "demo/ca_punto_accesso_data.xml",
    ],
    'installable': True,
    'application': True,
}
