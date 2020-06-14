#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: Save monthly performance
# TODO: Create lint and unit tests
# TODO: Change strategy output form dict to dataframe
# TODO: Compute indicators for every stock
# TODO: Make replace_records.py functions reusable
# TODO: Update backtest data using 2011+ data
# TODO: Optimize backtest

# System libraries
from flask import Flask
from flask_restful import Api

# Own libraries
from backend.resources.get_indicators import GetIndicators
from backend.resources.get_performance import GetPerformance

# Initiate app
app = Flask(__name__)
api = Api(app)

# Routes
api.add_resource(GetIndicators, "/get-indicators")
api.add_resource(GetPerformance, "/get-performance")

# Test route
@app.route("/", methods=["GET"])
def index():
    return {"message": "Hello world!"}


if __name__ == "__main__":
    app.run(debug=True)
