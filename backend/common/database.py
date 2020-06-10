#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import os
import ssl
from pymongo import MongoClient


def insert_many(items, collection):
    connection = _get_connection()
    created_at = dt.datetime.utcnow()
    for item in items:
        item["createdAt"] = created_at
    insert_response = connection[collection].insert_many(items)
    return len(insert_response.inserted_ids)


def delete_many(items, collection):
    connection = _get_connection()
    delete_count = 0
    for item in items:
        filter_ = {"occurredAt": item["occurredAt"], "ticker": item["ticker"]}
        delete_response = connection[collection].delete_many(filter_)
        delete_count += delete_response.deleted_count
    return delete_count


def delete(item, collection, filter):
    connection = _get_connection()
    delete_count = 0
    delete_response = connection[collection].delete_many(filter)
    delete_count += delete_response.deleted_count
    return delete_count


def find(collection, **kwargs):
    connection = _get_connection()
    docs = connection[collection].find(**kwargs)
    docs = [doc for doc in docs]
    return docs


def aggregate(pipeline, collection):
    connection = _get_connection()
    docs = connection[collection].aggregate(pipeline)
    docs = [doc for doc in docs]
    return docs


def _get_connection():
    url = os.environ.get("MONGODB_URL")
    client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
    return client["cream"]
