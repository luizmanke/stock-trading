#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import json
import os
import pytest
import requests
from dotenv import load_dotenv

# Own libraries
from ..get_indicators import GetIndicators

# Configurations
load_dotenv()


# def test_get_indicators():
#     docs = GetIndicators().get()
#     _ = dt.datetime.strptime(docs["date"], "%Y-%m-%d")
#     one_data = docs["data"][1]
#     assert len(docs["data"]) > 10
#     KEYS = {"ticker": str, "rank": int, "trend": float}
#     for key, type_ in KEYS.items():
#         assert type(one_data[key]) == type_


@pytest.mark.integration
def test_get_indicators_endpoint():
    app = os.environ.get("HEROKU_APP")
    url = f"http://{app}.herokuapp.com/get-indicators"
    response = requests.get(url)
    docs = json.loads(response.text)
    _ = dt.datetime.strptime(docs["date"], "%Y-%m-%d")
    one_data = docs["data"][1]
    assert len(docs["data"]) > 10
    KEYS = {"ticker": str, "rank": int, "trend": float}
    for key, type_ in KEYS.items():
        assert type(one_data[key]) == type_
