{
    'name': 'Inrim Controllo Accessi',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': ['inrim_anagrafiche'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_config_parameter_data.xml',
        'data/ca_punto_accesso_data.xml',
        'data/ca_tag_lettore_data.xml',
        'wizard/ca_sposta_punto_accesso_views.xml',
        'wizard/ca_aggiungi_movimento_accesso_views.xml',
        'views/ca_tag_lettore_views.xml',
        'views/ca_punto_accesso_persona_views.xml',
        'views/ca_punto_accesso_views.xml',
        'views/ca_anag_registro_accesso_views.xml',
        'views/ca_log_integrazione_lettori_views.xml',
        'views/ca_richiesta_riga_accesso_sede_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
