#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import numpy as np
from flask_restful import Resource

# Own libraries
from ..common import database


class GetPerformances(Resource):
    def get(self):
        filter_ = {"userId": {"$in": [0, 1]}}
        fields = {"_id": 0, "occurredAt": 0, "createdAt": 0}
        sort = [("userId", 1)]
        docs = database.find(
            collection="performances", filter=filter_, projection=fields, sort=sort)
        output = {}
        for doc in docs:
            output.update(self._preprocess(doc))
        return output

    def _preprocess(self, doc):
        dictionary = {}
        if doc["userId"] == 0:
            dictionary.update(self._get_baseline_performance(doc))
        elif doc["userId"] == 1:
            dictionary.update(self._get_strategy_performance(doc))
        return dictionary

    def _get_baseline_performance(self, doc):
        dictionary = self._get_dates(doc)
        doc.pop("userId")
        for key, value in doc.items():
            dictionary[key] = {
                "profit_in_percentage": value["profit_in_percentage"],
                "sharpe_ratio": value["sharpe_ratio"],
                "maximum_drawdown_in_percentage": value["maximum_drawdown_in_percentage"]
            }
        return {"IBOV": dictionary}

    def _get_strategy_performance(self, doc):
        dictionary = self._get_dates(doc)
        doc.pop("userId")
        for key, value in doc.items():
            dictionary[key] = {
                "profit_in_percentage": value["profit_in_percentage"],
                "sharpe_ratio": value["sharpe_ratio"],
                "maximum_drawdown_in_percentage": value["maximum_drawdown_in_percentage"],
                "total_trades": value["total_trades"],
                "percentage_of_gain_trades": value["percentage_of_gain_trades"],
                "percentage_of_loss_trades": value["percentage_of_loss_trades"],
                "avg_gain_per_trade": value["avg_gain_per_trade"],
                "avg_loss_per_trade": value["avg_loss_per_trade"],
                "avg_gain_in_percentage": value["avg_gain_in_percentage"],
                "avg_loss_in_percentage": value["avg_loss_in_percentage"]
            }
            for item, value in dictionary[key].items():
                if np.isnan(value):
                    dictionary[key][item] = 0
        return {"strategy": dictionary}

    @staticmethod
    def _get_dates(doc):
        dictionary = {"initial_date": str(doc.pop("initial_date")),
                      "current_date": str(doc.pop("current_date"))}
        return dictionary
