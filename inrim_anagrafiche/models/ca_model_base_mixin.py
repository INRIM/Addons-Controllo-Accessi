from datetime import datetime

from odoo import models
import json


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
        domain: list = json.loads(params.get('domain', '[]'))
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
        if body:
            return self.create(body), ""
        else:
            return False, msg

    def rest_put(self, body: dict = None):
        record, msg = self.rest_record_from_body(body)
        if not record:
            return False, msg
        body.pop("id")
        vals, msg = self.rest_put_eval_body(body)
        if vals:
            record.write(vals)
            return record, ""
        else:
            return False, msg

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
        label = dict(self._fields[fieldname].selection).get(value)
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
    def f_img(cls, record_o):
        return str(record_o)

    @classmethod
    def f_o2m(cls, record_o, name="name"):
        return {"name": record_o.id, "label": record_o.display_name}

    @classmethod
    def f_m2m(cls, record_o, name="name"):
        return [{"name": p.id, "label": p.display_name} for p in record_o]
