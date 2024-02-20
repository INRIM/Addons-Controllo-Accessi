from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from datetime import date
import base64

@tagged("post_install", "-at_install")
class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        # Utenti
        cls.user = cls.env['res.users'].create({
            'name' : 'User',
            'login': 'User',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_base').id])]
        })
        cls.user_1 = cls.env['res.users'].create({
            'name' : 'User 1',
            'login': 'User 1',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_ca').id])]
        })
        cls.user_2 = cls.env['res.users'].create({
            'name' : 'User 2',
            'login': 'User 2',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_ru').id])]
        })
        cls.user_3 = cls.env['res.users'].create({
            'name' : 'User 3',
            'login': 'User 3',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_spp').id])]
        })
        cls.user_4 = cls.env['res.users'].create({
            'name' : 'User 4',
            'login': 'User 4',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_portineria').id])]
        })
        cls.user_5 = cls.env['res.users'].create({
            'name' : 'User 5',
            'login': 'User 5',
            'groups_id': [(6, 0, [cls.env.ref('inrim_controllo_accessi_base.ca_tech').id])]
        })
        # Enti/Aziende
        cls.ente_azienda_1 = cls.env['ca.ente_azienda'].create({
            'name' : 'Campus',
            'pec': 'Pec 1',
            'tipo_ente_azienda_id': cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            'note': 'Ente Azienda 1'
        })
        cls.ente_azienda_2 = cls.env['ca.ente_azienda'].create({
            'name' : 'Campus',
            'pec': 'Sede 2',
            'tipo_ente_azienda_id': cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
            'note': 'Ente Azienda 2'
        })
        cls.ente_azienda_3 = cls.env['ca.ente_azienda'].create({
            'name' : 'Azienda Test',
            'pec': 'Sede 3',
            'tipo_ente_azienda_id': cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_azienda').id,
            'note': 'Ente Azienda 3'
        })
        cls.ente_azienda_4 = cls.env['ca.ente_azienda'].create({
            'name' : 'Professionista Test',
            'pec': 'Sede 4',
            'tipo_ente_azienda_id': cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_professionista').id,
            'note': 'Ente Azienda 4'
        })
        cls.ente_azienda_5 = cls.env['ca.ente_azienda'].create({
            'name' : 'Ente test',
            'pec': 'Sede 5',
            'tipo_ente_azienda_id': cls.env.ref('inrim_anagrafiche.tipo_ente_azienda_universita').id,
            'note': 'Ente Azienda 5'
        })
        # Persona
        cls.persona_1 = cls.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '1',
            'fiscalcode': 'Fiscalcode 1',
            'type_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.tipo_persona_esterno').id
                ]
            )],
            'ca_documento_ids': cls.env['ca.documento'].create({
                'tipo_documento_id': cls.env.ref('inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
                'validity_start_date': date(2024, 1, 1),
                'validity_end_date': date(2024, 6, 30),
                'image_ids': [(6, 0, [
                    cls.env['ca.img_documento'].create({
                        'name': 'Fronte 1',
                        'side': 'fronte',
                        'image': base64.b64encode(b'Fronte 1')
                    }).id,
                    cls.env['ca.img_documento'].create({
                        'name': 'Retro 1',
                        'side': 'retro',
                        'image': base64.b64encode(b'Retro 1')
                    }).id
                ])],
                'document_code_id': cls.env['ca.codice_documento'].create({
                    'name': 'Codice Doc Persona 1'
                }).id
            })
        })
        cls.persona_2 = cls.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '2',
            'fiscalcode': 'Fiscalcode 2',
            'type_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.tipo_persona_esterno').id,
                    cls.env.ref('inrim_anagrafiche.tipo_persona_servizi_mensa_ristorazione').id
                ]
            )],
            'ca_documento_ids': cls.env['ca.documento'].create({
                'tipo_documento_id': cls.env.ref('inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
                'validity_start_date': date(2024, 6, 30),
                'validity_end_date': date(2024, 12, 31),
                'image_ids': [(6, 0, [
                    cls.env['ca.img_documento'].create({
                        'name': 'Fronte 2',
                        'side': 'fronte',
                        'image': base64.b64encode(b'Fronte 2')
                    }).id
                ])],
                'document_code_id': cls.env['ca.codice_documento'].create({
                    'name': 'Codice Doc Persona 2'
                }).id
            })
        })
        cls.persona_3 = cls.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '3',
            'fiscalcode': 'Fiscalcode 3',
            'type_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.tipo_persona_esterno').id,
                    cls.env.ref('inrim_anagrafiche.tipo_persona_servizi').id
                ]
            )],
            'ca_documento_ids': cls.env['ca.documento'].create({
                'tipo_documento_id': cls.env.ref('inrim_anagrafiche.tipo_doc_ident_carta_identita').id,
                'validity_start_date': date(2024, 6, 30),
                'validity_end_date': date(2024, 12, 31),
                'image_ids': [(6, 0, [
                    cls.env['ca.img_documento'].create({
                        'name': 'Fronte 3',
                        'side': 'fronte',
                        'image': base64.b64encode(b'Fronte 3')
                    }).id
                ])],
                'document_code_id': cls.env['ca.codice_documento'].create({
                    'name': 'Codice Doc Persona 3'
                }).id
            })
        })
        cls.persona_4 = cls.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '4',
            'fiscalcode': 'Fiscalcode 4',
            'type_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.tipo_persona_interno').id,
                    cls.env.ref('inrim_anagrafiche.tipo_persona_dipendente_ti').id
                ]
            )]
        })
        cls.persona_5 = cls.env['ca.persona'].create({
            'name': 'Persona',
            'lastname': '5',
            'fiscalcode': 'Fiscalcode 5',
            'type_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.tipo_persona_interno').id,
                    cls.env.ref('inrim_anagrafiche.tipo_persona_dipendente_td').id
                ]
            )]
        })
        # Tag
        cls.tag_1 = cls.env['ca.tag'].create({
            'name': 'Tag 1',
            'tag_code': 'E0010150AD255C11',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_temporaneo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_visitatore').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_valido').id
                ]
            )]
        })
        cls.tag_2 = cls.env['ca.tag'].create({
            'name': 'Tag 2',
            'tag_code': 'E0010150AD255C12',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_temporaneo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_jolly').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_valido').id
                ]
            )]
        })
        cls.tag_3 = cls.env['ca.tag'].create({
            'name': 'Tag 3',
            'tag_code': 'E0010150AD255C13',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_valido').id
                ]
            )]
        })
        cls.tag_4 = cls.env['ca.tag'].create({
            'name': 'Tag 4',
            'tag_code': 'E0010150AD255C14',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_valido').id
                ]
            )]
        })
        cls.tag_5 = cls.env['ca.tag'].create({
            'name': 'Tag 5',
            'tag_code': 'E0010150AD255C15',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_valido').id
                ]
            )]
        })
        cls.tag_6 = cls.env['ca.tag'].create({
            'name': 'Tag 6',
            'tag_code': 'E0010150AD255C16',
            'ca_proprieta_tag_ids': [(6, 0,
                [
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_definitivo').id,
                    cls.env.ref('inrim_anagrafiche.proprieta_tag_revocato').id
                ]
            )]
        })
        # Lettore
        cls.lettore_1 = cls.env['ca.lettore'].create({
            'name': 'Lettore 1',
            'reader_ip': '10.10.10.1',
            'direction': 'in'
        })
        cls.lettore_2 = cls.env['ca.lettore'].create({
            'name': 'Lettore 2',
            'reader_ip': '10.10.10.3',
            'direction': 'out'
        })