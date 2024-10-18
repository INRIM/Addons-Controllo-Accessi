{
    'name': 'Inrim Anagrafiche',
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'version': '17.0.1.0.0',
    'description': "Inrim Anagrafiche",
    'depends': ['controllo_accessi'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ca_tipo_persona_data.xml',
        'data/ca_tipo_doc_ident_data.xml',
        'data/ca_tipo_ente_azienda_data.xml',
        'data/ca_proprieta_tag_data.xml',
        'data/ca_stato_documento_data.xml',
        'data/ca_stato_anag_data.xml',
        'data/ca_categoria_richiesta_data.xml',
        'data/ca_categoria_tipo_richiesta_data.xml',
        'data/ir.cron.xml',
        'views/ca_persona_views.xml',
        'views/ca_tipo_persona_views.xml',
        'views/ca_documento_views.xml',
        'views/ca_ente_azienda_views.xml',
        'views/ca_tipo_ente_azienda_views.xml',
        'views/ca_lettore_views.xml',
        'views/ca_tag_views.xml',
        'views/ca_tag_persona_views.xml',
        'views/ca_spazio_views.xml',
        'views/ca_codice_locale_views.xml',
        'views/ca_stato_anag_views.xml',
        'views/ca_categoria_richiesta_views.xml',
        'views/ca_categoria_tipo_richiesta_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/res_users_demo.xml',
        'demo/ca_ente_azienza_demo.xml',
        'demo/ca_tipo_spazio_demo.xml',
        'demo/ca_spazio_demo.xml',
        'demo/ca_lettore_demo.xml',
        'demo/ca_tag_demo.xml',
        'demo/ca_persona_demo.xml',
        'demo/ca_tag_persona_demo.xml',
    ],
    'installable': True,
    'application': True,
}