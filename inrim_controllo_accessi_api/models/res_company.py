from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_people = fields.Boolean()
    people_x_key = fields.Char('People X-Key')
    people_url = fields.Char()
    get_addressbook_path = fields.Char()