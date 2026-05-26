{
    'name': 'Inrim Controllo Accessi Richieste Accesso Inrim',
    'version': '19.0.1.0.0',
    'description': "Inrim Controllo Accessi Richieste Accesso Inrim",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'controllo_accessi_inrim_app'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ca_categoria_richiesta_data.xml',
        'data/ca_categoria_tipo_richiesta_data.xml',
        'data/ca_anag_avanzamento_rich_data.xml',
        'data/ca_anag_tipologie_istanze_data.xml',
        'views/ca_categoria_richiesta_views.xml',
        'views/ca_categoria_tipo_richiesta_views.xml',
        'views/ca_settore_ente_views.xml',
        'views/ca_anag_servizi_views.xml',
        'views/ca_anag_tipologie_istanze_views.xml',
        'views/ca_anag_avanzamento_rich_views.xml',
        'views/ca_richiesta_servizi_persona_views.xml',
        'views/ca_richiesta_accesso_persona_views.xml',
        'views/ca_richiesta_accesso_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/ca_anag_servizi_demo.xml',
        'demo/ca_settore_ente_demo.xml',
    ],
    'installable': True,
    'application': False
}
