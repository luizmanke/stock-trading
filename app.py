#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from flask import Flask
from flask_restful import Api

# Own libraries
from backend.resources import get_indicators

# Initiate app
app = Flask(__name__)
api = Api(app)

# Routes
api.add_resource(get_indicators.Run, "/get-indicators")

# Test route
@app.route("/", methods=["GET"])
def index():
    return {"message": "Hello world!"}


if __name__ == "__main__":
    app.run(debug=True)
