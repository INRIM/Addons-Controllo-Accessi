{
    'name': 'Inrim Controllo Accessi RfidGlobal',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi RfidGlobal",
    'depends': [
        'inrim_controllo_accessi_custom',
        'inrim_controllo_accessi_api',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/ca_tag_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}