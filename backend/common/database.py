#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import os
import ssl
from pymongo import MongoClient


class Database():

    def __init__(self):
        super(Database, self).__init__()
        self._connect()

    def insert(self, items, collection):
        created_at = dt.datetime.utcnow()
        delete_count = 0
        for item in items:
            item["createdAt"] = created_at
            filter_ = {"occurredAt": item["occurredAt"], "ticker": item["ticker"]}
            delete_response = self._connection[collection].delete_many(filter_)
            delete_count += delete_response.deleted_count
        insert_response = self._connection[collection].insert_many(items)
        print(f" > {delete_count} items deleted")
        print(f" > {len(insert_response.inserted_ids)} items inserted")

    def _connect(self):
        url = os.environ.get("MONGODB_URL")
        client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
        self._connection = client["cream"]
