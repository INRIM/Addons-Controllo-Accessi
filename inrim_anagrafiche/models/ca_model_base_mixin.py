import json
import logging
import urllib.parse
from datetime import datetime

import pytz
from odoo import models

logger = logging.getLogger(__name__)


class CaModelBase(models.AbstractModel):
    _name = "ca.model.base.mixin"
    _description = "Control Access Model Base"

    def rest_get_record(self):
        return {
            "id": self.id
        }

    def rest_record_from_body(self, body):
        rec_id = body.get('id', 0)
        if rec_id == 0:
            return False, "No Id key in body"
        return self.browse(int(rec_id)), ""

    def rest_eval_body(self, body, required_lst=None):
        msg = ""
        if required_lst:
            body, msg = self.check_required(
                body, required_lst
            )
        return body, msg

    def rest_put_eval_body(self, body):
        return body, ""

    def rest_get(self, params: dict):
        strparams = urllib.parse.unquote(params.get('domain', '[]'))
        domain: list = json.loads(strparams)
        offset: int = params.get('offset', None)
        limit: int = params.get('limit', None)
        order: str = params.get('order', None)
        res = []
        if not domain:
            domain = []
        records = self.search(
            domain, offset=offset, limit=limit, order=order)
        for record in records:
            res.append(record.rest_get_record())
        return res, ""

    def rest_post(self, body: dict):
        body, msg = self.rest_eval_body(body)
        record = False
        try:
            if body:
                res = self.load(list(body.keys()), [list(body.values())])
                created_ids = res.get("ids")
                if created_ids:
                    record = self.browse(created_ids)
                else:
                    created_msg = res.get("messages", "Error during record creation")
                    return False, created_msg
            return record, msg
        except Exception as e:
            logger.error(f"{msg} Error {e}", exc_info=True)
            return False, f"{msg} Error {e}"

    def rest_put(self, body: dict = None):
        record, msg = self.rest_record_from_body(body)
        if not record:
            return False, msg
        body.pop("id")
        vals, msg = self.rest_put_eval_body(body)
        try:
            if vals:
                vals[".id"] = record.id
                res = self.load(list(vals.keys()), [list(vals.values())])
                created_ids = res.get("ids")
                if created_ids:
                    record = self.browse(created_ids)
                else:
                    created_msg = res.get("messages", "Error during record update")
                    return False, created_msg
                return record, ""
            else:
                return False, msg
        except Exception as e:
            logger.error(f"{msg} Error {e}", exc_info=True)
            return False, f"{msg} Error {e}"

    def rest_delete(self, body: dict = None):
        idrecord = body.get('id', None)
        if not idrecord:
            return False, "No Id key in body"
        record = self.browse(idrecord)
        if not record:
            return False, "No Irecord found"
        record.unlink()
        return True, ""

    def rest_boby_hint(self):
        return {
            "id": type(1)
        }

    def message_body_hint(self, msg):
        return f"""
         message: {msg}
         
         BodyHint: {self.rest_boby_hint()} 
         
        """

    def check_required(self, data: dict, list_required: list):
        for k in list_required:
            if not data.get(k):
                return False, self.message_body_hint(
                    f"campo {k} obbligorio")
        return data, ""

    def get_by_key(self, key: str, value, operator="="):
        return self.search([(key, operator, value)], limit=1)

    def get_by_id(self, id):
        if not isinstance(id, int):
            return False
        return self.browse(id)

    def f_selection(self, fieldname, value):
        name = value
        label = self._fields[fieldname].convert_to_export(value, self)
        return {"name": name, "label": label}

    @classmethod
    def f_to_date(cls, record_o):
        if record_o:
            return datetime.strptime(record_o, '%Y-%m-%d')
        return record_o

    @classmethod
    def f_date(cls, record_o):
        if record_o:
            return record_o.strftime("%Y-%m-%d")
        return record_o

    @classmethod
    def f_datetime(cls, record_o, tz=None):
        if record_o:
            if tz:
                tzo = pytz.timezone(tz)
                dt_naive = datetime.fromisoformat(
                    record_o.strftime("%Y-%m-%d %H:%M:%S"))
                dt_utc = pytz.UTC.localize(dt_naive)
                res = dt_utc.astimezone(tzo).replace(tzinfo=None)
                return res.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                return record_o.strftime("%Y-%m-%dT%H:%M:%S")
        return record_o

    @classmethod
    def f_img(cls, record_o):
        return str(record_o)

    @classmethod
    def f_m2o(cls, record_o, name="name"):
        if record_o:
            return {"name": record_o.id, "label": record_o.display_name}
        else:
            return False

    @classmethod
    def f_o2m(cls, record_o, name="name"):
        if record_o:
            return [{"name": p.id, "label": p.display_name} for p in record_o]
        else:
            return []

    @classmethod
    def f_m2m(cls, record_o, name="name"):
        if record_o:
            return [{"name": p.id, "label": p.display_name} for p in record_o]
        else:
            return []
