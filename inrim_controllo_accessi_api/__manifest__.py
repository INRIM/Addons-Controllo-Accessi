{
    'name': 'Inrim Controllo Accessi API',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi API",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'base_geolocalize',
        'auth_api_key_server_env',
        'inrim_anagrafiche',
        'inrim_controllo_accessi'
    ],
    'data': [
        'data/ir_cron.xml',
        'views/ca_persona_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
