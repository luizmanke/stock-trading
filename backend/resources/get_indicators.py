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
        filter_ = {"occurredAt": last_date}
        fields = {"_id": 0, "ticker": 1, "rate": 1, "trend": 1}
        return database.find(filter_, fields, "indicators")


def _get_last_date():
    connection = database._get_connection()
    fields = {"_id": 0, "occurredAt": 1}
    sort = [("occurredAt", -1)]
    docs = connection["indicators"].find({}, fields, sort=sort).limit(1)
    return docs[0]["occurredAt"]
