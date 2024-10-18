import json

from odoo import models


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

    def rest_eval_body(self, body):
        return body, ""

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
        vals, msg = self.rest_eval_body(body)
        if vals:
            return self.create(vals), ""
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

    def get_by_key(self, key: str, value, operator="="):
        return self.search([(key, operator, value)], limit=1)

    def get_by_id(self, id):
        if not isinstance(id, int):
            return False
        return self.browse(id)
