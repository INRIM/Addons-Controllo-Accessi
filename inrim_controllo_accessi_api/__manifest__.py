{
    'name': 'Inrim Controllo Accessi API',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi API",
    'depends': [
        'inrim_anagrafiche',
        'inrim_controllo_accessi',
    ],
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/ca_richiesta_riga_accesso_sede_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}