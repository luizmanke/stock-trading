#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
import requests


def run(initial_date="31/12/2019"):  # dd/mm/YYYY
    companies = _request_companies()
    raw_quotations = _request_quotations(companies, initial_date)
    quotations = _preprocess(raw_quotations)
    return quotations


def _request_companies():
    MAX_PAGE_NUMBERS = 100
    companies = {"IBOV": {"id": "941612"}}  # Market ID
    for page_number in range(1, MAX_PAGE_NUMBERS+1):
        page_contents = _request_companies_page(page_number)
        _update_companies(companies, page_contents)
        if len(companies)-1 == page_contents["totalCount"]:
            break
    return companies


def _request_companies_page(page_number):
    URL = "https://br.investing.com/stock-screener/Service/SearchStocks"
    HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
    data = {"country[]": "32",
            "exchange[]": "47",
            "order[col]": "viewData.symbol",
            "order[dir]": "a"}
    data["pn"] = page_number
    response = requests.post(URL, data, headers=HEADERS)
    return response.json()


def _update_companies(companies, page_contents):
    for content in page_contents["hits"]:
        content_data = content["viewData"]
        ticker = content_data["symbol"]
        companies[ticker] = {"id": content["pair_ID"]}


def _request_quotations(companies, initial_date):
    quotations = {}
    for ticker in companies:
        id = companies[ticker]["id"]
        ticker_quotations = _request_ticker_quotations(id, initial_date)
        if type(ticker_quotations.loc[0, "Último"]) == str:
            continue
        ticker_quotations = ticker_quotations.set_index("Data")
        quotations[ticker] = ticker_quotations
    return quotations


def _request_ticker_quotations(id, initial_date):
    URL = "https://br.investing.com/instruments/HistoricalDataAjax"
    HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
    data = {"st_date": initial_date,
            "end_date": "01/01/2030",
            "interval_sec": "Daily",
            "curr_id": id}
    response = requests.post(URL, data, headers=HEADERS)
    quotations = pd.read_html(response.text)[0]
    return quotations


def _preprocess(old_quotations):
    new_quotations = []
    for ticker, data in old_quotations.items():
        data = _create_dataframe(data)
        data = _convert_to_float(data)
        _rescale(data)
        new_quotations = new_quotations + _to_list(data, ticker)
    return new_quotations


def _create_dataframe(data):
    data.index = [dt.datetime.strptime(date, "%d.%m.%Y") for date in data.index]
    data = data.rename(columns={
        "Último": "close",
        "Abertura": "open",
        "Máxima": "high",
        "Mínima": "low",
        "Vol.": "volume",
        "Var%": "change"
        })
    data = data.drop("change", axis=1)
    return data


def _convert_to_float(data):
    data = data.replace(",", ".", regex=True)
    data = data.replace("%", "", regex=True)
    data["multiplier"] = 1
    multiplier = data.pop("multiplier")
    multiplier = multiplier.where(data["volume"].str.find("K") < 0, 1000)
    multiplier = multiplier.where(data["volume"].str.find("M") < 0, 1000000)
    multiplier = multiplier.where(data["volume"].str.find("B") < 0, 1000000000)
    data = data.replace("K", "", regex=True)
    data = data.replace("M", "", regex=True)
    data = data.replace("B", "", regex=True)
    data = data.replace("-", float("nan"))
    data = data.astype(float)
    data["volume"] = data["volume"] * multiplier
    return data


def _rescale(data):
    for column in ["close", "open", "high", "low"]:
        data[column] = data[column] / 100


def _to_list(data, ticker):
    data["ticker"] = ticker
    data["occurredAt"] = data.index
    return data.to_dict(orient="records")
