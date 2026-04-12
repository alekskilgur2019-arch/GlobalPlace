import hashlib
import json
import os

from dotenv import load_dotenv

from database import (
    create_user,
    delete_all_alerts_for_user,
    get_user_by_username,
    init_db,
    set_user_telegram_chat_id,
)
from services.alert_service import AlertService
from services.notification_service import NotificationService


TEST_USERNAME = "qa_alert_batch_user"
TEST_PASSWORD = "qa_batch_password"
QA_ALERTS = [
    {"query": "AirPods Pro", "target_price": None},
    {"query": "iPhone 13", "target_price": None},
    {"query": "PS5", "target_price": None},
    {"query": "Sony WH-1000XM5", "target_price": None},
    {"query": "MacBook Air", "target_price": 850},
    {"query": "Dyson V11", "target_price": 460},
    {"query": "AirPods", "target_price": None},
    {"query": "iPhone", "target_price": None},
    {"query": "Sony", "target_price": None},
    {"query": "Nintendo Switch", "target_price": None},
    {"query": "Xbox", "target_price": 500},
    {"query": "Philips Coffee Machine", "target_price": 350},
    {"query": "Air Fryer Philips", "target_price": 129},
    {"query": "Dell XPS 13", "target_price": 1000},
    {"query": "Google Pixel 7", "target_price": 380},
    {"query": "Pro", "target_price": None},
    {"query": "Max", "target_price": None},
    {"query": "Air", "target_price": None},
    {"query": "PS", "target_price": None},
    {"query": "Sneak", "target_price": None},
]


def _hash_password(password):
    return hashlib.sha256(str(password).encode("utf-8")).hexdigest()


def _ensure_test_user(telegram_chat_id):
    user = get_user_by_username(TEST_USERNAME)
    if not user:
        create_user(TEST_USERNAME, _hash_password(TEST_PASSWORD))
        user = get_user_by_username(TEST_USERNAME)

    user_id = user[0]
    set_user_telegram_chat_id(user_id, telegram_chat_id)
    return {
        "id": user_id,
        "username": user[1],
    }


def _build_alert_label(alert):
    target_price = alert.get("target_price")
    if target_price is None:
        return str(alert["query"])
    return f"{alert['query']} ({target_price})"


def _create_alerts(user_id):
    alert_service = AlertService()
    created_alerts = []
    for alert in QA_ALERTS:
        result = alert_service.create_user_alert(
            user_id=user_id,
            query=alert["query"],
            target_price=alert["target_price"],
        )
        created_alerts.append(
            {
                "query": alert["query"],
                "target_price": alert["target_price"],
                "ok": result["ok"],
                "alert_id": result.get("alert_id"),
            }
        )
    return created_alerts


def _build_run_summary(preview_response, notify_result):
    alerts = preview_response["alerts"]
    matches = preview_response["matches"]
    matched_alert_ids = {match["alert_id"] for match in matches}
    triggered_alerts = []
    ignored_alerts = []

    for alert in alerts:
        label = _build_alert_label(alert)
        if alert["id"] in matched_alert_ids:
            triggered_alerts.append(label)
        else:
            ignored_alerts.append(label)

    return {
        "total_alerts": len(alerts),
        "matches_found": notify_result["matches_found"],
        "notifications_sent": notify_result["notifications_sent"],
        "triggered_alerts": triggered_alerts,
        "ignored_alerts": ignored_alerts,
    }


def main():
    load_dotenv()
    init_db()

    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not telegram_chat_id:
        print("TELEGRAM_CHAT_ID is required for batch alert QA.")
        raise SystemExit(1)

    notification_service = NotificationService()
    test_user = _ensure_test_user(telegram_chat_id)

    delete_all_alerts_for_user(test_user["id"])
    notification_service.clear_user_notification_state(
        user_id=test_user["id"],
        telegram_chat_id=telegram_chat_id,
    )
    created_alerts = _create_alerts(test_user["id"])

    first_preview = notification_service.preview_alert_matches_for_user(test_user["id"])
    first_run_result = notification_service.notify_alert_matching_deals()
    first_summary = _build_run_summary(first_preview, first_run_result)

    second_preview = notification_service.preview_alert_matches_for_user(test_user["id"])
    second_run_result = notification_service.notify_alert_matching_deals()
    second_summary = _build_run_summary(second_preview, second_run_result)

    output = {
        "test_user": test_user,
        "total_seed_alerts": len(QA_ALERTS),
        "created_alerts": created_alerts,
        "first_run": first_summary,
        "second_run": second_summary,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
