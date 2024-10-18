{
    'name': 'Inrim Controllo Accessi Custom',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi Custom",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'mail',
        'controllo_accessi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_config_parameter_data.xml',
        'views/ente_azienda_views.xml',
        'views/ca_richiesta_riga_accesso_sede_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/ca_ente_azienza_demo.xml',
    ],
    'installable': True,
    'application': True,
}