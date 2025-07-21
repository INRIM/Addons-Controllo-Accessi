import random
import string

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CaPersona(models.Model):
    _name = 'ca.persona'
    _inherit = "ca.model.base.mixin"
    _description = 'Persona'
    _rec_name = "display_name"
    _rec_names_search = ['display_name', 'token', 'uid', 'fiscalcode', 'freshman']

    name = fields.Char(required=True)
    lastname = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    associated_user_id = fields.Many2one('res.users')
    fiscalcode = fields.Char(groups="controllo_accessi.ca_gdpr")
    vat = fields.Char()
    type_ids = fields.Many2many('ca.tipo_persona')
    freshman = fields.Char()
    work_id_number = fields.Char(string="A.C. ID Number",
                                 groups="controllo_accessi.ca_gdpr")
    nationality = fields.Many2one('res.country', groups="controllo_accessi.ca_gdpr")
    birth_date = fields.Date(groups="controllo_accessi.ca_gdpr")
    birth_place = fields.Char(groups="controllo_accessi.ca_gdpr")
    istat_code = fields.Char(groups="controllo_accessi.ca_gdpr")
    parent_id = fields.Many2one(
        'ca.persona', string='Reference person', index=True,
        domain=[('is_internal', '=', True)]
    )
    child_ids = fields.One2many(
        'ca.persona', 'parent_id', string='Contact',
        domain=[('active', '=', True)]
    )
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    private_mobile = fields.Char()
    residence_street = fields.Char()
    residence_street2 = fields.Char()
    residence_city = fields.Char(
        compute='_compute_residence_city', readonly=False, store=True
    )
    residence_zip = fields.Char(
        compute='_compute_residence_zip',
        readonly=False, store=True
    )
    residence_state_id = fields.Many2one(
        'res.country.state',
        domain="[('country_id', '=?', residence_country_id)]",
        compute='_compute_residence_state_id', readonly=False, store=True
    )
    residence_country_id = fields.Many2one(
        'res.country', compute='_compute_residence_country_id',
        readonly=False, store=True
    )
    residence_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_residence_zip_id",
        readonly=False,
        store=True,
    )
    residence_city_id = fields.Many2one(
        'res.city',
        index=True,
        compute="_compute_residence_city_id",
        readonly=False,
        store=True,
    )
    domicile_street = fields.Char()
    domicile_street2 = fields.Char()
    domicile_city = fields.Char(
        compute='_compute_domicile_city', readonly=False, store=True
    )
    domicile_state_id = fields.Many2one(
        'res.country.state',
        domain="[('country_id', '=?', domicile_country_id)]",
        compute='_compute_domicile_state_id', readonly=False, store=True
    )
    domicile_zip = fields.Char(
        compute='_compute_domicile_zip',
        readonly=False, store=True
    )
    domicile_country_id = fields.Many2one(
        'res.country', compute='_compute_domicile_country_id',
        readonly=False, store=True
    )
    domicile_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_domicile_zip_id",
        readonly=False,
        store=True,
    )
    domicile_city_id = fields.Many2one(
        'res.city',
        index=True,
        compute="_compute_domicile_city_id",
        readonly=False,
        store=True,
    )
    domicile_other_than_residence = fields.Boolean()
    ca_workinfo_ids = fields.One2many('ca.work_info', 'ca_persona_id')
    ca_documento_ids = fields.One2many(
        'ca.documento', 'ca_persona_id', string="Document")
    ca_stato_anag_id = fields.Many2one('ca.stato_anag', default=lambda
        self: self.default_ca_stato_anag_id(), required=True,
                                       string="Partner Status")
    ca_ente_azienda_ids = fields.Many2many('ca.ente_azienda', string="Companies")
    token = fields.Char(required=True, readonly=True, copy=False,
                        default=lambda self: self.get_token())
    present = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], default='no', readonly=True)
    send_to_payroll_system = fields.Boolean()
    uid = fields.Char()
    note = fields.Text()
    trust_level = fields.Integer("Trust Level", default=1)
    is_external = fields.Boolean(compute="_compute_bool", store=True)
    is_internal = fields.Boolean(compute="_compute_bool", store=True)
    is_structured = fields.Boolean(compute='_compute_is_structured', store=True)
    current_tag = fields.Many2one('ca.tag_persona', compute='_compute_current_tag')
    ca_tag_ids = fields.One2many('ca.tag_persona', 'ca_persona_id', readonly=True,
                                 string="Tag")
    active = fields.Boolean(default=True)

    @api.depends('ca_tag_ids', 'ca_tag_ids.state')
    def _compute_current_tag(self):
        for persona in self:
            persona.current_tag = persona.get_current_tag()

    def get_current_tag(self):
        tag = self.ca_tag_ids.search(
            [('ca_persona_id', '=', self.id), ('state', '=', 'to_give_back')],
            order='id desc', limit=1)

        return tag or False

    def set_tag_returned(self):
        tag.state = 'returned'

    def btn_presence(self):
        ...

    def get_current_winfo(self):
        winfo = self.env['ca.work_info'].search([
            ('ca_persona_id', '=', self.id), ('state', '=', 'active')])
        return winfo

    def update_work_info(self, vals):
        winfo = self.get_current_winfo()
        create_enable = False
        if winfo:
            if vals.get("date_start") and vals.get("date_start") > winfo.date_end:
                create_enable = True
            else:
                self.env['ca.work_info'].write(vals)
                winfo.check_update_state()
        if not winfo or create_enable:
            self.env['ca.work_info'].create(vals)

    @api.constrains('is_external', 'parent_id')
    def _check_external_and_parent_id(self):
        check = False
        for record in self:
            if (
                    record.is_external and
                    not record.parent_id and
                    not self.env.context.get("massive_create") and
                    check
            ):
                raise ValidationError(
                    _("For External person Internal reference is required "))

    @api.constrains('fiscalcode', 'active')
    def _check_unique_fiscalcode(self):
        for record in self:
            if record.fiscalcode:
                persona_id = self.env['ca.persona'].with_context(
                    active_test=False).search(
                    [
                        ('id', '!=', record.id),
                        ('fiscalcode', '=', record.fiscalcode)
                    ]
                )
                if persona_id:
                    msg = _(
                        f'Esiste già una persona con questo codice fiscale: {record.fiscalcode}')
                    if not record.active:
                        msg = _(
                            f"{msg} la persona Risulta disattivata, riattivare per utilizzare")
                    raise UserError(
                        _(msg))

    @api.constrains('ca_documento_ids')
    def _check_external_documento_ids(self):
        check = False
        for record in self:
            if check and len(record.ca_documento_ids) == 0 and record.is_external:
                if not self.env.context.get(
                        "massive_create") or not self.env.context.get("wizard_create"):
                    raise UserError(_(
                        'For an external person it is mandatory to upload the documents'))

    @api.onchange('domicile_state_id')
    def _onchange_domicile_state_id(self):
        if self.domicile_state_id.country_id:
            self.domicile_country_id = self.domicile_state_id.country_id

    @api.onchange('residence_state_id')
    def _onchange_residence_state_id(self):
        if self.residence_state_id.country_id:
            self.residence_country_id = self.residence_state_id.country_id

    @api.depends('type_ids')
    def _compute_bool(self):
        for record in self:
            record.is_external = False
            record.is_internal = False
            interno_id = self.env.ref('inrim_anagrafiche.tipo_persona_interno').id
            esterno_id = self.env.ref('inrim_anagrafiche.tipo_persona_esterno').id
            if interno_id in record.type_ids.ids:
                record.is_internal = True
            elif (
                    esterno_id in record.type_ids.ids
            ):
                record.is_external = True

    @api.depends('type_ids', 'type_ids.structured')
    def _compute_is_structured(self):
        for record in self:
            record.is_structured = False
            for type in record.type_ids:
                if type.structured:
                    record.is_structured = True

    def compute_name(self):
        self.ensure_one()
        self.display_name = False
        winfo = self.get_current_winfo()
        spec = ''
        if winfo:
            spec = winfo.ca_div_uo_code
        if not spec:
            if self.ca_ente_azienda_ids:
                specs = [r.name for r in self.ca_ente_azienda_ids if r]
                spec = ", ".join(specs)
            else:
                spec = 'No Spec'
        if self.name and self.lastname:
            self.display_name = f"{self.lastname} {self.name} ({spec})"

    @api.depends('name', 'lastname', "ca_workinfo_ids")
    def _compute_display_name(self):
        for record in self:
            record.compute_name()

    def default_ca_stato_anag_id(self):
        return self.env.ref('inrim_anagrafiche.ca_stato_anag_bozza').id

    def action_draft(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_bozza').id

    def action_documents(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_in_attesa_documenti').id

    def action_expired(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_scaduto').id

    def action_in_update(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_in_aggiornamento').id

    def action_checks_in_progress(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_verifiche_in_corso').id

    def action_completed(self):
        for record in self:
            record.ca_stato_anag_id = self.env.ref(
                'inrim_anagrafiche.ca_stato_anag_completata').id

    def action_attendance_today(self):
        return {
            'name': _('Access Log'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ca.anag_registro_accesso',
            'domain': [('ca_ente_azienda_id', 'in', self.ca_ente_azienda_ids.ids)],
        }

    def update_m2o(self, vals):
        res = []
        fields = [
            'nationality',
            'residence_zip',
            'residence_city',
            'domicile_zip'
            'domicile_city',
        ]
        for v in vals:
            ret = {**v}
            for field in fields:
                if v.get(field):
                    if field != "nationality" and field.find('city') > 0:
                        rec = self.env['res.city'].search(
                            [('name', '=', v.get(field))], limit=1
                        )
                        ret[f'{field}_id'] = rec.id if rec else False
                    elif field != "nationality" and field.find('zip') > 0:
                        pre = field.split('_')[0]
                        rec = self.env['res.city.zip'].search(
                            [
                                ('name', '=', v.get(field)),
                                ('city_id.name', '=', v.get(f'{pre}_city')),
                            ], limit=1
                        )
                        ret[f'{field}_id'] = rec.id if rec else False
                    else:
                        rec = self.env['res.country'].search(
                            [('code', '=', v.get(field))]
                        )
                        ret[field] = rec.id if rec else False
            res.append(ret)
        return res

    @api.model_create_multi
    def create(self, vals):
        # newvals = self.update_m2o(vals)
        newvals = vals
        res = super(CaPersona, self).create(newvals)
        self._check_external_documento_ids()
        return res

    def write(self, vals_list):
        res = super(CaPersona, self).write(vals_list)
        self._check_external_documento_ids()
        return res

    def get_token(self):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(10))
        persona_id = self.env['ca.persona'].search([('token', '=', token)])
        if persona_id:
            self.get_token()
        return token

    def get_by_login_uid(self, uid):
        if uid:
            user_id = self.env['res.users'].search([
                ('login', '=', uid)
            ], limit=1)
            person_id = self.env['ca.persona'].search([
                ('associated_user_id', '=', user_id.id)
            ], limit=1)
            return person_id
        return False

    # DOMICILE
    @api.depends("domicile_state_id", "domicile_country_id", "domicile_city_id",
                 "domicile_zip")
    def _compute_domicile_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("domicile_zip_id"):
            fields_map = {
                "domicile_zip": "name",
                "domicile_city_id": "city_id",
                "domicile_state_id": "state_id",
                "domicile_country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                        record[rec_field]
                        and record[rec_field] != record._origin[rec_field]
                        and record[rec_field] != record.domicile_zip_id[zip_field]
                ):
                    record.domicile_zip_id = False
                    break

    @api.depends("domicile_zip_id")
    def _compute_domicile_city_id(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_city_id = record.domicile_zip_id.city_id

    @api.depends("domicile_zip_id")
    def _compute_domicile_city(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_city = record.domicile_zip_id.city_id.name

    @api.depends("domicile_zip_id")
    def _compute_domicile_zip(self):
        for record in self:
            if record.domicile_zip_id:
                record.domicile_zip = record.domicile_zip_id.name

    @api.depends("domicile_zip_id", "domicile_state_id")
    def _compute_domicile_country_id(self):
        for record in self:
            if record.domicile_zip_id.city_id.country_id:
                record.domicile_country_id = record.domicile_zip_id.city_id.country_id
            elif record.domicile_state_id:
                record.domicile_country_id = record.domicile_state_id.country_id

    @api.depends("domicile_zip_id")
    def _compute_domicile_state_id(self):
        for record in self:
            state = record.domicile_zip_id.city_id.state_id
            if state and record.domicile_state_id != state:
                record.domicile_state_id = record.domicile_zip_id.city_id.state_id

    @api.constrains("domicile_zip_id", "domicile_country_id", "domicile_city_id",
                    "domicile_state_id", "domicile_zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.domicile_zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.domicile_zip_id.name}
            if rec.domicile_zip_id.city_id.country_id != rec.domicile_country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.city_id.state_id != rec.domicile_state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.city_id != rec.domicile_city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.domicile_zip_id.name != rec.domicile_zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )

    # RESIDENCE
    @api.depends("residence_state_id", "residence_country_id", "residence_city_id",
                 "residence_zip")
    def _compute_residence_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("residence_zip_id"):
            fields_map = {
                "residence_zip": "name",
                "residence_city_id": "city_id",
                "residence_state_id": "state_id",
                "residence_country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                        record[rec_field]
                        and record[rec_field] != record._origin[rec_field]
                        and record[rec_field] != record.residence_zip_id[zip_field]
                ):
                    record.residence_zip_id = False
                    break

    @api.depends("residence_zip_id")
    def _compute_residence_city_id(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_city_id = record.residence_zip_id.city_id

    @api.depends("residence_zip_id")
    def _compute_residence_city(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_city = record.residence_zip_id.city_id.name

    @api.depends("residence_zip_id")
    def _compute_residence_zip(self):
        for record in self:
            if record.residence_zip_id:
                record.residence_zip = record.residence_zip_id.name

    @api.depends("residence_zip_id", "residence_state_id")
    def _compute_residence_country_id(self):
        for record in self:
            if record.residence_zip_id.city_id.country_id:
                record.residence_country_id = record.residence_zip_id.city_id.country_id
            elif record.residence_state_id:
                record.residence_country_id = record.residence_state_id.country_id

    @api.depends("residence_zip_id")
    def _compute_residence_state_id(self):
        for record in self:
            state = record.residence_zip_id.city_id.state_id
            if state and record.residence_state_id != state:
                record.residence_state_id = record.residence_zip_id.city_id.state_id

    @api.constrains("residence_zip_id", "residence_country_id", "residence_city_id",
                    "residence_state_id", "residence_zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.residence_zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.residence_zip_id.name}
            if rec.residence_zip_id.city_id.country_id != rec.residence_country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.city_id.state_id != rec.residence_state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.city_id != rec.residence_city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.residence_zip_id.name != rec.residence_zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )

    def rest_boby_hint(self):
        return {
            "name": "",
            "lastname": "",
            "fiscalcode": "",
            "parent_id": "",
        }

    def rest_get_record(self):
        winfo = self.get_current_winfo()
        vals = {
            'id': self.id,
            "uid": self.uid,
            'name': self.name,
            'lastname': self.lastname,
            'display_name': self.display_name,
            'parent_id': self.f_m2o(self.parent_id),
            'associated_user_id': self.f_m2o(self.associated_user_id),
            'domicile_street': self.domicile_street or "",
            'domicile_street2': self.domicile_street2 or "",
            'domicile_city': self.domicile_city or "",
            'domicile_zip': self.domicile_zip or "",
            'domicile_state_id': self.f_m2o(self.domicile_state_id),
            'domicile_country_id': self.f_m2o(self.domicile_country_id),
            'vat': self.vat or "",
            'domicile_other_than_residence': self.domicile_other_than_residence,
            'type_ids': self.f_m2m(self.type_ids),
            'ca_ente_azienda_ids': self.f_m2m(self.ca_ente_azienda_ids),
            'present': self.f_selection("present", self.present),
            'token': self.token,
            'residence_street': self.residence_street or "",
            'residence_street2': self.residence_street2 or "",
            'residence_city': self.residence_city or "",
            'residence_zip': self.residence_zip or "",
            'residence_state_id': self.f_m2o(self.residence_state_id),
            'residence_country_id': self.f_m2o(self.residence_country_id),
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'ca_workinfo_ids': self.f_o2m(self.ca_workinfo_ids),
            'send_to_payroll_system': self.send_to_payroll_system,
            "current_tag": self.current_tag.rest_get_record(),
            "current_workinfo": winfo.rest_get_record() if winfo else {}
        }
        if self.env.user.has_group('controllo_accessi.ca_gdpr'):
            vals.update({
                'fiscalcode': self.fiscalcode,
                'freshman': self.freshman or "",
                'nationality': self.f_m2o(self.nationality),
                'birth_date': self.f_date(self.birth_date),
                'birth_place': self.birth_place,
                'istat_code': self.istat_code,
            })
        return vals

    def rest_eval_body(self, body):
        body, msg = super().rest_eval_body(
            body, [
                'name', 'lastname', 'fiscalcode'
            ])
        return body, msg
