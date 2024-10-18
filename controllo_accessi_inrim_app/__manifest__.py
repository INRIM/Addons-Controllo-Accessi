{
    'name': 'App Controllo Accessi INRIM',
    'version': '17.0.1.0.0',
    'description': "App Controllo Accessi INRIM",
    "author": "Alessio Gerace - Inrim",
    "website": "https://github.com/INRIM",
    'depends': [
        'inrim_iam_user_ldap',
        'controllo_accessi',
        'inrim_controllo_accessi_rfidglobal'
    ],
    'data': [
        'data/res_company_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
