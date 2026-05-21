{
    'name': 'Controllo Accessi Base',
    'version': '18.0.1.0.0',
    'description': "Controllo Accessi Base",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'mail',
        'base_location_geonames_import',
        'base_geolocalize'
    ],
    'data': [
        'security/security.xml',
    ],
    'demo': [],
    'pre_init_hook': '_init_italy',
    'installable': True,
    'application': False,
}
