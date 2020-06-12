#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from flask_restful import Resource

# Own libraries
from ..common import database


class Runs(Resource):
    def get(self):
        filter = {"userId": {"$in": [0, 1]}}
        fields = {"_id": 0, "occurredAt": 0, "createdAt": 0}
        sort = [("userId", 1)]
        docs = database.find(
            collection="performances", filter=filter, projection=fields, sort=sort)
        return docs
