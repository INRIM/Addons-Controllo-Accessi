{
    'name': 'Inrim Controllo Accessi Provisioning Lettori',
    'version': '19.0.1.0.0',
    'summary': "Procedura di installazione e sostituzione lettori badge, via API",
    'description': """
Procedura guidata (record con stato) per installare un nuovo lettore badge o
sostituire un lettore danneggiato, pilotabile via API REST (es. da Ansible).
Include un check generico del lettore (/info + /status del gateway).
""",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'controllo_accessi_inrim_app',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
