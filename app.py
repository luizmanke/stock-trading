#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_restful import Api

# Own libraries
from backend.resources.metadata import update_database

# Set triggers
scheduler = BackgroundScheduler()
scheduler.add_job(
    update_database, trigger="cron", day_of_week="mon-fri", hour=21, timezone="UTC")
scheduler.start()

# Initiate app
app = Flask(__name__)
api = Api(app)


# Test route
@app.route("/", methods=["GET"])
def index():
    return {"message": "Hello world!"}


if __name__ == "__main__":
    app.run(debug=True)
