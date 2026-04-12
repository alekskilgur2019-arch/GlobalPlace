from database import get_behavior_event_counts
from services.events import ALLOWED_EVENT_TYPES, normalize_product_family_key


def get_event_counts(user_id, product_family_key):
    normalized_family_key = normalize_product_family_key(product_family_key)
    counts = {event_type: 0 for event_type in ALLOWED_EVENT_TYPES}
    if not normalized_family_key:
        return counts

    rows = get_behavior_event_counts(user_id, normalized_family_key)
    for event_type, count in rows:
        counts[str(event_type)] = int(count or 0)
    return counts


def get_open_rate(user_id, product_family_key):
    counts = get_event_counts(user_id, product_family_key)
    sent = counts["notification_sent"]
    if sent <= 0:
        return 0.0
    return counts["notification_opened"] / sent


def get_click_rate(user_id, product_family_key):
    counts = get_event_counts(user_id, product_family_key)
    opened = counts["notification_opened"]
    if opened <= 0:
        return 0.0
    return counts["offer_clicked"] / opened


def get_engagement_score(user_id, product_family_key):
    counts = get_event_counts(user_id, product_family_key)
    return (
        counts["notification_opened"] * 1
        + counts["product_viewed"] * 1
        + counts["offer_clicked"] * 3
    )


def get_family_metrics(user_id, product_family_key):
    counts = get_event_counts(user_id, product_family_key)
    return {
        "counts": counts,
        "open_rate": get_open_rate(user_id, product_family_key),
        "click_rate": get_click_rate(user_id, product_family_key),
        "engagement_score": get_engagement_score(user_id, product_family_key),
    }
