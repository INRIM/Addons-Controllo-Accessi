from odoo import models, fields, api


class CaEnteAzienda(models.Model):
    _inherit = 'ca.ente_azienda'

    url_gateway_lettori = fields.Char(groups="controllo_accessi.ca_tech")
    nome_chiave_header = fields.Char(groups="controllo_accessi.ca_tech",
                                     default="authtoken")
    jwt = fields.Char(groups="controllo_accessi.ca_tech")
    ref = fields.Char()
    lock = fields.Boolean()

    def update_default(self):
        sede = self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        sede_distaccata = self.env.ref(
            'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata')
        for record in self:
            if record.tipo_ente_azienda_id.id in [sede.id, sede_distaccata.id]:
                if not record.jwt:
                    record.jwt = self.env['ir.config_parameter'].sudo().get_param(
                        'service_reader.jwt')
                if not record.url_gateway_lettori:
                    record.url_gateway_lettori = self.env[
                        'ir.config_parameter'].sudo().get_param('service_reader.url')

    @api.model_create_multi
    def create(self, vals):
        res = super(CaEnteAzienda, self).create(vals)
        self.with_context(skip_update_default=True).update_default()
        return res

    def write(self, vals):
        res = super(CaEnteAzienda, self).write(vals)
        if not self.env.context.get("skip_update_default"):
            self.with_context(skip_update_default=True).update_default()
        return res
