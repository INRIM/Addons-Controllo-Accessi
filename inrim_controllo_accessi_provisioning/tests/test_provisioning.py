from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, HttpCase, new_test_user

from .common import GatewayMixin

NEW_IP = "10.99.0.10"
FINAL_IP = "10.99.0.11"


def _tech_user(env, login):
    user = new_test_user(
        env, login=login, password=f"{login}-pwd",
        groups="base.group_user,controllo_accessi.ca_tech",
    )
    user.api_enabled = True
    return user


@tagged("post_install", "-at_install", "inrim")
class TestProvisioningLettore(GatewayMixin, TransactionCase):

    def setUp(self):
        super().setUp()
        self.setup_gateway(self.env)
        self.tech = _tech_user(self.env, "prov_tech")
        self.tenv = self.env(user=self.tech)
        self.Prov = self.tenv['ca.provisioning_lettore']
        self.ente = self.env.ref('inrim_anagrafiche.inrim_demo_ca_ente_azienda_1')
        self.tipo_locale = self.env.ref('inrim_anagrafiche.tipo_spazio_locale')
        self.portineria = self.env.ref(
            'controllo_accessi_inrim_app.punto_accesso_category_portineria_cacce')
        # Badge valido consegnato (to_give_back): i dati demo hanno solo
        # assegnazioni future, e lo stamping collega solo badge consegnati
        self.tag = self.env.ref('inrim_anagrafiche.inrim_demo_ca_tag_3')
        self.tag_persona = self.env['ca.tag_persona'].create({
            'ca_persona_id': self.env.ref('inrim_anagrafiche.inrim_demo_ca_persona_1').id,
            'ca_tag_id': self.tag.id,
            'date_start': fields.Datetime.now() - timedelta(days=1),
            'date_end': fields.Datetime.now() + timedelta(days=30),
        })
        self.assertEqual(self.tag_persona.state, 'to_give_back')

    # -- helpers ---------------------------------------------------------

    def _step(self, prov, step, body=None):
        return prov.run_step(step, body or {})

    def _elapse_wait(self, prov):
        prov.sudo().activated_at = fields.Datetime.now() - timedelta(minutes=11)

    def _run_sync_cron(self, prov):
        """Quello che fa il cron 'Read Data and Update Tags' sul nuovo punto."""
        prov.punto_accesso_id.sudo().update_reader_tags()

    def _start_checked(self, operation, typology, setup_ip, **extra):
        prov = self.Prov.start({'operation': operation, 'typology': typology})
        self.online_ips.add(NEW_IP)
        res = self._step(prov, 'check_ip', dict(ip=NEW_IP, setup_ip=setup_ip, **extra))
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(prov.state, 'checked')
        return prov

    def _stamping_reference(self, punto):
        """Allinea il punto di riferimento ai soli badge validi correnti, come
        li calcola stamping_attach (i dati demo ne hanno altri)."""
        punto = punto.sudo()
        punto.ca_tag_lettore_ids.write({'active': False})
        punto.check_and_attach()
        punto.remote_update = False

    def _lab_point(self):
        category = self.env['ca.punto_accesso_category'].create({'name': 'LAB PROV TEST'})
        lettore = self.env['ca.lettore'].create({
            'name': 'Lettore Lab', 'reader_ip': '10.98.0.1', 'direction': 'in'})
        punto = self.env['ca.punto_accesso'].create({
            'ca_spazio_id': self.env.ref('inrim_anagrafiche.ca_spazio_1p003').id,
            'ca_lettore_id': lettore.id,
            'ca_category': category.id,
            'typology': 'local_access',
            'date_start': fields.Date.today(),
        })
        self.assertTrue(punto.local_access_attach(self.tag), "badge non collegabile")
        punto.remote_update = False
        return category, punto

    # -- check generico --------------------------------------------------

    def test_check_report(self):
        checker = self.tenv['ca.reader_check']
        report = checker.run(NEW_IP)
        self.assertFalse(report['ok'])
        self.assertTrue(report['info']['reachable'])
        self.assertFalse(report['info']['status'])

        self.online_ips.add(NEW_IP)
        report = checker.run(NEW_IP)
        self.assertTrue(report['ok'], report['messages'])
        self.assertEqual(report['info']['device_id'], '29335616')
        self.assertEqual(report['status']['event_tab_size'], 3268)
        self.assertIsNotNone(report['status']['clock_drift_seconds'])

        self.assertFalse(checker.run("not-an-ip")['ok'])

        self.env['ir.config_parameter'].sudo().set_param('service_reader.url', "In base al sistema")
        report = checker.run(NEW_IP)
        self.assertFalse(report['ok'])
        self.assertIn("Gateway lettori non configurato", report['messages'][0])

    def test_check_punto_accesso(self):
        punto = self.env.ref('inrim_controllo_accessi.ca_punto_accesso_1p001')
        self.online_ips.add(punto.ca_lettore_id.reader_ip)
        report = self.tenv['ca.reader_check'].run_for_punto_accesso(punto)
        self.assertTrue(report['ok'], report['messages'])
        self.assertEqual(report['punto_accesso']['id'], punto.id)

    # -- passo 2 ---------------------------------------------------------

    def test_check_ip_duplicate_blocks(self):
        prov = self.Prov.start({'operation': 'install', 'typology': 'stamping'})
        used_ip = self.env.ref('inrim_anagrafiche.inrim_demo_ca_lettore_1').reader_ip
        self.online_ips.add(used_ip)
        res = self._step(prov, 'check_ip', {'ip': used_ip, 'setup_ip': 'N'})
        self.assertFalse(res['ok'])
        self.assertIn("gia' usato", res['message'])
        self.assertEqual(prov.state, 'draft')

    def test_check_ip_archived_duplicate_blocks(self):
        lettore = self.env['ca.lettore'].create({
            'name': 'Vecchio', 'reader_ip': NEW_IP, 'direction': 'in'})
        lettore.active = False
        prov = self.Prov.start({'operation': 'install', 'typology': 'stamping'})
        self.online_ips.add(NEW_IP)
        res = self._step(prov, 'check_ip', {'ip': NEW_IP, 'setup_ip': 'N'})
        self.assertFalse(res['ok'])
        self.assertIn("archiviato", res['message'])

    def test_check_ip_offline_blocks(self):
        prov = self.Prov.start({'operation': 'install', 'typology': 'stamping'})
        res = self._step(prov, 'check_ip', {'ip': NEW_IP, 'setup_ip': 'N'})
        self.assertFalse(res['ok'])
        self.assertIn("non leggibile", res['message'])
        self.assertEqual(prov.state, 'draft')
        self.assertEqual(len(prov.log_ids), 1)

    def test_check_ip_requires_setup_flag(self):
        prov = self.Prov.start({'operation': 'install', 'typology': 'stamping'})
        with self.assertRaises(UserError):
            self._step(prov, 'check_ip', {'ip': NEW_IP})

    def test_wrong_step_order(self):
        prov = self.Prov.start({'operation': 'install', 'typology': 'stamping'})
        with self.assertRaises(UserError):
            self._step(prov, 'activate')
        with self.assertRaises(UserError):
            self._step(prov, 'unknown')

    # -- installazione ---------------------------------------------------

    def test_install_stamping_with_setup_ip(self):
        prov = self._start_checked('install', 'stamping', 'Y', final_ip=FINAL_IP)
        self.assertTrue(prov.setup_ip)

        # 3.1.i nuovo gruppo
        res = self._step(prov, 'set_group', {'new_category': {'name': 'Ingresso Nuovo', 'code': 'IN'}})
        self.assertTrue(res['ok'], res['message'])
        self.assertTrue(res['data']['created'])
        self.assertEqual(prov.next_step, 'set_access_point')

        # 4.i grum obbligatorio per stamping, e nel range
        with self.assertRaises(UserError):
            self._step(prov, 'set_access_point', {'reader_name': 'R1', 'direction': 'in'})
        with self.assertRaises(UserError):
            self._step(prov, 'set_access_point',
                       {'reader_name': 'R1', 'direction': 'in', 'codice_lettore_grum': 5})
        with self.assertRaises(UserError):  # gia' usato da 1p001
            self._step(prov, 'set_access_point',
                       {'reader_name': 'R1', 'direction': 'in', 'codice_lettore_grum': 20})
        res = self._step(prov, 'set_access_point',
                         {'reader_name': 'Lettore Nuovo', 'direction': 'in',
                          'codice_lettore_grum': 900})
        self.assertTrue(res['ok'])
        self.assertEqual(prov.next_step, 'set_position')

        # 5.i posizione nuova, con codice posizione
        res = self._step(prov, 'set_position', {
            'name': 'PROV-TEST-1', 'ente_azienda_id': self.ente.id,
            'tipo_spazio_id': self.tipo_locale.id, 'codice_locale': 'CL-PROV-1'})
        self.assertTrue(res['ok'], res['message'])
        self.assertTrue(res['data']['spazio_creato'])
        punto = prov.punto_accesso_id
        self.assertEqual(punto.ca_spazio_id.codice_locale_id.name, 'CL-PROV-1')
        self.assertEqual(punto.codice_lettore_grum, 900)
        self.assertEqual(punto.ca_lettore_id.reader_ip, NEW_IP)
        self.assertFalse(punto.enable_sync)
        self.assertEqual(prov.state, 'configured')

        # 6 attivazione
        res = self._step(prov, 'activate')
        self.assertTrue(res['ok'], res['message'])
        self.assertTrue(punto.enable_sync)
        self.assertTrue(punto.remote_update)
        self.assertGreater(res['data']['tag_count'], 0)
        self.assertEqual(res['retry_after'], 600)

        # 7 troppo presto, poi sync non ancora fatto, poi ok
        res = self._step(prov, 'verify')
        self.assertFalse(res['ok'])
        self.assertGreater(res['retry_after'], 0)
        self._elapse_wait(prov)
        res = self._step(prov, 'verify')
        self.assertFalse(res['ok'])
        self.assertIn("sync in attesa", res['message'])
        self._run_sync_cron(prov)
        self.assertFalse(punto.remote_update)
        res = self._step(prov, 'verify')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(prov.state, 'ip_change')
        self.assertIn(FINAL_IP, res['message'])

        # 9/10 cambio IP: dispositivo non ancora sul nuovo IP, poi si'
        res = self._step(prov, 'final_check')
        self.assertFalse(res['ok'])
        self.assertEqual(prov.state, 'ip_change')
        self.online_ips.add(FINAL_IP)
        res = self._step(prov, 'final_check')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(prov.state, 'done')
        self.assertEqual(prov.ca_lettore_id.reader_ip, FINAL_IP)

    def test_install_local_access_existing_position(self):
        prov = self._start_checked('install', 'local_access', 'N')
        self._step(prov, 'set_group', {'ca_category_id': self.portineria.id})
        self._step(prov, 'set_access_point', {'reader_name': 'Lab Nuovo', 'direction': 'out'})
        spazio = self.env.ref('inrim_anagrafiche.ca_spazio_1p004')
        res = self._step(prov, 'set_position', {'name': spazio.name, 'ente_azienda_id': spazio.ente_azienda_id.id})
        self.assertFalse(res['data']['spazio_creato'])
        self.assertEqual(prov.ca_spazio_id, spazio)
        self.assertTrue(self._step(prov, 'activate')['ok'])
        res = self._step(prov, 'verify')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(prov.state, 'done')

    def test_new_category_only_for_install(self):
        prov = self._start_checked('replace', 'stamping', 'N')
        with self.assertRaises(UserError):
            self._step(prov, 'set_group', {'new_category': {'name': 'Nuovo'}})

    # -- sostituzione ----------------------------------------------------

    def test_replace_stamping(self):
        old = self.env.ref('inrim_controllo_accessi.ca_punto_accesso_1p001')
        old_lettore = old.ca_lettore_id
        old_ip = old_lettore.reader_ip
        self._stamping_reference(old)

        prov = self._start_checked('replace', 'stamping', 'Y')
        res = self._step(prov, 'set_group', {'ca_category_id': self.portineria.id})
        self.assertTrue(res['ok'], res['message'])
        options = prov.get_options()
        self.assertIn(old.id, [p['id'] for p in options['punto_accesso']])

        res = self._step(prov, 'set_replace', {'old_punto_accesso_id': old.id})
        self.assertTrue(res['ok'], res['message'])
        punto = prov.punto_accesso_id
        self.assertEqual(punto.ca_lettore_id.name, f"{old_lettore.name}.replace")
        self.assertEqual(punto.codice_lettore_grum, old.codice_lettore_grum)
        self.assertEqual(punto.ca_spazio_id, old.ca_spazio_id)
        self.assertEqual(prov.final_ip, old_ip)

        self.assertTrue(self._step(prov, 'activate')['ok'])
        self._elapse_wait(prov)
        self._run_sync_cron(prov)
        res = self._step(prov, 'verify')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(res['data']['tag_count'], res['data']['reference_tag_count'])
        self.assertEqual(prov.state, 'verified')

        # 8 vecchio disabilitato, nuovo rinominato
        res = self._step(prov, 'disable_old')
        self.assertTrue(res['ok'])
        self.assertFalse(old.active)
        self.assertFalse(old.enable_sync)
        self.assertFalse(old_lettore.active)
        self.assertEqual(punto.ca_lettore_id.name, old_lettore.name)
        self.assertNotIn(".replace", punto.name)
        self.assertEqual(prov.state, 'ip_change')

        # 9/10 il nuovo prende l'IP del vecchio
        self.online_ips.add(old_ip)
        res = self._step(prov, 'final_check')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(punto.ca_lettore_id.reader_ip, old_ip)
        self.assertEqual(prov.state, 'done')

    def test_replace_stamping_tag_mismatch(self):
        old = self.env.ref('inrim_controllo_accessi.ca_punto_accesso_1p001')
        self._stamping_reference(old)
        prov = self._start_checked('replace', 'stamping', 'N')
        self._step(prov, 'set_group', {'ca_category_id': self.portineria.id})
        self._step(prov, 'set_replace', {'old_punto_accesso_id': old.id})
        self._step(prov, 'activate')
        prov.punto_accesso_id.sudo().ca_tag_lettore_ids[:1].detach()
        self._elapse_wait(prov)
        self._run_sync_cron(prov)
        res = self._step(prov, 'verify')
        self.assertFalse(res['ok'])
        self.assertIn("Badge sul nuovo lettore", res['message'])
        self.assertEqual(len(res['data']['missing_tags']), 1)
        self.assertEqual(prov.state, 'active')

    def test_replace_wrong_access_point(self):
        category, lab = self._lab_point()
        prov = self._start_checked('replace', 'stamping', 'N')
        self._step(prov, 'set_group', {'ca_category_id': self.portineria.id})
        with self.assertRaises(UserError):
            self._step(prov, 'set_replace', {'old_punto_accesso_id': lab.id})

    def test_replace_local_access(self):
        category, old = self._lab_point()
        old_persons = old.ca_tag_lettore_persona_view.mapped('ca_persona_id')
        self.assertTrue(old_persons)

        prov = self._start_checked('replace', 'local_access', 'N')
        self._step(prov, 'set_group', {'ca_category_id': category.id})
        res = self._step(prov, 'set_replace', {'old_punto_accesso_id': old.id})
        self.assertEqual(res['data']['tag_copiati'], 1)
        self.assertTrue(self._step(prov, 'activate')['ok'])
        self._run_sync_cron(prov)
        res = self._step(prov, 'verify')
        self.assertTrue(res['ok'], res['message'])
        self.assertEqual(res['data']['persons_new'], len(old_persons))

        res = self._step(prov, 'disable_old')
        self.assertTrue(res['ok'])
        self.assertEqual(prov.state, 'done')
        self.assertEqual(prov.ca_lettore_id.reader_ip, NEW_IP)
        self.assertEqual(
            prov.punto_accesso_id.ca_tag_lettore_persona_view.mapped('ca_persona_id'),
            old_persons)

    def test_replace_local_access_users_mismatch(self):
        category, old = self._lab_point()
        prov = self._start_checked('replace', 'local_access', 'N')
        self._step(prov, 'set_group', {'ca_category_id': category.id})
        self._step(prov, 'set_replace', {'old_punto_accesso_id': old.id})
        self._step(prov, 'activate')
        self._run_sync_cron(prov)
        prov.punto_accesso_id.sudo().ca_tag_lettore_persona_view.write({'state': 'expired'})
        res = self._step(prov, 'verify')
        self.assertFalse(res['ok'])
        self.assertIn("Utenti autorizzati diversi", res['message'])

    def test_cancel(self):
        prov = self._start_checked('install', 'stamping', 'N')
        res = self._step(prov, 'cancel')
        self.assertTrue(res['ok'])
        self.assertEqual(prov.state, 'cancelled')
        with self.assertRaises(UserError):
            self._step(prov, 'cancel')


