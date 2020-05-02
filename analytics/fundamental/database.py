#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd


class Database():

    def __init__(self):
        super(Database, self).__init__()
        self.data_ = pd.DataFrame()

    def update_indicators(self, index, table):

        # Rename
        table = table.rename(columns={
            "Papel": "ticker", "Cotação": "price", "P/L": "pe",
            "P/VP": "price_book_value", "PSR": "price_sales_ratio",
            "Div.Yield": "annual_dividend_yield", "P/Ativo": "price_asset",
            "P/Cap.Giro": "price_working_capital", "P/EBIT": "price_ebit",
            "P/Ativ Circ.Liq": "price_net_current_asset", "EV/EBIT": "ev_ebit",
            "EV/EBITDA": "ev_ebitda", "Mrg Ebit": "ebit_margin",
            "Mrg. Líq.": "net_margin", "Liq. Corr.": "current_liquidity",
            "ROIC": "roic", "ROE": "roe", "Liq.2meses": "volume",
            "Patrim. Líq": "net_worth", "Dív.Brut/ Patrim.": "gross_debt_equity",
            "Cresc. Rec.5a": "cagr"
        })

        # To float
        table_copy = table.copy()
        table = table.replace("%", "", regex=True)
        table = table.replace("\\.", "", regex=True)
        table = table.replace(",", ".", regex=True)
        tickers = table.pop("ticker")
        table = table.astype(float)
        table["ticker"] = tickers

        # Rescale
        COLUMNS = ["price", "pe", "price_book_value", "price_working_capital",
                   "price_ebit", "price_net_current_asset", "ev_ebit", "ev_ebitda",
                   "current_liquidity", "gross_debt_equity", "volume", "net_worth"]
        for column in COLUMNS:
            table[column] = table[column] / 100
        for column in ["price_sales_ratio", "price_asset"]:
            table[column] = table[column] / 1000

        # Update
        table.index = [index] * table.shape[0]
        data = self.data_[self.data_.index != index]
        self.data_ = pd.concat([data, table])

    def update_market_data(self, index, table):
        data = self.data_
        table = table.rename(columns={"Último": "price"})
        table["ticker"] = "IBOV"
        table.index = pd.to_datetime(table.index)
        data = pd.concat([data, table])
        data.index.name = "date"
        data = data.reset_index(drop=False)
        data = data.drop_duplicates(keep="last")
        data = data.set_index("date")
        data = data.sort_index()
        self.data_ = data
