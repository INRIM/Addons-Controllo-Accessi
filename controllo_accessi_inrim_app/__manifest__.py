{
    'name': 'App Controllo Accessi INRIM',
    'version': '17.0.1.0.0',
    'description': "App Controllo Accessi INRIM",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'inrim_iam_user_ldap',
        'inrim_controllo_accessi_rfidglobal'
    ],
    'data': [
        'data/res_company_data.xml',
        'data/ente_azienda_inrim_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/ir_cron.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
