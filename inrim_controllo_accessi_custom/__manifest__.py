{
    'name': 'Inrim Controllo Accessi Custom',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi Custom",
    'depends': [
        'mail',
        'inrim_anagrafiche',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/ente_azienda_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}