"""
Checks which routine reminders are due right now (Nepal time) and
haven't already gone out today, and sends them.
"""

from datetime import datetime, timedelta

import state
from config import NEPAL_TZ, POLL_INTERVAL_MINUTES, ROUTINE_TASKS
from telegram_client import inline_keyboard, send_message


def _is_due(task_time_str: str, now: datetime) -> bool:
    task_h, task_m = map(int, task_time_str.split(":"))
    task_dt = now.replace(hour=task_h, minute=task_m, second=0, microsecond=0)
    # Due if the scheduled moment falls in the window since the last
    # poll -- still catches it if this run is a few minutes late.
    window_start = now - timedelta(minutes=POLL_INTERVAL_MINUTES)
    return window_start <= task_dt <= now


def check_and_send_due_reminders():
    now = datetime.now(NEPAL_TZ)
    today = now.date()

    for task in ROUTINE_TASKS:
        if state.has_sent_today(task["id"], today):
            continue
        if not _is_due(task["time"], now):
            continue
        _send_reminder(task, today)
        state.mark_sent(task["id"], today)


def _send_reminder(task: dict, today):
    text = f"⏰ {task['name']} ({task['time']})"
    if task["description"]:
        text += f"\n{task['description']}"

    date_str = today.isoformat()
    done_row = [
        ("✅ Completed", f"done:{task['id']}:{date_str}"),
        ("❌ Not completed", f"notdone:{task['id']}:{date_str}"),
    ]

    if task["kind"] == "expense":
        keyboard = inline_keyboard([
            [("💸 Log an expense", f"startform:expense:{date_str}")],
            done_row,
        ])
    elif task["kind"] == "journal":
        keyboard = inline_keyboard([
            [("📓 Start trading journal", f"startform:trading_journal:{date_str}")],
            [("📝 Start daily journal", f"startform:daily_journal:{date_str}")],
            done_row,
        ])
    else:
        keyboard = inline_keyboard([done_row])

    send_message(text, reply_markup=keyboard)
