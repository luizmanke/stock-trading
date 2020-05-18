#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
import requests


class Request():

    def __init__(self):
        super(Request, self).__init__()

    def fundamentals(self):
        TICKERS_URL = "http://fundamentus.com.br/resultado.php"
        response = requests.post(url=TICKERS_URL)
        table = pd.read_html(response.text)[0]
        fundamentals = self._preprocess_fundamentals(table)
        return fundamentals

    @staticmethod
    def _preprocess_fundamentals(table):

        # Rename
        new_table = table.rename(columns={
            "Papel": "ticker",
            "Cotação": "price",
            "P/L": "priceToEarnings",
            "P/VP": "priceToBookValue",
            "PSR": "priceToSalesRatio",
            "Div.Yield": "dividendYield",
            "P/Ativo": "priceToAsset",
            "P/Cap.Giro": "priceToWorkingCapital",
            "P/EBIT": "priceToEbit",
            "P/Ativ Circ.Liq": "priceToNetCurrentAsset",
            "EV/EBIT": "enterpriseValueToEbit",
            "EV/EBITDA": "enterpriseValueToEbitda",
            "Mrg Ebit": "ebitMargin",
            "Mrg. Líq.": "netMargin",
            "Liq. Corr.": "currentLiquidity",
            "ROIC": "returnOnInvestedCapital",
            "ROE": "returnOnEquity",
            "Liq.2meses": "volume",
            "Patrim. Líq": "netEquity",
            "Dív.Brut/ Patrim.": "grossDebtToEquity",
            "Cresc. Rec.5a": "cagr"
            })

        # To float
        new_table = new_table.replace("%", "", regex=True)
        new_table = new_table.replace("\\.", "", regex=True)
        new_table = new_table.replace(",", ".", regex=True)
        tickers = new_table.pop("ticker")
        new_table = new_table.astype(float)
        new_table["ticker"] = tickers

        # Rescale
        COLUMNS = ["price", "priceToEarnings", "priceToBookValue", "priceToWorkingCapital",
                   "priceToEbit", "priceToNetCurrentAsset", "enterpriseValueToEbit",
                   "enterpriseValueToEbitda", "currentLiquidity", "volume", "netEquity",
                   "grossDebtToEquity"]
        for column in COLUMNS:
            new_table[column] = new_table[column] / 100
        for column in ["priceToSalesRatio", "priceToAsset"]:
            new_table[column] = new_table[column] / 1000

        new_table = new_table.drop(["price", "volume"], axis=1)
        new_table = new_table.to_dict(orient="records")
        return new_table

    def quotations(self, initial_date="31/12/2019"):  # dd/mm/YYYY
        URL = "https://br.investing.com/instruments/HistoricalDataAjax"
        HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

        # Get companies
        companies = self._companies()

        # Loop companies
        raw_quotations = {}
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
            raw_quotations[ticker] = table

        # Preprocess
        quotations = self._preprocess_quotations(raw_quotations)

        return quotations

    @staticmethod
    def _companies():
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
            for content in page_contents["hits"]:
                content_data = content["viewData"]
                ticker = content_data["symbol"]
                companies[ticker] = {"id": content["pair_ID"]}

            if len(companies) == page_contents["totalCount"]:
                break

        # Add market
        companies["IBOV"] = {"id": "941612"}

        return companies

    @staticmethod
    def _preprocess_quotations(data):

        # Loop tickers
        output_data = []
        for ticker, new_data in data.items():

            # Create ticker dataframe
            new_data.index = [dt.datetime.strptime(date, "%d.%m.%Y")
                              for date in new_data.index]
            new_data = new_data.rename(columns={
                "Último": "close",
                "Abertura": "open",
                "Máxima": "high",
                "Mínima": "low",
                "Vol.": "volume",
                "Var%": "change"
                })
            new_data = new_data.drop("change", axis=1)

            # Convert to float
            new_data = new_data.replace(",", ".", regex=True)
            new_data = new_data.replace("%", "", regex=True)
            new_data = new_data.replace("-", float("nan"))
            new_data["multiplier"] = 1
            multiplier = new_data.pop("multiplier")
            multiplier = multiplier.where(new_data["volume"].str.find("K") < 0, 1000)
            multiplier = multiplier.where(new_data["volume"].str.find("M") < 0, 1000000)
            multiplier = multiplier.where(new_data["volume"].str.find("B") < 0, 1000000000)
            new_data = new_data.replace("K", "", regex=True)
            new_data = new_data.replace("M", "", regex=True)
            new_data = new_data.replace("B", "", regex=True)
            new_data = new_data.astype(float)

            # Rescale data
            for column in ["close", "open", "high", "low"]:
                new_data[column] = new_data[column] / 100
            new_data["volume"] = new_data["volume"] * multiplier

            # Reorganize
            new_data["ticker"] = ticker
            new_data["occurredAt"] = new_data.index

            new_data = new_data.to_dict(orient="records")
            output_data = output_data + new_data
        return output_data
