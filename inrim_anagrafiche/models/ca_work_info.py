from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaWorkInfoType(models.Model):
    _name = 'ca.work_info_type'
    _inherit = "ca.model.base.mixin"
    _description = 'Tipo Info Lavorative'
    _rec_name = 'name'

    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Char()
    structured = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    @api.constrains('code', 'active')
    def _check_unique_code(self):
        for record in self:
            if record.code:
                tags = self.env['ca.work_info_type'].with_context(
                    active_test=False).search(
                    [
                        ('id', '!=', record.id),
                        ('code', '=', record.code)
                    ]
                )
                if tags:
                    msg = f'Esiste già questa tipologia: {record.code}'
                    if not record.active:
                        msg = f"{record.code} Risulta disattivato, riattivare per utilizzare"
                    raise UserError(_(msg))

    @api.constrains('name', 'active')
    def _check_unique_name(self):
        for record in self:
            if record.name:
                tags = self.env['ca.work_info_type'].with_context(
                    active_test=False).search(
                    [
                        ('id', '!=', record.id),
                        ('name', '=', record.name)
                    ]
                )
                if tags:
                    msg = f'Esiste già questa tipologia: {record.name}'
                    if not record.active:
                        msg = f"{record.name} Risulta disattivato, riattivare per utilizzare"
                    raise UserError(_(msg))

    @api.model
    def get_by_name(self, name):
        return self.env['ca.work_info_type'].search([
            ('name', '=', name)
        ], limit=1)

    def rest_boby_hint(self):
        return {
            "name": "Interno",
            "code": "Interno"
        }

    def rest_get_record(self):
        vals = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'code'
            ])
        return body, msg


class CaWorkInfo(models.Model):
    _name = 'ca.work_info'
    _inherit = "ca.model.base.mixin"
    _description = 'Info Lavorative'
    _rec_name = 'ca_persona_id'

    ca_persona_id = fields.Many2one(
        'ca.persona', required=True)

    work_id_number = fields.Char(
        string="A.C. ID Numeber", groups="controllo_accessi.ca_gdpr")

    ca_work_info_type_id = fields.Many2one(
        'ca.work_info_type', ondelete='cascade')

    ca_title_id = fields.Many2one(
        'ca.titolo_persona', ondelete='cascade')

    ca_div_uo_code = fields.Char(string="DIV/UO")

    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('scheduled', 'Scheduled')
    ], readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end <= record.date_start:
                    raise UserError(
                        _('Data fine deve essere maggiore della data di inizio'))

    def check_update_state(self):
        now = fields.Date.today()
        self.ensure_one()
        if self.date_start <= now <= self.date_end:
            self.state = 'active'
        elif self.date_start > now:
            self.state = 'scheduled'
        else:
            self.state = 'expired'

    def check_update_by_date_valididty(self):
        for winfo_persona in self.search([]):
            if winfo_persona:
                winfo_persona.check_update_state()

    def _cron_check_validity_winfo(self):
        self.check_update_by_date_valididty()

    @api.model_create_multi
    def create(self, vals):
        res = super(CaWorkInfo, self).create(vals)
        res.check_update_state()
        return res

    @api.onchange('date_start', 'date_end')
    def check_date(self):
        for record in self:
            record.check_update_state()
