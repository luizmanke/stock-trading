#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd
import requests


class Connection():

    def __init__(self):
        super(Connection, self).__init__()

    @staticmethod
    def request_companies():
        URL = "https://br.investing.com/stock-screener/Service/SearchStocks"
        HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
        MAX_PAGE_NUMBERS = 100

        # Loop pages
        companies = {}
        data = {"country[]": "32",
                "exchange[]": "47",
                "order[col]": "viewData.symbol",
                "order[dir]": "a"}
        for page_number in range(1, MAX_PAGE_NUMBERS+1):
            data["pn"] = page_number
            response = requests.post(URL, data, headers=HEADERS)
            page_contents = response.json()

            # Loop tickers
            i = 0
            for content in page_contents["hits"]:
                i += 1
                content_data = content["viewData"]
                ticker = content_data["symbol"]
                companies[ticker] = {"name": content_data["name"],
                                     "link": content_data["link"],
                                     "volume": content.get("avg_volume", 0),
                                     "id": content["pair_ID"]}

            if len(companies) == page_contents["totalCount"]:
                break

        # Add market
        companies["IBOV"] = {"name": "IBOV",
                             "link": None,
                             "volume": 1000000000,
                             "id": "941612"}

        return companies

    @staticmethod
    def request_quotations(companies=[], initial_date="31/12/2019"):  # dd/mm/YYYY
        URL = "https://br.investing.com/instruments/HistoricalDataAjax"
        HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

        # Loop companies
        quotations = {}
        data = {"st_date": initial_date,
                "end_date": "01/01/2030",
                "interval_sec": "Daily"}
        for ticker in companies:
            data["curr_id"] = companies[ticker]["id"]
            response = requests.post(URL, data, headers=HEADERS)
            table = pd.read_html(response.text)[0]
            if type(table.loc[0, "Último"]) == str:
                continue

            # Update quotations
            table = table.set_index("Data")
            quotations[ticker] = table

        return quotations
