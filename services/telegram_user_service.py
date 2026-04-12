from services.telegram_service import send_telegram_message
from services.user_profile_service import UserProfileService
from database import (
    add_user_preference,
    get_product_by_id,
    get_user_by_telegram_chat_id,
    get_or_create_telegram_user,
    init_db,
    log_telegram_interaction,
)
from services.deal_service import get_personalized_deals
from services.user_behavior_service import track_user_feedback, track_user_product_click

user_profile_service = UserProfileService()


def _extract_start_token(text):
    normalized_text = str(text or "").strip()
    if not normalized_text.startswith("/start"):
        return ""

    parts = normalized_text.split(maxsplit=1)
    if len(parts) < 2:
        return ""
    return parts[1].strip()


def _send_telegram_onboarding_message(chat_id):
    onboarding_context = user_profile_service.get_telegram_onboarding_context()
    website_url = onboarding_context.get("website_url", "")
    message = (
        "Это бот GlobalPlace.\n"
        "Он уведомляет вас, когда появляется нужный товар.\n"
        "Перейдите на сайт, чтобы начать."
    )
    keyboard = None
    if website_url:
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "Open GlobalPlace",
                        "url": website_url,
                    }
                ]
            ]
        }

    send_telegram_message(message, chat_id=chat_id, reply_markup=keyboard)
    return {
        "ok": True,
        "message": "Telegram onboarding message sent.",
        "chat_id": str(chat_id),
        "website_url": website_url,
    }


def _handle_telegram_start(chat_id, text):
    connect_token = _extract_start_token(text)
    if not connect_token:
        return _send_telegram_onboarding_message(chat_id)

    link_result = user_profile_service.link_telegram_chat_by_connect_token(
        connect_token=connect_token,
        telegram_chat_id=chat_id,
    )
    if link_result["ok"]:
        send_telegram_message(
            "Telegram подключён ✅",
            chat_id=chat_id,
        )
        return {
            "ok": True,
            "message": "Telegram account linked.",
            "chat_id": str(chat_id),
            "user_id": link_result["user_id"],
            "linked": True,
        }

    send_telegram_message(
        "Ссылка устарела. Вернитесь на сайт и попробуйте снова.",
        chat_id=chat_id,
    )
    return {
        "ok": False,
        "message": link_result["message"],
        "chat_id": str(chat_id),
        "linked": False,
    }


def _extract_search_query(text):
    normalized_text = str(text or "").strip()
    if not normalized_text:
        return ""

    if normalized_text.startswith("/start"):
        return ""
    if normalized_text.startswith("/search "):
        return normalized_text.split(" ", 1)[1].strip()
    return normalized_text


def register_telegram_message(chat_id, text):
    init_db()
    existing_user = get_user_by_telegram_chat_id(chat_id)
    user = get_or_create_telegram_user(chat_id)
    local_user_id = int(user[0])
    search_query = _extract_search_query(text)

    log_telegram_interaction(
        user_id=local_user_id,
        telegram_chat_id=chat_id,
        interaction_type="message",
        query=search_query or None,
        raw_text=text,
    )

    if search_query:
        add_user_preference(local_user_id, search_query)
        track_user_product_click(local_user_id, search_query)

    return {
        "user_id": str(chat_id),
        "local_user_id": local_user_id,
        "query": search_query,
        "created": existing_user is None,
    }


def process_telegram_update(update):
    callback_query = (update or {}).get("callback_query")
    if callback_query:
        return process_telegram_callback(callback_query)

    message = (update or {}).get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")
    if chat_id is None:
        return None

    if str(text or "").strip().startswith("/start"):
        return _handle_telegram_start(chat_id=chat_id, text=text)

    return register_telegram_message(chat_id=chat_id, text=text)


def get_personalized_deals_for_telegram_user(chat_id):
    init_db()
    user = get_or_create_telegram_user(chat_id)
    local_user_id = int(user[0])
    personalized = get_personalized_deals(local_user_id)
    return {
        "user_id": str(chat_id),
        "local_user_id": local_user_id,
        **personalized,
    }


def process_telegram_callback(callback_query):
    message = callback_query.get("message") or {}
    chat = (message.get("chat") or {})
    chat_id = chat.get("id")
    callback_data = callback_query.get("data", "")
    if chat_id is None or ":" not in callback_data:
        return None

    action, product_id = callback_data.split(":", 1)
    try:
        product_id = int(product_id)
    except ValueError:
        return None

    init_db()
    user = get_or_create_telegram_user(chat_id)
    local_user_id = int(user[0])
    product = get_product_by_id(product_id)
    if not product:
        return None

    product_name = product[1]
    liked = action == "like"
    track_user_feedback(local_user_id, product_name, liked=liked)
    log_telegram_interaction(
        user_id=local_user_id,
        telegram_chat_id=chat_id,
        interaction_type=f"feedback_{action}",
        query=product_name,
        raw_text=callback_data,
    )

    return {
        "user_id": str(chat_id),
        "local_user_id": local_user_id,
        "product_id": product_id,
        "product_name": product_name,
        "liked": liked,
    }
