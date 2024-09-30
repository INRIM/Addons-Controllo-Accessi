from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    # People
    enable_people = fields.Boolean()
    people_x_key = fields.Char('People X-Key')
    people_url = fields.Char()
    get_addressbook_path = fields.Char(default="/api/get_addressbook")
    get_rooms_path = fields.Char(default="/api/get_rooms")
    # RFID
    enable_rfid = fields.Boolean('Enable RFID')
    rfid_token_jwt = fields.Char('Token JWT')
    rfid_url = fields.Char('RFID Url')
    rfid_info_path = fields.Char('RFID Info Path', default='/info')
    rfid_status_path = fields.Char('RFID Status Path', default='/status')