{
    'name': 'Controllo Accessi Base',
    'version': '17.0.1.0.0',
    'description': "Controllo Accessi Base",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': ['base_location_geonames_import'],
    'data': [
        'security/security.xml',
    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
