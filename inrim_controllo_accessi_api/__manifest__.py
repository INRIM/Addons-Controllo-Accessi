{
    'name': 'Inrim Controllo Accessi API',
    'version': '19.0.1.0.0',
    'description': "Inrim Controllo Accessi API",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'auth_api_key',
        'inrim_controllo_accessi'
    ],
    'data': [
        'views/ca_persona_views.xml',
        'views/res_users_views.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'installable': True,
    'application': True,
}
