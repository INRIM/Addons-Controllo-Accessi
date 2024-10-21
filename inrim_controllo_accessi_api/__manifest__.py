{
    'name': 'Inrim Controllo Accessi API',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi API",
    'depends': [
        'inrim_anagrafiche',
        'inrim_controllo_accessi',
        'auth_api_key_server_env',
    ],
    'data': [
        'data/ir_cron.xml',
        'views/res_users_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}