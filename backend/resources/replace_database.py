#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta

# Own libraries
from .update_performances import _update_performance
from .utils import get_today_date
from ..common import baseline, database
from ..analytics.strategy import Strategy
from ..analytics.wallet import Wallet


def run():
    print("Replacing...")

    print(" - baseline...")
    _replace_baseline()

    print(" - strategy...")
    _replace_strategy()


def _replace_baseline():
    USER_ID = 0

    # Get data
    fundamentals, quotations = _get_data()

    # Compute wallet
    wallet = {"remainingCash": 100000, "wallet": {}}
    records = []
    for index in sorted(set(fundamentals.index)):
        price = quotations[(quotations.index == index) & (quotations["ticker"] == "IBOV")]
        if not price.empty:
            price = price.loc[index, "close"]
            baseline.update_wallet(wallet, price, index)
            record = baseline.compute_record(wallet)
            record["occurredAt"] = index
            records.append(record)

    # Replace results
    _save_wallet(USER_ID, wallet)
    _save_records(USER_ID, records)
    _update_performance(user_id=0)


def _replace_strategy():
    USER_ID = 1
    fundamentals, quotations = _get_data()
    indicators = _compute_indicators(fundamentals, quotations)
    wallet, records = _compute_strategy(indicators, quotations)
    _save_wallet(USER_ID, wallet)
    _save_records(USER_ID, records)
    _update_performance(USER_ID)


def _compute_indicators(fundamentals, quotations):

    # Loop indexes
    indicators = []
    for index in sorted(set(fundamentals.index)):
        minimum_index = index - relativedelta(months=6)

        # Filter data
        fundamentals_subset = fundamentals[
            (fundamentals.index <= index) & (fundamentals.index > minimum_index)]
        fundamentals_subset = fundamentals_subset.drop_duplicates("ticker", keep="last")
        quotations_subset = quotations[
            (quotations.index <= index) & (quotations.index > minimum_index)]

        # Compute indicators
        indicators_subset = Strategy().get_indicators(fundamentals_subset, quotations_subset)
        for item in indicators_subset:
            item["occurredAt"] = index
        indicators = indicators + indicators_subset

    indicators = pd.DataFrame(indicators).set_index("occurredAt")
    return indicators


def _compute_strategy(indicators, quotations):

    # Loop indexes
    wallet = Wallet(remaining_cash=100000)
    for index in sorted(set(indicators.index)):

        # Update wallet
        quotations_subset = quotations[quotations.index == index]
        quotations_subset = quotations_subset.set_index("ticker")
        quotations_subset = quotations_subset[["close"]].to_dict(orient="index")
        wallet.update_wallet(quotations_subset, index)

        # Update deals
        quotations_subset = quotations[quotations.index <= index]
        quotations_subset = quotations_subset.drop_duplicates(subset=["ticker"], keep="last")
        quotations_subset = quotations_subset.set_index("ticker")
        quotations_subset = quotations_subset[["close"]].to_dict(orient="index")
        indicators_subset = indicators[indicators.index == index]
        indicators_subset = indicators_subset.to_dict(orient="records")
        wallet.compute_deals(quotations_subset, indicators_subset, index)

    records = wallet.records_
    records.index.name = "occurredAt"
    records = records.reset_index()
    records = records.to_dict(orient="records")
    wallet = {"remainingCash": wallet.wallet_.pop("remaining_cash"), "wallet": wallet.wallet_}
    return wallet, records


def _get_data():

    # Fundamentals
    fields = {"ticker": 1, "occurredAt": 1, "cagr": 1,
              "returnOnInvestedCapital": 1, "priceToEarnings": 1}
    sort = [("occurredAt", 1)]
    fundamentals = database.find(collection="fundamentals", projection=fields, sort=sort)
    fundamentals = pd.DataFrame(fundamentals).set_index("occurredAt")

    # Quotations
    fields = {"ticker": 1, "occurredAt": 1, "close": 1, "volume": 1}
    sort = [("occurredAt", 1)]
    quotations = database.find(collection="quotations", projection=fields, sort=sort)
    quotations = pd.DataFrame(quotations).set_index("occurredAt")

    return fundamentals, quotations


def _save_wallet(user_id, wallet):
    wallet["userId"] = user_id
    wallet["occurredAt"] = get_today_date()
    wallet["createdAt"] = dt.datetime.utcnow()

    filter_ = {"userId": {"$eq": user_id}}
    n_deleted = database.delete(filter_, "wallets")
    print(f"   > {n_deleted} wallets deleted")
    n_inserted = database.insert_many([wallet], "wallets")
    print(f"   > {n_inserted} wallets inserted")


def _save_records(user_id, records):
    print(records)

    created_at = dt.datetime.utcnow()
    for record in records:
        record["userId"] = user_id
        record["createdAt"] = created_at

    filter_ = {"userId": {"$eq": user_id}}
    n_deleted = database.delete(filter_, "records")
    print(f"   > {n_deleted} records deleted")
    n_inserted = database.insert_many(records, "records")
    print(f"   > {n_inserted} records inserted")


if __name__ == "__main__":

    # Run
    import dotenv
    dotenv.load_dotenv()
    run()
