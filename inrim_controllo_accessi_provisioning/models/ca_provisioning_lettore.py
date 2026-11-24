import json
import logging
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

REPLACE_SUFFIX = ".replace"
SYNC_RETRY_SECONDS = 60
MAX_LISTED_DIFF = 20

OPERATIONS = [
    ('install', 'Installazione'),
    ('replace', 'Sostituzione'),
]
TYPOLOGIES = [
    ('stamping', 'Stamping'),
    ('local_access', 'Local Access'),
]
STATES = [
    ('draft', 'Bozza'),
    ('checked', 'IP verificato'),
    ('grouped', 'Gruppo scelto'),
    ('configured', 'Punto accesso creato'),
    ('active', 'Punto accesso attivo'),
    ('verified', 'Verificato'),
    ('ip_change', 'Cambio IP in corso'),
    ('done', 'Completata'),
    ('cancelled', 'Annullata'),
]
# Passi invocabili via API (nome passo -> metodo)
STEPS = {
    'check_ip': 'step_check_ip',
    'set_group': 'step_set_group',
    'set_replace': 'step_set_replace',
    'set_access_point': 'step_set_access_point',
    'set_position': 'step_set_position',
    'activate': 'step_activate',
    'verify': 'step_verify',
    'disable_old': 'step_disable_old',
    'final_check': 'step_final_check',
    'cancel': 'step_cancel',
}


class CaProvisioningLettoreLog(models.Model):
    _name = 'ca.provisioning_lettore_log'
    _description = 'Provisioning Lettore - Log passi'
    _order = 'id desc'

    provisioning_id = fields.Many2one(
        'ca.provisioning_lettore', required=True, ondelete='cascade', index=True)
    step = fields.Char(required=True)
    ok = fields.Boolean()
    message = fields.Text()
    data = fields.Text()


