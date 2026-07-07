from odoo import models, fields, api


class CaEnteAzienda(models.Model):
    _inherit = 'ca.ente_azienda'

    url_gateway_lettori = fields.Char(groups="controllo_accessi.ca_tech",
                                      string="Url Gateway Readers")
    nome_chiave_header = fields.Char(groups="controllo_accessi.ca_tech",
                                     default="authtoken", 
                                     string="Name Key Header")
    jwt = fields.Char(groups="controllo_accessi.ca_tech")
    ref = fields.Char()
    lock = fields.Boolean()

    def update_default(self):
        sede = self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede')
        sede_distaccata = self.env.ref(
            'inrim_anagrafiche.tipo_ente_azienda_sede_distaccata')
        config = self.env['ir.config_parameter'].sudo()
        for record in self.sudo():
            if record.tipo_ente_azienda_id.id in [sede.id, sede_distaccata.id]:
                vals = {}
                if not record.jwt:
                    vals['jwt'] = config.get_param('service_reader.jwt')
                if not record.url_gateway_lettori:
                    vals['url_gateway_lettori'] = config.get_param(
                        'service_reader.url')
                if vals:
                    record.with_context(skip_update_default=True).sudo().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CaEnteAzienda, self).create(vals_list)
        res.with_context(skip_update_default=True).update_default()
        return res

    def write(self, vals):
        res = super(CaEnteAzienda, self).write(vals)
        if not self.env.context.get("skip_update_default"):
            self.with_context(skip_update_default=True).update_default()
        return res
