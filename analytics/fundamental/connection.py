#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd
import requests


class Connection():

    def __init__(self):
        super(Connection, self).__init__()

    @staticmethod
    def request_indicators():
        TICKERS_URL = "http://fundamentus.com.br/resultado.php"
        response = requests.post(url=TICKERS_URL)
        table = pd.read_html(response.text)[0]
        return table

    @staticmethod
    def request_market_data(initial_date="01/01/2019"):  # dd/mm/YYYY
        URL = "https://br.investing.com/instruments/HistoricalDataAjax"
        HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

        # Request
        data = {"st_date": initial_date,
                "curr_id": "941612",
                "end_date": "14/04/2030",
                "interval_sec": "Daily"}
        response = requests.post(URL, data, headers=HEADERS)
        table = pd.read_html(response.text)[0]
        table = table.set_index("Data")
        table = table[["Último"]]

        return table
