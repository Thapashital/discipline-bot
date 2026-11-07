"""
Entry point. GitHub Actions runs this once every POLL_INTERVAL_MINUTES
(see .github/workflows/poller.yml). It has no memory of previous runs
-- all state lives in the Google Sheet (see state.py).
"""

import callbacks
import forms
import reminders
import state
from telegram_client import get_updates

ACTIVITY_COMMANDS = {"/addactivity", "add activity", "additional activity"}
EXPENSE_COMMANDS = {"/expense", "expense"}


def main():
    offset = state.get_last_update_id()
    updates = get_updates(offset=(offset + 1) if offset else None)

    for update in updates:
        if "callback_query" in update:
            callbacks.handle_callback_query(update)

        elif "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"]

            # If the user is mid-form (or owes a "not completed" reason),
            # this text belongs to that flow, whatever it says.
            consumed = callbacks.handle_text(chat_id, text)

            if not consumed:
                normalized = text.strip().lower()
                if normalized in ACTIVITY_COMMANDS:
                    forms.start_form(str(chat_id), "additional_activity")
                elif normalized in EXPENSE_COMMANDS:
                    forms.start_form(str(chat_id), "expense")

        state.set_last_update_id(update["update_id"])

    reminders.check_and_send_due_reminders()


if __name__ == "__main__":
    main()
