#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import os
import smtplib
from email.message import EmailMessage


def get_today_date():
    UTC = -3
    today_date = dt.datetime.utcnow() + dt.timedelta(hours=UTC)
    today_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return today_date


def send_email(subject, content):
    USERNAME = os.environ.get("GMAIL_USERNAME")
    PASSWORD = os.environ.get("GMAIL_PASSWORD")
    EMAILS = os.environ.get("MONITORING_EMAILS")

    # Connect to email server
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp.login(USERNAME, PASSWORD)

    # Send message
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = USERNAME
    message.set_content(content)
    for email in EMAILS.split(", "):
        if email:
            message["To"] = email
            smtp.send_message(message)

    # Disconnect from server
    smtp.quit()
