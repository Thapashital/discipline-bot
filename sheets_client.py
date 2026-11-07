"""
Thin wrapper around gspread for the one Google Sheet that holds all
live data. Creates tabs with headers on first use so nothing else in
the project has to worry about one-time sheet setup.
"""

import base64
import json
from functools import lru_cache

import gspread
from gspread.exceptions import WorksheetNotFound
from google.oauth2.service_account import Credentials

from config import GOOGLE_SERVICE_ACCOUNT_JSON_B64, GOOGLE_SHEET_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# User-facing tabs, matching the spec's worksheet list (Dashboard,
# Weekly Summary and Incomplete Activities are built later, during the
# Excel workbook phase, from this raw data -- they aren't live-write
# tabs). Plus two small internal bookkeeping tabs the bot needs because
# it has no memory between runs.
TAB_HEADERS = {
    "Daily Activity Records": [
        "ID", "Date", "TaskID", "Task", "ScheduledTime",
        "Status", "CompletionTimestamp", "Reason", "Notes",
    ],
    "Additional Activities": [
        "ID", "Date", "ActivityName", "WhatDidYouDo",
        "TimeSpent", "LearnedOrAchieved", "Notes", "LoggedAt",
    ],
    "Trading Journal": [
        "ID", "Date", "BestTrade", "WinRatePercent", "NumTrades",
        "WinningTrades", "LosingTrades", "BacktestObservations",
        "TradingLessons", "MistakesAndImprovements", "LoggedAt",
    ],
    "Daily Journal": [
        "ID", "Date", "LearnedToday", "ImportantConcepts", "NewKnowledge",
        "QuestionsToResearch", "BestAchievement", "BiggestWin", "ProudOf",
        "NewAccomplishment", "HowWasMyDay", "WhatWentWell",
        "WhatCouldBeBetter", "LearnedAboutMyself", "OpenNotes", "LoggedAt",
    ],
    "Expense Report": ["ID", "Date", "AmountNPR", "Description", "LoggedAt"],
    # Internal only:
    "ReminderLog": ["Date", "TaskID", "SentAt"],
    "PendingFlow": ["ChatID", "FormKey", "StepIndex", "AnswersJSON", "ContextJSON", "UpdatedAt"],
    "BotState": ["Key", "Value"],
}


@lru_cache(maxsize=1)
def _client():
    info = json.loads(base64.b64decode(GOOGLE_SERVICE_ACCOUNT_JSON_B64))
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


@lru_cache(maxsize=1)
def _spreadsheet():
    return _client().open_by_key(GOOGLE_SHEET_ID)


@lru_cache(maxsize=None)
def get_worksheet(title: str):
    """Returns the worksheet, creating it with the right header row
    the first time it's needed."""
    ss = _spreadsheet()
    try:
        ws = ss.worksheet(title)
    except WorksheetNotFound:
        headers = TAB_HEADERS.get(title, [])
        ws = ss.add_worksheet(title=title, rows=2000, cols=max(len(headers), 1))
        if headers:
            ws.append_row(headers)
    return ws


def append_row(title: str, row: list):
    get_worksheet(title).append_row(row, value_input_option="USER_ENTERED")


def all_records(title: str):
    return get_worksheet(title).get_all_records()
