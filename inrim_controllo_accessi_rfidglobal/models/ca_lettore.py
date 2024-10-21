from odoo import models

info_path = '/info'
status_path = '/status'
read_events_path = '/read-events'
add_tags_path = '/add-tags'
update_clock_path = '/update-clock'


class CaLettore(models.Model):
    _inherit = 'ca.lettore'

    def remote_device_request(self, url: str, headers: dict, body: dict):
        try:
            response = requests.post(
                url, headers=headers, json=body, verify=False)
            if response.status_code == 200:
                data = read_events_request.json()
                return data
            else:
                logger.info(
                    f"{read_events_url}, Status Code: {read_events_request.status_code}")
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f'Error: {e}')
            return False

    def remote_device_info(self, url, headers):
        ...

    def remote_device_status(self, base_url, headers):
        try:
            req_url = f'{base_url}{status_path}'
            body = {
                'device': self.reader_ip
            }
            data = self.remote_device_request(req_url, headers, body)
            punto_accesso_id = self.punto_accesso_ids[0]
            if not data:
                return False

            if punto_accesso_id:
                vals = {}
                vals_punto_accesso = {}
                if 'status' in data:
                    if data.get('status') == True:
                        vals['system_error'] = False
                    else:
                        vals['system_error'] = True
                if 'diagnostic' in data:
                    if 'event_cnt' in data['diagnostic']:
                        vals['available_events'] = data['diagnostic']['event_cnt']
                        vals_punto_accesso['events_to_read_num'] = data['diagnostic'][
                                                                       'event_cnt'] + punto_accesso_id.events_to_read_num
                if vals:
                    punto_accesso_id.ca_lettore_id.write(vals)
                if vals_punto_accesso:
                    punto_accesso_id.write(vals_punto_accesso)
                return True
            else:
                logger.info(f'{status_path}, ID Dispositivo non trovato {device}')
                return False
        except Exception as e:
            self.env.cr.rollback()
            logger.info(f"{status_path}, Error: {e}")
            logger.info(e)
            return False
