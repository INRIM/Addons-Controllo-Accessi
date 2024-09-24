{
    'name': 'Inrim Controllo Accessi Custom',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi Custom",
    'depends': [
        'mail',
        'inrim_anagrafiche',
        'base_geolocalize',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/ente_azienda_views.xml',
        'views/ca_persona_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/ca_ente_azienza_demo.xml',
    ],
    'installable': True,
    'application': True,
}