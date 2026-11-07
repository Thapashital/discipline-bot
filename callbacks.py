"""
Handles Telegram callback_query updates (inline button presses) and
the one piece of free text that isn't a form -- the mandatory reason
for a "Not completed" tap.
"""

import json
import uuid
from datetime import datetime

import forms
import state
from config import NEPAL_TZ
from sheets_client import append_row
from telegram_client import answer_callback_query, send_message


def handle_callback_query(update: dict):
    cq = update["callback_query"]
    cq_id = cq["id"]
    chat_id = str(cq["message"]["chat"]["id"])
    data = cq["data"]  # e.g. "done:wake_up:2026-11-07"

    action, task_id, task_date = data.split(":", 2)

    if action == "done":
        _log_completion(task_id, task_date, status="Completed")
        answer_callback_query(cq_id, "Logged as completed.")
        send_message(f"✅ {task_id.replace('_', ' ').title()} marked completed.")

    elif action == "notdone":
        state.set_pending(chat_id, "await_reason", 0, {},
                           {"task_id": task_id, "date": task_date})
        answer_callback_query(cq_id, "Noted.")
        send_message("What stopped you from completing this? (required -- type your answer)")

    elif action == "startform":
        form_key = task_id  # reused this field to carry the form key
        answer_callback_query(cq_id)
        forms.start_form(chat_id, form_key, {"date": task_date})


def _log_completion(task_id: str, task_date: str, status: str, reason: str = ""):
    row_id = str(uuid.uuid4())[:8]
    append_row("Daily Activity Records", [
        row_id, task_date, task_id, task_id.replace("_", " ").title(),
        "", status, datetime.now(NEPAL_TZ).isoformat(timespec="seconds"), reason, "",
    ])


def handle_text(chat_id, text: str) -> bool:
    """Returns True if this text was consumed -- either the
    not-completed reason capture, or a multi-step form waiting on it."""
    chat_id = str(chat_id)
    _row_idx, pending = state.get_pending(chat_id)

    if pending and pending.get("FormKey") == "await_reason":
        context = json.loads(pending["ContextJSON"] or "{}")
        reason = text.strip()
        if not reason:
            send_message("A reason is required -- please type a short note.")
            return True
        _log_completion(context["task_id"], context["date"],
                         status="Not Completed", reason=reason)
        state.clear_pending(chat_id)
        send_message("Got it, logged. Thanks for the honesty.")
        return True

    return forms.handle_form_text(chat_id, text)
