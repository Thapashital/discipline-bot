"""
Minimal Telegram Bot API wrapper -- just the handful of calls this
project needs. No extra Telegram library, just `requests`.
"""

from __future__ import annotations

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def _post(method: str, **params):
    resp = requests.post(f"{API_BASE}/{method}", json=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def send_message(text: str, reply_markup: dict | None = None):
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    if reply_markup:
        params["reply_markup"] = reply_markup
    return _post("sendMessage", **params)


def answer_callback_query(callback_query_id: str, text: str = ""):
    return _post("answerCallbackQuery", callback_query_id=callback_query_id, text=text)


def get_updates(offset: int | None, timeout: int = 0):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=timeout + 15)
    resp.raise_for_status()
    return resp.json().get("result", [])


def inline_keyboard(buttons: list[list[tuple[str, str]]]) -> dict:
    """buttons = [[(label, callback_data), ...], ...] -> Telegram reply_markup"""
    return {
        "inline_keyboard": [
            [{"text": label, "callback_data": data} for label, data in row]
            for row in buttons
        ]
    }
