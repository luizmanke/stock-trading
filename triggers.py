#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from apscheduler.schedulers.background import BackgroundScheduler

# Own libraries
from backend.resources.metadata import update_database


if __name__ == "__main__":

    # Set triggers
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_database, trigger="cron", day_of_week="mon-fri", hour=21, timezone="UTC")
    scheduler.start()
