{
    'name': 'Inrim Controllo Accessi Base',
    'version': '17.0.1.0.0',
    'description': "Inrim Controllo Accessi Base",
    'depends': ['base'],
    'data': [
        'security/security.xml',
    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
}