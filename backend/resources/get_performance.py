#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import numpy as np
from flask_restful import Resource

# Own libraries
from ..common import database


# TODO: Add monthly stats
# TODO: Return initial date of records
class GetPerformance(Resource):
    def get(self):
        filter = {"userId": {"$in": [0, 1]}}
        sort = [("userId", 1)]
        docs = database.find(collection="performances", filter=filter, sort=sort)
        output = {}
        for doc in docs:
            output.update(self._preprocess(doc))
        return output

    def _preprocess(self, doc):
        dictionary = {}
        if doc["userId"] == 0:
            dictionary = self._get_baseline_performance(doc)
        elif doc["userId"] == 1:
            dictionary = self._get_strategy_performance(doc)
        return dictionary

    def _get_baseline_performance(self, doc):
        dictionary = {"IBOV": {
            "profit_in_percentage": doc["profit_in_percentage"],
            "sharpe_ratio": doc["sharpe_ratio"],
            "maximum_drawdown_in_percentage": doc["maximum_drawdown_in_percentage"]
            }
        }
        return dictionary

    def _get_strategy_performance(self, doc):
        dictionary = {"strategy": {
            "profit_in_percentage": doc["profit_in_percentage"],
            "sharpe_ratio": doc["sharpe_ratio"],
            "maximum_drawdown_in_percentage": doc["maximum_drawdown_in_percentage"],
            "total_trades": doc["total_trades"],
            "percentage_of_gain_trades": doc["percentage_of_gain_trades"],
            "percentage_of_loss_trades": doc["percentage_of_loss_trades"],
            "avg_gain_per_trade": doc["avg_gain_per_trade"],
            "avg_loss_per_trade": doc["avg_loss_per_trade"],
            "avg_gain_in_percentage": doc["avg_gain_in_percentage"],
            "avg_loss_in_percentage": doc["avg_loss_in_percentage"]
            }
        }
        for key, value in dictionary["strategy"].items():
            if np.isnan(value):
                dictionary["strategy"][key] = 0.0
        return dictionary
