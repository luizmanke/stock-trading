#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from flask_restful import Resource

# Own libraries
from .utils import get_today_date
from ..common import database


class Run(Resource):
    def get(self):
        last_date = _get_last_date()
        filter = {"occurredAt": last_date}
        fields = {"_id": 0, "ticker": 1, "rank": 1, "trend": 1}
        sort = [("rank", 1)]
        docs = database.find(
            collection="indicators", filter=filter, projection=fields, sort=sort)
        return {"date": last_date.strftime("%Y-%m-%d"), "data": docs}


def _get_last_date():
    fields = {"_id": 0, "occurredAt": 1}
    sort = [("occurredAt", -1)]
    docs = database.find(collection="indicators", projection=fields, sort=sort, limit=1)
    return docs[0]["occurredAt"]
