{
    'name': 'Controllo Accessi Portale',
    'version': '17.0.1.0.0',
    'description': "Controllo Accessi Portale",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'inrim_anagrafiche',
        'inrim_controllo_accessi',
        'web',
        'website',
    ],
    'data': [
        'security/security.xml',
        'views/partner_portals_views.xml',
        'views/badge_return_views.xml',
        'views/badge_release_views.xml',
    ],
     'assets': {
        'web.assets_frontend': [
            'controllo_accessi_portale/static/src/**/*',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
}