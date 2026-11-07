"""
Central configuration for the Personal Life Performance & Discipline
Automation System.

Nothing sensitive lives in this file. Secrets (bot token, service
account JSON, sheet ID, chat ID) are read from environment variables,
which GitHub Actions injects from repository Secrets at run time.
"""

import os
from zoneinfo import ZoneInfo

# ---- Secrets (never hardcode these) ------------------------------------
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GOOGLE_SERVICE_ACCOUNT_JSON_B64 = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON_B64"]
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]

# ---- Timezone ------------------------------------------------------------
NEPAL_TZ = ZoneInfo("Asia/Kathmandu")

# Must match the cron frequency in .github/workflows/poller.yml.
# This is the window a reminder is considered "due" in, so a run that's
# a couple of minutes late (GitHub Actions makes no exact-time promise)
# still catches it.
POLL_INTERVAL_MINUTES = 5

# ---- Daily routine (confirmed: same schedule every day of the week) ------
# kind controls what the reminder offers beyond the generic
# Completed / Not Completed buttons:
#   "simple"  -> just Completed / Not Completed (+ mandatory reason if not)
#   "expense" -> adds a "Log an expense" button -> short amount+note form
#   "journal" -> adds "Start trading journal" / "Start daily journal" buttons
ROUTINE_TASKS = [
    {"id": "wake_up", "time": "06:00", "name": "Wake up",
     "description": "10-minute meditation + discipline quote.", "kind": "simple"},
    {"id": "exercise", "time": "06:15", "name": "Morning exercise",
     "description": "Push-ups, sit-ups and squats.", "kind": "simple"},
    {"id": "get_ready", "time": "08:00", "name": "Get ready for office",
     "description": "", "kind": "simple"},
    {"id": "office", "time": "10:15", "name": "Office arrival deadline",
     "description": "", "kind": "simple"},
    {"id": "expense", "time": "15:30", "name": "Record daily expenses",
     "description": "Log everything you've spent so far today.", "kind": "expense"},
    {"id": "walk", "time": "18:15", "name": "Walk home",
     "description": "Target: 10,000 steps.", "kind": "simple"},
    {"id": "backtesting", "time": "20:00", "name": "Trading backtesting",
     "description": "1-hour backtesting session.", "kind": "simple"},
    {"id": "fin_learning", "time": "21:00", "name": "Financial learning",
     "description": "", "kind": "simple"},
    {"id": "journal", "time": "22:11", "name": "Daily journal & review",
     "description": "Trading journal, financial learning, achievements, reflection, open notes.",
     "kind": "journal"},
    {"id": "sleep", "time": "23:00", "name": "Sleep",
     "description": "", "kind": "simple"},
]
