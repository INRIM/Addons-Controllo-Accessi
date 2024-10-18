from odoo import models


class CaModelBase(models.AbstractModel):
    _name = "ca.model.base"
    _description = "Control Access Model Base"

    def rest_get_record(self):
        return {
            "id": self.id
        }

    def rest_record_from_body(self, body):
        rec_id = body.get('id')
        return self.browse(int(rec_id))


    def rest_eval_body(self, body):
        return {}

    def rest_get(
            self, domain: list = None, offset: int = None,
            limit: int = None, order: str = None, count: bool = None
    ):
        res = []
        if not domain:
            domain = []
        records = self.search(
            domain, offset=offset, limit=limit, order=order, count=count)
        for record in records:
            res.append(record.rest_get_record())



    def rest_post(self, body: dict):
        vals = self.rest_eval_body(body)
        if vals:
            return self.create(vals)
        else:
            return False

    def rest_put(self, body: dict = None):
        record = self.rest_record_from_body(body)
        if not record:
             return False
        body.pop("id")
        vals = self.rest_eval_body(body)
        if vals:
            try:
                record.write(vals)
                return record.rest_get_record()
            except Exception as e:
                return False
        else:
            return False

    def rest_delete(self, id: int = None):
        if not id:
            return False
        self.unlink(id)
        return True
