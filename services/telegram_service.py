import json
import os
from pathlib import Path
from datetime import date
from datetime import datetime, timedelta
from urllib import error, parse, request

from dotenv import load_dotenv
from database import (
    get_detected_deals_for_date,
    get_last_notification_time,
    has_notification_been_sent,
    init_db,
    mark_notification_sent,
    update_last_notification_time,
)
from services.ai_service import should_send_deal
from services.premium_service import get_premium_notification_context


TELEGRAM_API_BASE = "https://api.telegram.org"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NOTIFICATION_COOLDOWN_HOURS = 2
BOT_USERNAME_CACHE = None

load_dotenv(PROJECT_ROOT / ".env")


def _to_number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def get_telegram_bot_username():
    global BOT_USERNAME_CACHE

    if BOT_USERNAME_CACHE:
        return BOT_USERNAME_CACHE

    env_username = str(os.getenv("TELEGRAM_BOT_USERNAME") or "").strip().lstrip("@")
    if env_username:
        BOT_USERNAME_CACHE = env_username
        return BOT_USERNAME_CACHE

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return ""

    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/getMe"
    try:
        with request.urlopen(url, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            username = str((data.get("result") or {}).get("username") or "").strip()
            if username:
                BOT_USERNAME_CACHE = username
                return BOT_USERNAME_CACHE
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return ""

    return ""


def _format_deal_line(deal):
    return (
        f"{deal['name']}\n"
        f"💰 {deal['price']}\n"
        f"⭐ {_to_number(deal.get('score')):.1f}\n"
        f"{deal['url']}"
    )


def _build_feedback_keyboard(deals):
    inline_keyboard = []
    for deal in deals or []:
        product_id = deal.get("product_id")
        if product_id is None:
            continue
        inline_keyboard.append(
            [
                {"text": "👍 Like", "callback_data": f"like:{product_id}"},
                {"text": "👎 Not relevant", "callback_data": f"dislike:{product_id}"},
            ]
        )

    if not inline_keyboard:
        return None

    return {"inline_keyboard": inline_keyboard}


def _get_recipient_key(user_profile=None, chat_id=None):
    if user_profile:
        if user_profile.get("telegram_chat_id"):
            return f"tg:{user_profile['telegram_chat_id']}"
        if user_profile.get("user_id") is not None:
            return f"user:{user_profile['user_id']}"
    if chat_id:
        return f"tg:{chat_id}"
    env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    return f"tg:{env_chat_id}" if env_chat_id else "tg:default"


def _parse_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace(" ", "T"))
    except ValueError:
        return None


def _is_urgent_deal(deal):
    score = _to_number(deal.get("score"))
    discount_pct = _to_number(deal.get("discount_pct"))
    priority = str(deal.get("notification_priority", "")).strip().lower()
    return priority == "high" and (score >= 95.0 or discount_pct >= 70.0)


def _apply_notification_timing(deals, recipient_key, cooldown_hours):
    deals = deals or []
    if not deals:
        return []

    last_sent_at = _parse_timestamp(get_last_notification_time(recipient_key))
    if last_sent_at is None:
        return deals

    cooldown_until = last_sent_at + timedelta(hours=float(cooldown_hours))
    if datetime.now() >= cooldown_until:
        return deals

    return [deal for deal in deals if _is_urgent_deal(deal)]


def _filter_notifiable_deals(deals, user_profile):
    notifiable_deals = []
    for deal in deals or []:
        decision = should_send_deal(user_profile or {}, deal)
        if decision.get("send") and decision.get("priority") == "high":
            notifiable_deals.append(
                {
                    **deal,
                    "notification_priority": decision.get("priority"),
                    "notification_reason": decision.get("reason", ""),
                }
            )
    return notifiable_deals


def _build_deals_message(deals):
    if not deals:
        return ""

    ordered_deals = sorted(
        deals,
        key=lambda deal: (-_to_number(deal.get("score")), _to_number(deal.get("price"))),
    )
    best_deal = ordered_deals[0]
    other_deals = ordered_deals[1:]
    best_reason = str(best_deal.get("ai_reason", "")).strip() or "Strong match for this user."

    lines = [
        "🔥 BEST DEAL",
        best_deal["name"],
        f"💰 {best_deal['price']}",
        f"⭐ {_to_number(best_deal.get('score')):.1f}",
        "",
        "💡 Why:",
        best_reason,
        "",
        best_deal["url"],
    ]

    if other_deals:
        lines.append("")
        lines.append("Other deals:")
        for deal in other_deals:
            lines.append(
                f"• {deal['name']} | {deal['price']} | score {_to_number(deal.get('score')):.1f}\n{deal['url']}"
            )

    return "\n".join(lines)


