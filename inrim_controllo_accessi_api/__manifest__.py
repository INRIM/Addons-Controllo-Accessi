{
    'name': 'Inrim Controllo Accessi API',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi API",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'auth_api_key_server_env',
        'inrim_controllo_accessi'
    ],
    'data': [
        'views/ca_persona_views.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'installable': True,
    'application': True,
}
