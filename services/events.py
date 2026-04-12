import re

from database import insert_behavior_event


ALLOWED_EVENT_TYPES = {
    "notification_sent",
    "notification_opened",
    "product_viewed",
    "offer_clicked",
}


def normalize_product_family_key(value):
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""

    normalized = re.sub(r"[.\-_/]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def log_event(
    user_id,
    event_type,
    product_family_key,
    offer_id=None,
    price=None,
):
    if str(event_type or "").strip() not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")

    normalized_family_key = normalize_product_family_key(product_family_key)
    if not normalized_family_key:
        return

    insert_behavior_event(
        user_id=user_id,
        event_type=str(event_type).strip(),
        product_family_key=normalized_family_key,
        offer_id=offer_id,
        price=price,
    )