def _build_daily_summary_message(deals):
    if not deals:
        return ""

    ordered_deals = sorted(
        deals,
        key=lambda deal: (-_to_number(deal.get("score")), _to_number(deal.get("price"))),
    )
    best_deal = ordered_deals[0]
    other_deals = ordered_deals[1:]
    best_reason = str(best_deal.get("ai_reason", "")).strip() or "Top deal of the day."

    lines = [
        "📊 DAILY DEAL SUMMARY",
        "",
        "🔥 BEST DEAL",
        best_deal["name"],
        f"💰 {best_deal['price']}",
        f"⭐ {_to_number(best_deal.get('score')):.1f}",
        "",
        "💡 Why:",
        best_reason,
        "",
        best_deal["url"],
    ]

    if other_deals:
        lines.append("")
        lines.append("Other deals:")
        for deal in other_deals:
            lines.append(
                f"• {deal['name']} | {deal['price']} | score {_to_number(deal.get('score')):.1f}\n{deal['url']}"
            )

    return "\n".join(lines)


def _build_alert_match_message(match):
    return "\n".join(
        [
            f"🔔 {match['name']} появился",
            "",
            "Открыть на сайте:",
            match["url"],
        ]
    )


def send_telegram_message(text, chat_id=None, reply_markup=None):
    bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = str(chat_id or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not bot_token or not chat_id or not str(text or "").strip():
        return False

    payload_dict = {
        "chat_id": chat_id,
        "text": str(text),
        "disable_web_page_preview": "true",
    }
    if reply_markup:
        payload_dict["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)

    payload = parse.urlencode(payload_dict, encoding="utf-8").encode("utf-8")
    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        req = request.Request(url, data=payload, headers=headers, method="POST")
        with request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            return bool(data.get("ok"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return False


def notify_alert_matches(matches, chat_id):
    if not matches or not chat_id:
        return 0

    sent_count = 0
    for match in matches:
        if send_alert_match(match, chat_id):
            sent_count += 1
    return sent_count


def send_alert_match(match, chat_id):
    if not match or not chat_id:
        return False

    message = _build_alert_match_message(match)
    return send_telegram_message(message, chat_id=chat_id)


def notify_new_deals(deals, user_profile=None):
    notification_context = get_premium_notification_context(deals)
    premium_deals = notification_context["deals"]
    recipients = notification_context["recipients"]
    if not premium_deals or not recipients:
        return 0

    notifiable_deals = _filter_notifiable_deals(premium_deals, user_profile or {})
    if not notifiable_deals:
        return 0

    chat_id = (user_profile or {}).get("telegram_chat_id")
    recipient_key = _get_recipient_key(user_profile=user_profile, chat_id=chat_id)
    timed_deals = _apply_notification_timing(
        notifiable_deals,
        recipient_key=recipient_key,
        cooldown_hours=(user_profile or {}).get(
            "notification_cooldown_hours",
            DEFAULT_NOTIFICATION_COOLDOWN_HOURS,
        ),
    )
    if not timed_deals:
        return 0

    text = _build_deals_message(timed_deals)
    keyboard = _build_feedback_keyboard(timed_deals)
    sent = 1 if text and send_telegram_message(text, chat_id=chat_id, reply_markup=keyboard) else 0
    if sent:
        update_last_notification_time(recipient_key)
    return sent


def send_daily_summary(summary_date=None):
    init_db()
    summary_date = summary_date or date.today().isoformat()
    notification_type = "daily_summary"

    if has_notification_been_sent(notification_type, summary_date):
        return {
            "sent": False,
            "reason": "already_sent",
            "date": summary_date,
            "deals_count": 0,
        }

    rows = get_detected_deals_for_date(summary_date)
    deals = [
        {
            "deal_id": row[0],
            "product_id": row[1],
            "name": row[2],
            "price": row[3],
            "source": row[4],
            "score": row[5],
            "url": row[6],
            "detected_at": row[7],
        }
        for row in rows
    ]
    notification_context = get_premium_notification_context(deals)
    premium_deals = notification_context["deals"]
    recipients = notification_context["recipients"]
    if not premium_deals or not recipients:
        return {
            "sent": False,
            "reason": "no_deals",
            "date": summary_date,
            "deals_count": 0,
        }

    text = _build_daily_summary_message(premium_deals)
    if not text or not send_telegram_message(text):
        return {
            "sent": False,
            "reason": "send_failed",
            "date": summary_date,
            "deals_count": len(premium_deals),
        }

    mark_notification_sent(notification_type, summary_date)
    return {
        "sent": True,
        "reason": "ok",
        "date": summary_date,
        "deals_count": len(premium_deals),
        "recipient_count": len(recipients),
    }
