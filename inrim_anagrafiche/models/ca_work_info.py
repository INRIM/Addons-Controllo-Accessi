from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CaWorkInfoType(models.Model):
    _name = 'ca.work_info_type'
    _inherit = "ca.model.base.mixin"
    _description = 'Tipo Info Lavorative'
    _rec_name = 'name'
    _rec_names_search = ["code", "name"]

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
                    msg = _(f'Esiste già questa tipologia: {record.code}')
                    if not record.active:
                        msg = _(
                            f"{record.code} Risulta disattivato, riattivare per utilizzare")
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
                    msg = _(f'Esiste già questa tipologia: {record.name}')
                    if not record.active:
                        msg = _(
                            f"{record.name} Risulta disattivato, riattivare per utilizzare")
                    raise UserError(_(msg))

    @api.model
    def get_by_name(self, name):
        return self.env['ca.work_info_type'].search([
            ('name', '=', name)
        ], limit=1)

    @api.model
    def get_by_code(self, code):
        return self.env['ca.work_info_type'].search([
            ('code', '=', code)
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
            'structured': self.structured,
        }
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'code', 'structured'
            ])
        return body, msg


class CaWorkInfo(models.Model):
    _name = 'ca.work_info'
    _inherit = "ca.model.base.mixin"
    _description = 'Info Lavorative'
    _rec_name = 'ca_persona_id'
    _order = "date_end desc"

    ca_persona_id = fields.Many2one(
        'ca.persona', required=True, string="Person")

    work_id_number = fields.Char(string="ID Number")

    ca_work_info_type_id = fields.Many2one(
        'ca.work_info_type', ondelete='cascade')

    ca_title_id = fields.Many2one(
        'ca.titolo_persona', ondelete='cascade', string="Title")

    ca_div_uo_code = fields.Char(string="DIV/UO")

    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('scheduled', 'Scheduled')
    ], readonly=True, string='Status')
    active = fields.Boolean(default=True)

    @api.depends_context('show_work_id_number')
    def _compute_display_name(self):
        if not self.env.context.get('show_work_id_number', False):
            return super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.work_id_number} - {record.ca_persona_id.display_name}"

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_start:
                if record.date_end < record.date_start:
                    raise UserError(
                        _('End date must be greater than start date'))

    def check_update_state(self):
        now = fields.Date.today()
        self.ensure_one()
        if not self.date_start or not self.date_end:
            return
        if self.date_start <= now <= self.date_end:
            self.state = 'active'
        elif self.date_start > now:
            self.state = 'scheduled'
        else:
            self.state = 'expired'

    def check_update_by_date_valididty(self):
        for winfo_persona in self.env['ca.work_info'].search([]):
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

    def rest_get_record(self):
        return {
            "id": self.id,
            "ca_persona_id": self.f_m2o(self.ca_persona_id),
            "work_id_number": self.work_id_number,
            "ca_work_info_type_id": self.ca_work_info_type_id.rest_get_record(),
            "ca_title_id": self.ca_title_id.rest_get_record(),
            "ca_div_uo_code": self.ca_div_uo_code,
            "date_start": self.f_date(self.date_start),
            "date_end": self.f_date(self.date_end),
            "state": self.state,
            "active": self.active,
        }
