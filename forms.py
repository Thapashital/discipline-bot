"""
Generic multi-step conversation engine. Each form is an ordered list
of fields; the bot asks one question per field, and "skip" satisfies
any optional field. Once every field has an answer (or was skipped),
the collected answers are written as a single row to the form's tab.
"""

import json
import uuid
from datetime import datetime

import state
from config import NEPAL_TZ
from sheets_client import append_row
from telegram_client import send_message

# field = (column_name, prompt_text, required: bool)

FORMS = {
    "additional_activity": {
        "sheet": "Additional Activities",
        "intro": "Logging an additional activity -- outside your normal routine.",
        "fields": [
            ("ActivityName", "Activity name?", True),
            ("WhatDidYouDo", "What did you do?", True),
            ("TimeSpent", "Time spent? (or type 'skip')", False),
            ("LearnedOrAchieved", "What did you learn or achieve?", True),
            ("Notes", "Any additional notes? (or type 'skip')", False),
        ],
    },
    "expense": {
        "sheet": "Expense Report",
        "intro": "Logging an expense.",
        "fields": [
            ("AmountNPR", "How much did you spend (NPR)?", True),
            ("Description", "What was it for? (or type 'skip')", False),
        ],
    },
    "trading_journal": {
        "sheet": "Trading Journal",
        "intro": "Trading journal -- type 'skip' on anything that doesn't apply today. "
                  "(Win rate is only saved if you also give a real trade count.)",
        "fields": [
            ("BestTrade", "Best trade of the day? (or 'skip')", False),
            ("WinRatePercent", "Win rate %, only if measured (or 'skip')", False),
            ("NumTrades", "Number of trades today (or 'skip')", False),
            ("WinningTrades", "Winning trades (or 'skip')", False),
            ("LosingTrades", "Losing trades (or 'skip')", False),
            ("BacktestObservations", "Backtesting observations (or 'skip')", False),
            ("TradingLessons", "Trading lessons (or 'skip')", False),
            ("MistakesAndImprovements", "Mistakes and improvements (or 'skip')", False),
        ],
    },
    "daily_journal": {
        "sheet": "Daily Journal",
        "intro": "Daily journal -- financial learning, achievements, reflection. "
                  "Type 'skip' to pass on any section.",
        "fields": [
            ("LearnedToday", "What did you learn today? (or 'skip')", False),
            ("ImportantConcepts", "Important concepts? (or 'skip')", False),
            ("NewKnowledge", "New knowledge? (or 'skip')", False),
            ("QuestionsToResearch", "Questions or topics to research? (or 'skip')", False),
            ("BestAchievement", "Best achievement of the day? (or 'skip')", False),
            ("BiggestWin", "Biggest win of the day? (or 'skip')", False),
            ("ProudOf", "Something you're proud of? (or 'skip')", False),
            ("NewAccomplishment", "Something new you accomplished? (or 'skip')", False),
            ("HowWasMyDay", "How was your day? (or 'skip')", False),
            ("WhatWentWell", "What went well? (or 'skip')", False),
            ("WhatCouldBeBetter", "What could have been better? (or 'skip')", False),
            ("LearnedAboutMyself", "What did you learn about yourself? (or 'skip')", False),
            ("OpenNotes", "Anything else, free-form -- write as much as you like.", False),
        ],
    },
}


def start_form(chat_id: str, form_key: str, context: dict | None = None):
    form = FORMS[form_key]
    if form["intro"]:
        send_message(form["intro"])
    state.set_pending(chat_id, form_key, 0, {}, context or {})
    _ask_current_field(form_key, 0)


def _ask_current_field(form_key: str, step_index: int):
    _field_name, prompt, _required = FORMS[form_key]["fields"][step_index]
    send_message(prompt)


def handle_form_text(chat_id: str, text: str) -> bool:
    """Returns True if this text was consumed by an in-progress form."""
    _row_idx, pending = state.get_pending(chat_id)
    if not pending or pending.get("FormKey") not in FORMS:
        return False

    form_key = pending["FormKey"]
    step_index = int(pending["StepIndex"])
    answers = json.loads(pending["AnswersJSON"] or "{}")
    context = json.loads(pending["ContextJSON"] or "{}")
    form = FORMS[form_key]
    field_name, prompt, required = form["fields"][step_index]

    value = text.strip()
    if value.lower() == "skip":
        if required:
            send_message(f"That one's required: {prompt}")
            return True
        value = ""

    answers[field_name] = value
    step_index += 1

    if step_index < len(form["fields"]):
        state.set_pending(chat_id, form_key, step_index, answers, context)
        _ask_current_field(form_key, step_index)
    else:
        _finish_form(form_key, answers)
        state.clear_pending(chat_id)

    return True


def _finish_form(form_key: str, answers: dict):
    sheet = FORMS[form_key]["sheet"]
    header_order = [f[0] for f in FORMS[form_key]["fields"]]
    row_id = str(uuid.uuid4())[:8]
    today = datetime.now(NEPAL_TZ).date().isoformat()
    row = (
        [row_id, today]
        + [answers.get(col, "") for col in header_order]
        + [datetime.now(NEPAL_TZ).isoformat(timespec="seconds")]
    )
    append_row(sheet, row)
    send_message("Saved. Thanks!")
