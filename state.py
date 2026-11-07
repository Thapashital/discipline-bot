"""
The poller has no memory between runs -- GitHub Actions gives it a
fresh, empty container every time it fires. So anything that needs to
persist (which Telegram update_id we've already processed, which
reminders already went out today, what a user is mid-way through
answering) lives in the Google Sheet instead.
"""

import json
from datetime import date, datetime

from config import NEPAL_TZ
from sheets_client import append_row, get_worksheet


def _now():
    return datetime.now(NEPAL_TZ)


# ---- Telegram update offset ----------------------------------------------

def get_last_update_id() -> int | None:
    ws = get_worksheet("BotState")
    for row in ws.get_all_records():
        if row.get("Key") == "last_update_id":
            value = row.get("Value")
            return int(value) if value not in (None, "") else None
    return None


def set_last_update_id(update_id: int):
    ws = get_worksheet("BotState")
    records = ws.get_all_records()
    for idx, row in enumerate(records, start=2):  # row 1 is the header
        if row.get("Key") == "last_update_id":
            ws.update_cell(idx, 2, update_id)
            return
    ws.append_row(["last_update_id", update_id])


# ---- Reminder dedupe ("has today's 6 AM message already gone out?") ------

def has_sent_today(task_id: str, for_date: date) -> bool:
    ws = get_worksheet("ReminderLog")
    for row in ws.get_all_records():
        if row.get("TaskID") == task_id and row.get("Date") == for_date.isoformat():
            return True
    return False


def mark_sent(task_id: str, for_date: date):
    append_row("ReminderLog", [for_date.isoformat(), task_id,
                                _now().isoformat(timespec="seconds")])


# ---- Pending multi-step flows (reason capture, journal/expense forms) ----

def get_pending(chat_id: str):
    ws = get_worksheet("PendingFlow")
    for idx, row in enumerate(ws.get_all_records(), start=2):
        if str(row.get("ChatID")) == str(chat_id):
            return idx, row
    return None, None


def set_pending(chat_id: str, form_key: str, step_index: int,
                 answers: dict, context: dict):
    ws = get_worksheet("PendingFlow")
    row_idx, _ = get_pending(chat_id)
    values = [
        str(chat_id), form_key, step_index,
        json.dumps(answers), json.dumps(context),
        _now().isoformat(timespec="seconds"),
    ]
    if row_idx:
        ws.update(f"A{row_idx}:F{row_idx}", [values])
    else:
        ws.append_row(values)


def clear_pending(chat_id: str):
    ws = get_worksheet("PendingFlow")
    row_idx, _ = get_pending(chat_id)
    if row_idx:
        ws.delete_rows(row_idx)
