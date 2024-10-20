{
    'name': 'Inrim Controllo Accessi RfidGlobal',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi RfidGlobal",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'inrim_controllo_accessi_api',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/ente_azienda_views.xml',
        'views/ca_tag_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
