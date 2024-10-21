from odoo import models, fields, api

class CaEnteAzienda(models.Model):
    _inherit = 'ca.ente_azienda'

    url_gateway_lettori = fields.Char(groups="inrim_controllo_accessi_base.ca_tech")
    nome_chiave_header = fields.Char(groups="inrim_controllo_accessi_base.ca_tech")
    jwt = fields.Char(groups="inrim_controllo_accessi_base.ca_tech")
    ref = fields.Char()
    lock = fields.Boolean()

    @api.model_create_multi
    def create(self, vals):
        res = super(CaEnteAzienda, self).create(vals)
        sede = self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        for record in res:
            if self.env.user.has_group('inrim_controllo_accessi_base.ca_tech'):
                if record.tipo_ente_azienda_id == sede:
                    if not record.jwt:
                        record.jwt = self.env['ir.config_parameter'].sudo().get_param('service_reader.jwt')
                    if not record.url_gateway_lettori:
                        record.url_gateway_lettori = self.env['ir.config_parameter'].sudo().get_param('service_reader.url')
        return res
    
    def write(self, vals):
        res = super(CaEnteAzienda, self).write(vals)
        sede = self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        for record in self:
            if self.env.user.has_group('inrim_controllo_accessi_base.ca_tech'):
                if record.tipo_ente_azienda_id == sede:
                    if not record.jwt:
                        record.jwt = self.env['ir.config_parameter'].sudo().get_param('service_reader.jwt')
                    if not record.url_gateway_lettori:
                        record.url_gateway_lettori = self.env['ir.config_parameter'].sudo().get_param('service_reader.url')
        return res