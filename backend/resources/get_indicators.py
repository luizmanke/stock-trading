#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from flask_restful import Resource

# Own libraries
from ..common import database


class GetIndicators(Resource):
    def get(self):
        fields = {"_id": 0, "ticker": 1, "rank": 1, "trend": 1, "occurredAt": 1}
        sort = [("rank", 1)]
        docs = database.find(collection="indicators", projection=fields, sort=sort)
        date = docs[0]["occurredAt"]
        for doc in docs:
            del doc["occurredAt"]
        return {"date": date.strftime("%Y-%m-%d"), "data": docs}
