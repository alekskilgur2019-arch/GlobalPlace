import json
import os
import time
from urllib import error, request

from database import init_db
from services.telegram_service import TELEGRAM_API_BASE
from services.telegram_user_service import process_telegram_update


def _get_bot_token():
    return str(os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()


def _telegram_api_request(method_name, payload=None):
    bot_token = _get_bot_token()
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required.")

    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/{method_name}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method="POST")
    with request.urlopen(req, timeout=35) as response:
        body = response.read().decode("utf-8")
        parsed = json.loads(body)
        if not parsed.get("ok"):
            raise RuntimeError(f"Telegram API error on {method_name}: {parsed}")
        return parsed


def _delete_webhook():
    _telegram_api_request("deleteWebhook", {"drop_pending_updates": False})


def _get_updates(offset=None, timeout=25):
    payload = {
        "timeout": int(timeout),
        "allowed_updates": ["message", "callback_query"],
    }
    if offset is not None:
        payload["offset"] = int(offset)
    response = _telegram_api_request("getUpdates", payload)
    return response.get("result", [])


def main():
    init_db()
    last_update_id = None
    print("Telegram bot polling started.")
    while True:
        try:
            _delete_webhook()
            updates = _get_updates(
                offset=None if last_update_id is None else last_update_id + 1
            )
            for update in updates:
                update_id = int(update.get("update_id", 0) or 0)
                if update_id:
                    last_update_id = update_id
                result = process_telegram_update(update)
                print(
                    json.dumps(
                        {
                            "event": "telegram_update_processed",
                            "update_id": update_id,
                            "result": result,
                        },
                        ensure_ascii=False,
                    )
                )
        except (error.URLError, error.HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            print(f"Telegram bot polling error: {exc}")
            time.sleep(3)
        except Exception as exc:
            print(f"Telegram bot unexpected error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()