class CaProvisioningLettore(models.Model):
    """
    Procedura di installazione [I] o sostituzione [S] di un lettore badge.

    Ogni passo e' un metodo step_* che valida lo stato, esegue il passo e
    restituisce un risultato (ok, messaggio, dati, retry_after). Un passo
    fallito (ok False) non avanza lo stato e si puo' ripetere; un input non
    valido solleva UserError.
    """
    _name = 'ca.provisioning_lettore'
    _inherit = "ca.model.base.mixin"
    _description = 'Provisioning Lettore Badge'
    _order = 'id desc'

    name = fields.Char(readonly=True, copy=False, default="/")
    operation = fields.Selection(OPERATIONS, required=True)
    typology = fields.Selection(TYPOLOGIES, required=True)
    state = fields.Selection(STATES, default='draft', required=True, readonly=True)

    # Passo 2 / 2.1
    reader_ip = fields.Char(string="IP lettore")
    setup_ip = fields.Boolean(
        string="IP solo di setup",
        help="L'IP usato in installazione e' provvisorio: a fine procedura il "
             "dispositivo prendera' l'IP definitivo")
    final_ip = fields.Char(
        string="IP definitivo",
        help="Se vuoto, in sostituzione vale l'IP del lettore sostituito")
    check_ente_azienda_id = fields.Many2one(
        'ca.ente_azienda', string="Sede per il gateway del check")

    # Passo 3
    ca_category_id = fields.Many2one('ca.punto_accesso_category', string="Gruppo")
    # Passo 4.s
    old_punto_accesso_id = fields.Many2one(
        'ca.punto_accesso', string="Punto accesso sostituito")
    old_lettore_id = fields.Many2one(
        'ca.lettore', string="Lettore sostituito", readonly=True)
    # Passo 4.i
    reader_name = fields.Char(string="Nome lettore")
    direction = fields.Selection([('in', 'In'), ('out', 'Out')])
    codice_lettore_grum = fields.Integer(string="Codice lettore GRUM")
    ca_persona_id = fields.Many2one('ca.persona', string="Referente")
    access_point_data_set = fields.Boolean(readonly=True)
    # Passo 5.i
    ca_spazio_id = fields.Many2one('ca.spazio', string="Posizione")

    # Record creati
    ca_lettore_id = fields.Many2one('ca.lettore', string="Nuovo lettore", readonly=True)
    punto_accesso_id = fields.Many2one(
        'ca.punto_accesso', string="Nuovo punto accesso", readonly=True)
    activated_at = fields.Datetime(readonly=True)

    # Ultimo risultato
    last_step = fields.Char(readonly=True)
    last_ok = fields.Boolean(readonly=True)
    last_message = fields.Text(readonly=True)
    log_ids = fields.One2many('ca.provisioning_lettore_log', 'provisioning_id')
    next_step = fields.Char(compute="_compute_next_step")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.name = f"PROV-{record.id:05d}"
        return records

    @api.depends('state', 'operation', 'access_point_data_set')
    def _compute_next_step(self):
        for record in self:
            record.next_step = record._get_next_step()

    def _get_next_step(self):
        self.ensure_one()
        if self.state == 'draft':
            return 'check_ip'
        if self.state == 'checked':
            return 'set_group'
        if self.state == 'grouped':
            if self.operation == 'replace':
                return 'set_replace'
            return 'set_position' if self.access_point_data_set else 'set_access_point'
        if self.state == 'configured':
            return 'activate'
        if self.state == 'active':
            return 'verify'
        if self.state == 'verified':
            return 'disable_old'
        if self.state == 'ip_change':
            return 'final_check'
        return ''

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------

    def rest_get_record(self):
        return {
            "id": self.id,
            "name": self.name,
            "operation": self.operation,
            "typology": self.typology,
            "state": self.state,
            "next_step": self._get_next_step(),
            "reader_ip": self.reader_ip or "",
            "setup_ip": self.setup_ip,
            "final_ip": self.final_ip or "",
            "ca_category_id": self.f_m2o(self.ca_category_id),
            "old_punto_accesso_id": self.f_m2o(self.old_punto_accesso_id),
            "ca_spazio_id": self.f_m2o(self.ca_spazio_id),
            "ca_lettore_id": self.f_m2o(self.ca_lettore_id),
            "punto_accesso_id": self.f_m2o(self.punto_accesso_id),
            "activated_at": self.f_datetime(self.activated_at),
            "last": {
                "step": self.last_step or "",
                "ok": self.last_ok,
                "message": self.last_message or "",
            },
        }

    @api.model
    def start(self, body):
        operation = body.get('operation')
        typology = body.get('typology')
        if operation not in dict(OPERATIONS):
            raise UserError(("operation deve essere 'install' o 'replace'"))
        if typology not in dict(TYPOLOGIES):
            raise UserError(("typology deve essere 'stamping' o 'local_access'"))
        return self.create({'operation': operation, 'typology': typology})

    def run_step(self, step, body):
        self.ensure_one()
        method = STEPS.get(step)
        if not method:
            raise UserError((f"Passo sconosciuto: {step}. Passi: {', '.join(STEPS)}"))
        return getattr(self, method)(body or {})

    def _result(self, step, ok, message, data=None, retry_after=0):
        self.ensure_one()
        self.write({'last_step': step, 'last_ok': ok, 'last_message': message})
        self.env['ca.provisioning_lettore_log'].create({
            'provisioning_id': self.id,
            'step': step,
            'ok': ok,
            'message': message,
            'data': json.dumps(data, default=str) if data else False,
        })
        log = logger.info if ok else logger.warning
        log("%s %s ok=%s: %s", self.name, step, ok, message)
        return {
            'ok': ok,
            'step': step,
            'message': message,
            'retry_after': retry_after,
            'data': data or {},
            'record': self.rest_get_record(),
        }

    def _require(self, states=None, operation=None):
        self.ensure_one()
        if operation and self.operation != operation:
            raise UserError((
                f"Passo valido solo per operation={operation} "
                f"(questa procedura e' {self.operation})"))
        if states and self.state not in states:
            raise UserError((
                f"Passo non valido nello stato '{self.state}': "
                f"prossimo passo '{self._get_next_step() or '-'}'"))

    @staticmethod
    def _get_int(body, key, required=True):
        value = body.get(key)
        if value in (None, "", False):
            if required:
                raise UserError((f"campo {key} obbligatorio"))
            return False
        try:
            return int(value)
        except (TypeError, ValueError):
            raise UserError((f"campo {key} deve essere un intero"))

    def _browse_existing(self, model, rec_id, label):
        record = self.env[model].browse(rec_id).exists()
        if not record:
            raise UserError((f"{label} con id {rec_id} non trovato"))
        return record

    @staticmethod
    def _bool(value):
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ('y', 'yes', 's', 'si', 'true', '1')

    def _checker(self):
        return self.env['ca.reader_check']

    def _gateway_ente(self):
        """Sede da cui prendere il gateway lettori per i check."""
        self.ensure_one()
        return (
            self.punto_accesso_id.ente_azienda_id
            or self.old_punto_accesso_id.ente_azienda_id
            or self.check_ente_azienda_id
        )

    @staticmethod
    def _ap_tag_codes(punto_accesso):
        """Codici tag che il punto accesso scrive sul lettore (vedi
        get_tags_boby: tutti i tag_lettore attivi)."""
        return set(punto_accesso.ca_tag_lettore_ids.mapped('ca_tag_code'))

    def _ap_persons(self, punto_accesso):
        return set(self.env['ca.lettore_persona'].search([
            ('ca_punto_accesso_id', '=', punto_accesso.id),
            ('state', 'in', ['active', 'scheduled']),
        ]).mapped('ca_persona_id').ids)

    def _date_end_for(self, date_end):
        today = fields.Date.context_today(self)
        if date_end and date_end > today:
            return date_end
        return self.env['ca.punto_accesso'].default_date_end()

    # ------------------------------------------------------------------
    # Opzioni per il prossimo passo (per scelte interattive, es. Ansible)
    # ------------------------------------------------------------------

    def get_options(self):
        self.ensure_one()
        step = self._get_next_step()
        options = {'next_step': step}
        sedi = self.env['ca.ente_azienda'].search([
            ('tipo_ente_azienda_id', 'in', [
                self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede').id,
                self.env.ref('inrim_anagrafiche.tipo_ente_azienda_sede_distaccata').id,
            ])
        ])
        if step == 'check_ip':
            options['ente_azienda'] = [{'id': s.id, 'name': s.display_name} for s in sedi]
        elif step == 'set_group':
            options['ca_category'] = [{
                'id': c.id, 'name': c.name, 'code': c.code or "",
                'punti_accesso': len(c.ca_access_point_ids),
            } for c in self.env['ca.punto_accesso_category'].search([], order='name')]
        elif step == 'set_replace':
            options['punto_accesso'] = [{
                'id': p.id,
                'name': p.name,
                'reader_ip': p.ca_lettore_id.reader_ip,
                'codice_lettore_grum': p.codice_lettore_grum,
                'enable_sync': p.enable_sync,
                'system_error': p.system_error,
            } for p in self._replace_candidates()]
        elif step == 'set_position':
            options['ente_azienda'] = [{'id': s.id, 'name': s.display_name} for s in sedi]
            options['tipo_spazio'] = [
                {'id': t.id, 'name': t.name}
                for t in self.env['ca.tipo_spazio'].search([], order='name')]
        return options

    def _replace_candidates(self):
        return self.env['ca.punto_accesso'].search([
            ('ca_category', '=', self.ca_category_id.id),
            ('typology', '=', self.typology),
            ('id', '!=', self.punto_accesso_id.id or 0),
        ], order='name')

    # ------------------------------------------------------------------
    # Passi
    # ------------------------------------------------------------------

    def step_check_ip(self, body):
        """2 / 2.1 - IP non duplicato, lettore che risponde a /info e /status,
        IP definitivo o solo di setup."""
        self._require(states=['draft', 'checked'])
        step = 'check_ip'
        ip = (body.get('ip') or "").strip()
        if not ip:
            raise UserError(("campo ip obbligatorio"))
        if 'setup_ip' not in body:
            raise UserError(("campo setup_ip obbligatorio: l'IP e' solo di setup? (Y/N)"))
        setup_ip = self._bool(body.get('setup_ip'))
        final_ip = (body.get('final_ip') or "").strip()
        if final_ip and not self._checker().valid_ip(final_ip):
            raise UserError((f"final_ip non valido: {final_ip}"))
        ente_id = self._get_int(body, 'ente_azienda_id', required=False)
        ente = self._browse_existing(
            'ca.ente_azienda', ente_id, "Sede") if ente_id else self.check_ente_azienda_id

        owners = self._checker().find_ip_owners(ip)
        if owners:
            names = ", ".join(
                f"{o['lettore']}{'' if o['active'] else ' (archiviato)'}" for o in owners)
            return self._result(
                step, False, f"IP {ip} gia' usato da: {names}. Non procedo.",
                {'duplicate': owners})

        report = self._checker().run(ip, ente_azienda=ente)
        if not report['ok']:
            return self._result(
                step, False,
                f"Lettore su {ip} non leggibile, non procedo: "
                + "; ".join(report['messages']),
                {'check': report})

        self.write({
            'reader_ip': ip,
            'setup_ip': setup_ip,
            'final_ip': final_ip or False,
            'check_ente_azienda_id': ente.id if ente else False,
            'state': 'checked',
        })
        return self._result(step, True, "; ".join(report['messages']), {'check': report})

    def step_set_group(self, body):
        """3 / 3.1.i - Gruppo punti accesso di destinazione, creato se
        installazione e non esiste."""
        self._require(states=['checked', 'grouped'])
        step = 'set_group'
        category_model = self.env['ca.punto_accesso_category']
        category_id = self._get_int(body, 'ca_category_id', required=False)
        new_category = body.get('new_category') or {}
        if category_id:
            category = self._browse_existing(category_model._name, category_id, "Gruppo")
            created = False
        elif new_category:
            if self.operation != 'install':
                raise UserError((
                    "In sostituzione il gruppo deve esistere: passare ca_category_id"))
            name = (new_category.get('name') or "").strip()
            if not name:
                raise UserError(("new_category.name obbligatorio"))
            existing = category_model.search([('name', '=ilike', name)], limit=1)
            if existing:
                raise UserError((
                    f"Il gruppo '{existing.name}' esiste gia' (id {existing.id}): "
                    "passare ca_category_id"))
            category = category_model.create({
                'name': name,
                'code': new_category.get('code') or False,
                'description': new_category.get('description') or False,
            })
            created = True
        else:
            raise UserError(("passare ca_category_id oppure new_category {name, code}"))

        self.write({'ca_category_id': category.id, 'state': 'grouped'})
        msg = f"Gruppo {'creato' if created else 'scelto'}: {category.name}"
        data = {'ca_category_id': category.id, 'created': created}
        if self.operation == 'replace':
            data['punti_accesso'] = [
                {'id': p.id, 'name': p.name} for p in self._replace_candidates()]
            if not data['punti_accesso']:
                return self._result(
                    step, False,
                    f"{msg}, ma non contiene punti accesso {self.typology} da sostituire",
                    data)
        return self._result(step, True, msg, data)

    def step_set_replace(self, body):
        """4.s - Punto accesso da sostituire: crea '<lettore>.replace' e il
        nuovo punto accesso con la stessa configurazione (disabilitato)."""
        self._require(states=['grouped'], operation='replace')
        step = 'set_replace'
        old = self._browse_existing(
            'ca.punto_accesso', self._get_int(body, 'old_punto_accesso_id'),
            "Punto accesso")
        if old not in self._replace_candidates():
            raise UserError((
                f"Il punto accesso {old.name} non e' un punto {self.typology} attivo "
                f"del gruppo {self.ca_category_id.name}"))

        old_lettore = old.ca_lettore_id
        lettore = self.env['ca.lettore'].create({
            'name': f"{old_lettore.name}{REPLACE_SUFFIX}",
            'reader_ip': self.reader_ip,
            'direction': old_lettore.direction,
        })
        vals = {
            'ca_spazio_id': old.ca_spazio_id.id,
            'ca_lettore_id': lettore.id,
            'ca_category': old.ca_category.id,
            'typology': old.typology,
            'ca_persona_id': old.ca_persona_id.id,
            'codice_lettore_grum': old.codice_lettore_grum,
            'events_to_read_num': old.events_to_read_num,
            'recursive_read_events': old.recursive_read_events,
            'date_start': fields.Date.context_today(self),
            'date_end': self._date_end_for(old.date_end),
            'enable_sync': False,
        }
        punto_accesso = self.env['ca.punto_accesso'].create(vals)
        if old.allowed_users:
            punto_accesso.allowed_users = [(6, 0, old.allowed_users.ids)]

        copied = 0
        if old.typology == 'local_access':
            # Gli stessi badge autorizzati del vecchio lettore
            for tag_lettore in old.ca_tag_lettore_ids.filtered(
                    lambda t: t.state != 'expired'):
                self.env['ca.tag_lettore'].create({
                    'ca_lettore_id': lettore.id,
                    'ca_tag_id': tag_lettore.ca_tag_id.id,
                    'date_start': tag_lettore.date_start,
                    'date_end': tag_lettore.date_end,
                    'ca_punto_accesso_id': punto_accesso.id,
                })
                copied += 1
            self.env['ca.lettore_persona'].elabora_persone(lettore)

        self.write({
            'old_punto_accesso_id': old.id,
            'old_lettore_id': old_lettore.id,
            'ca_spazio_id': old.ca_spazio_id.id,
            'ca_lettore_id': lettore.id,
            'punto_accesso_id': punto_accesso.id,
            'final_ip': self.final_ip or (old_lettore.reader_ip if self.setup_ip else False),
            'state': 'configured',
        })
        msg = f"Creato {punto_accesso.name} (lettore {lettore.name}) in sostituzione di {old.name}"
        if copied:
            msg += f", copiati {copied} badge autorizzati"
        return self._result(step, True, msg, {
            'punto_accesso_id': punto_accesso.id,
            'ca_lettore_id': lettore.id,
            'tag_copiati': copied,
        })

    def step_set_access_point(self, body):
        """4.i - Dati del nuovo punto accesso (codice GRUM se stamping)."""
        self._require(states=['grouped'], operation='install')
        step = 'set_access_point'
        reader_name = (body.get('reader_name') or "").strip()
        direction = body.get('direction')
        if not reader_name:
            raise UserError(("campo reader_name obbligatorio"))
        if direction not in ('in', 'out'):
            raise UserError(("campo direction obbligatorio: 'in' o 'out'"))
        grum = self._get_int(
            body, 'codice_lettore_grum', required=self.typology == 'stamping') or 0
        if grum:
            if not 20 <= grum <= 999:
                raise UserError(("Il codice lettore GRUM deve essere tra 20 e 999"))
            used = self.env['ca.punto_accesso'].search(
                [('codice_lettore_grum', '=', grum)], limit=1)
            if used:
                raise UserError((
                    f"Codice GRUM {grum} gia' usato dal punto accesso {used.name}"))
        persona_id = self._get_int(body, 'ca_persona_id', required=False)
        if persona_id:
            self._browse_existing('ca.persona', persona_id, "Persona")

        self.write({
            'reader_name': reader_name,
            'direction': direction,
            'codice_lettore_grum': grum,
            'ca_persona_id': persona_id,
            'access_point_data_set': True,
        })
        return self._result(step, True, f"Dati punto accesso salvati: {reader_name}")

    def _find_or_create_spazio(self, body):
        spazio_id = self._get_int(body, 'ca_spazio_id', required=False)
        if spazio_id:
            return self._browse_existing('ca.spazio', spazio_id, "Posizione"), False
        name = (body.get('name') or "").strip()
        if not name:
            raise UserError(("passare ca_spazio_id oppure name + ente_azienda_id"))
        ente = self._browse_existing(
            'ca.ente_azienda', self._get_int(body, 'ente_azienda_id'), "Sede")
        codice = (body.get('codice_locale') or "").strip()
        spazio = self.env['ca.spazio'].search([
            ('name', '=', name), ('ente_azienda_id', '=', ente.id)], limit=1)
        codice_locale = False
        if codice:
            codice_model = self.env['ca.codice_locale']
            codice_locale = codice_model.search([('name', '=', codice)], limit=1) \
                or codice_model.create({'name': codice})
        if spazio:
            if codice_locale and not spazio.codice_locale_id:
                spazio.codice_locale_id = codice_locale.id
            return spazio, False
        tipo = self._browse_existing(
            'ca.tipo_spazio', self._get_int(body, 'tipo_spazio_id'), "Tipo spazio")
        spazio = self.env['ca.spazio'].create({
            'name': name,
            'ente_azienda_id': ente.id,
            'tipo_spazio_id': tipo.id,
            'codice_locale_id': codice_locale.id if codice_locale else False,
        })
        return spazio, True

    def step_set_position(self, body):
        """5.i - Posizione (codice posizione e sede), creata se non esiste;
        crea il lettore e il punto accesso (disabilitato)."""
        self._require(states=['grouped'], operation='install')
        if not self.access_point_data_set:
            raise UserError(("Prima il passo set_access_point"))
        step = 'set_position'
        spazio, created = self._find_or_create_spazio(body)
        lettore = self.env['ca.lettore'].create({
            'name': self.reader_name,
            'reader_ip': self.reader_ip,
            'direction': self.direction,
        })
        punto_accesso = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': spazio.id,
            'ca_lettore_id': lettore.id,
            'ca_category': self.ca_category_id.id,
            'typology': self.typology,
            'ca_persona_id': self.ca_persona_id.id,
            'codice_lettore_grum': self.codice_lettore_grum or 0,
            'date_start': fields.Date.context_today(self),
            'enable_sync': False,
        })
        self.write({
            'ca_spazio_id': spazio.id,
            'ca_lettore_id': lettore.id,
            'punto_accesso_id': punto_accesso.id,
            'state': 'configured',
        })
        return self._result(
            step, True,
            f"Posizione {'creata' if created else 'trovata'}: {spazio.name}; "
            f"creato punto accesso {punto_accesso.name}",
            {'ca_spazio_id': spazio.id, 'spazio_creato': created,
             'punto_accesso_id': punto_accesso.id, 'ca_lettore_id': lettore.id})

    def step_activate(self, body):
        """6 - Attiva il punto accesso; per stamping collega tutti i badge
        validi (li scrivera' il cron di sync)."""
        self._require(states=['configured'])
        step = 'activate'
        punto_accesso = self.punto_accesso_id
        report = self._checker().run_for_punto_accesso(punto_accesso)
        if not report['ok']:
            return self._result(
                step, False,
                "Lettore non raggiungibile, non attivo: " + "; ".join(report['messages']),
                {'check': report})

        punto_accesso.enable_sync = True
        punto_accesso.load_reader()
        if self.typology == 'stamping':
            punto_accesso.check_and_attach()
        else:
            self.env['ca.lettore_persona'].elabora_persone(punto_accesso.ca_lettore_id)
        tags = len(self._ap_tag_codes(punto_accesso))
        self.write({'activated_at': fields.Datetime.now(), 'state': 'active'})
        wait = self._stamping_wait_seconds() if self.typology == 'stamping' else SYNC_RETRY_SECONDS
        return self._result(
            step, True,
            f"Punto accesso {punto_accesso.name} attivo, {tags} badge da scrivere: "
            f"verificare tra {wait // 60} min",
            {'check': report, 'tag_count': tags}, retry_after=wait)

    def _stamping_wait_seconds(self):
        minutes = int(self.env['ir.config_parameter'].sudo().get_param(
            'provisioning_lettore.stamping_wait_minutes', 10))
        return minutes * 60

    def _reference_stamping_point(self):
        """Punto stamping di confronto per il conteggio badge: il vecchio in
        sostituzione, altrimenti un punto stamping attivo (stesso gruppo se
        possibile)."""
        if self.old_punto_accesso_id:
            return self.old_punto_accesso_id
        domain = [
            ('typology', '=', 'stamping'),
            ('enable_sync', '=', True),
            ('system_error', '=', False),
            ('id', '!=', self.punto_accesso_id.id),
        ]
        model = self.env['ca.punto_accesso']
        return model.search(domain + [('ca_category', '=', self.ca_category_id.id)],
                            limit=1) or model.search(domain, limit=1)

    def _sync_errors(self):
        logs = self.env['ca.log_integrazione_lettori'].sudo().search([
            ('ca_lettore_id', '=', self.ca_lettore_id.id),
            ('datetime', '>=', self.activated_at),
        ], order='id desc', limit=5)
        return [f"{log.activity_code}: {log.log_error}" for log in logs]

    def _after_verify_state(self):
        if self.operation == 'replace':
            return 'verified'
        return 'ip_change' if self.setup_ip else 'done'

    def step_verify(self, body):
        """7 / 7.1.s - Stamping: dopo l'attesa, sync eseguito e stessi badge
        del punto di riferimento. Laboratorio in sostituzione: stessi utenti
        autorizzati del vecchio punto accesso."""
        self._require(states=['active'])
        step = 'verify'
        punto_accesso = self.punto_accesso_id
        data = {}

        if self.typology == 'stamping':
            ready_at = self.activated_at + timedelta(seconds=self._stamping_wait_seconds())
            remaining = int((ready_at - fields.Datetime.now()).total_seconds())
            if remaining > 0:
                return self._result(
                    step, False,
                    f"Attendere ancora {remaining // 60 + 1} min per il popolamento",
                    retry_after=remaining)

        report = self._checker().run_for_punto_accesso(punto_accesso)
        data['check'] = report
        if not report['ok']:
            return self._result(
                step, False, "Lettore non raggiungibile: " + "; ".join(report['messages']),
                data, retry_after=SYNC_RETRY_SECONDS)

        if punto_accesso.remote_update:
            errors = self._sync_errors()
            data['sync_errors'] = errors
            msg = "Badge non ancora scritti sul lettore (sync in attesa)"
            if errors:
                msg += ": " + errors[0]
            return self._result(step, False, msg, data, retry_after=SYNC_RETRY_SECONDS)

        new_codes = self._ap_tag_codes(punto_accesso)
        data['tag_count'] = len(new_codes)
        if self.typology == 'stamping':
            reference = self._reference_stamping_point()
            if reference:
                ref_codes = self._ap_tag_codes(reference)
                missing = sorted(ref_codes - new_codes)
                extra = sorted(new_codes - ref_codes)
                data.update({
                    'reference_punto_accesso': reference.name,
                    'reference_tag_count': len(ref_codes),
                    'missing_tags': missing[:MAX_LISTED_DIFF],
                    'extra_tags': extra[:MAX_LISTED_DIFF],
                })
                if len(new_codes) != len(ref_codes):
                    return self._result(
                        step, False,
                        f"Badge sul nuovo lettore: {len(new_codes)}, su {reference.name}: "
                        f"{len(ref_codes)} (mancanti {len(missing)}, in piu' {len(extra)})",
                        data)
            else:
                data['warning'] = "Nessun punto stamping di riferimento: conteggio non confrontato"
        elif self.old_punto_accesso_id:
            old_persons = self._ap_persons(self.old_punto_accesso_id)
            new_persons = self._ap_persons(punto_accesso)
            persone = self.env['ca.persona']
            missing = persone.browse(sorted(old_persons - new_persons))
            extra = persone.browse(sorted(new_persons - old_persons))
            data.update({
                'persons_old': len(old_persons),
                'persons_new': len(new_persons),
                'missing_persons': missing[:MAX_LISTED_DIFF].mapped('display_name'),
                'extra_persons': extra[:MAX_LISTED_DIFF].mapped('display_name'),
            })
            if old_persons != new_persons:
                return self._result(
                    step, False,
                    f"Utenti autorizzati diversi: vecchio {len(old_persons)}, "
                    f"nuovo {len(new_persons)} (mancanti {len(missing)}, in piu' {len(extra)})",
                    data)

        self.state = self._after_verify_state()
        msg = f"Verifica ok: {len(new_codes)} badge sul lettore"
        if self.state == 'ip_change':
            msg += f". {self._ip_change_message()}"
        return self._result(step, True, msg, data)

    def _ip_change_message(self):
        if self.final_ip:
            return (f"Impostare sul dispositivo l'IP definitivo {self.final_ip}, "
                    "poi eseguire final_check")
        return "Impostare sul dispositivo l'IP definitivo, poi eseguire final_check con final_ip"

    def step_disable_old(self, body):
        """8.s - Disabilita il vecchio punto accesso e il suo lettore; il
        nuovo lettore prende il nome del vecchio."""
        self._require(states=['verified'], operation='replace')
        step = 'disable_old'
        old = self.old_punto_accesso_id
        old_lettore = self.old_lettore_id
        old.write({'enable_sync': False, 'active': False})
        old_lettore.active = False
        lettore = self.ca_lettore_id
        if lettore.name.endswith(REPLACE_SUFFIX):
            lettore.name = old_lettore.name
            self.punto_accesso_id._compute_name()
        self.state = 'ip_change' if self.setup_ip else 'done'
        msg = f"Disabilitato {old.name}; nuovo lettore rinominato {lettore.name}"
        if self.state == 'ip_change':
            msg += f". {self._ip_change_message()}"
        return self._result(step, True, msg)

    def step_final_check(self, body):
        """9 / 10 - Dopo il cambio IP sul dispositivo: check sull'IP
        definitivo e aggiornamento del lettore."""
        self._require(states=['ip_change'])
        step = 'final_check'
        ip = (body.get('final_ip') or self.final_ip or "").strip()
        if not ip:
            raise UserError(("campo final_ip obbligatorio"))
        if not self._checker().valid_ip(ip):
            raise UserError((f"final_ip non valido: {ip}"))
        exclude = [self.ca_lettore_id.id]
        if self.old_lettore_id:
            exclude.append(self.old_lettore_id.id)
        owners = self._checker().find_ip_owners(ip, exclude_lettore_ids=exclude)
        if owners:
            names = ", ".join(o['lettore'] for o in owners)
            return self._result(
                step, False, f"IP {ip} gia' usato da: {names}", {'duplicate': owners})

        report = self._checker().run(
            ip, ente_azienda=self.punto_accesso_id.ente_azienda_id,
            tz=self.punto_accesso_id.tz)
        if not report['ok']:
            return self._result(
                step, False,
                f"Il dispositivo non risponde su {ip}: verificare il cambio IP e riprovare. "
                + "; ".join(report['messages']),
                {'check': report}, retry_after=SYNC_RETRY_SECONDS)

        self.ca_lettore_id.reader_ip = ip
        self.punto_accesso_id.load_reader()
        self.write({'final_ip': ip, 'state': 'done'})
        return self._result(
            step, True,
            f"Procedura completata: {self.punto_accesso_id.name} su {ip}",
            {'check': report})

    def step_cancel(self, body):
        self._require(states=[s for s, _label in STATES if s not in ('done', 'cancelled')])
        self.state = 'cancelled'
        created = []
        if self.punto_accesso_id:
            created.append(f"punto accesso {self.punto_accesso_id.name}")
        if self.ca_lettore_id:
            created.append(f"lettore {self.ca_lettore_id.name}")
        msg = "Procedura annullata"
        if created:
            msg += "; record creati da sistemare a mano: " + ", ".join(created)
        return self._result('cancel', True, msg)