@tagged("post_install", "-at_install", "inrim")
class TestProvisioningLettoreApi(GatewayMixin, HttpCase):

    def setUp(self):
        super().setUp()
        self.setup_gateway(self.env)
        _tech_user(self.env, "prov_api")
        response = self.url_open(
            '/token/authenticate',
            json={"username": "prov_api", "password": "prov_api-pwd"})
        self.headers = {'token': response.json()['token']}

    def _post(self, path, body=None):
        return self.opener.post(
            self.base_url() + path, headers=self.headers, json=body or {})

    def _get(self, path):
        return self.opener.get(self.base_url() + path, headers=self.headers)

    def test_api_flow(self):
        response = self._post('/api/provisioning_lettore',
                              {'operation': 'install', 'typology': 'stamping'})
        self.assertEqual(response.status_code, 200, response.text)
        prov = response.json()
        self.assertEqual(prov['next_step'], 'check_ip')
        base = f"/api/provisioning_lettore/{prov['id']}"

        response = self._get(f"{base}/options")
        self.assertEqual(response.status_code, 200)
        self.assertIn('ente_azienda', response.json())

        # lettore non raggiungibile: 200 con ok False, stato invariato
        response = self._post(f"{base}/check_ip", {'ip': NEW_IP, 'setup_ip': 'N'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(response.json()['record']['state'], 'draft')

        self.online_ips.add(NEW_IP)
        response = self._post(f"{base}/check_ip", {'ip': NEW_IP, 'setup_ip': 'N'})
        self.assertTrue(response.json()['ok'], response.text)
        self.assertEqual(response.json()['record']['next_step'], 'set_group')

        # passo fuori sequenza: 400 JSON
        response = self._post(f"{base}/activate")
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

        response = self._get("/api/provisioning_lettore/999999")
        self.assertEqual(response.status_code, 404)

    def test_api_check(self):
        punto = self.env.ref('inrim_controllo_accessi.ca_punto_accesso_1p001')
        self.online_ips.add(punto.ca_lettore_id.reader_ip)
        response = self._post('/api/provisioning_lettore/check', {'punto_accesso_id': punto.id})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()['ok'])

        response = self._post('/api/provisioning_lettore/check',
                              {'ip': punto.ca_lettore_id.reader_ip})
        self.assertTrue(response.json()['ok'])
        self.assertEqual(len(response.json()['ip_owners']), 1)

    def test_api_requires_token(self):
        response = self.opener.post(
            self.base_url() + '/api/provisioning_lettore', json={})
        self.assertEqual(response.status_code, 401)
