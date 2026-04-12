PREMIUM_MIN_SCORE = 80.0


def get_premium_recipients():
    return [
        {
            "id": "default-premium",
            "tier": "premium",
            "min_score": PREMIUM_MIN_SCORE,
            "telegram_enabled": True,
        }
    ]


def filter_premium_deals(deals, min_score=PREMIUM_MIN_SCORE):
    filtered_deals = []
    for deal in deals or []:
        try:
            score = float(deal.get("score", 0) or 0)
        except (TypeError, ValueError):
            score = 0.0

        if score > float(min_score):
            filtered_deals.append(deal)

    filtered_deals.sort(
        key=lambda deal: (
            -float(deal.get("score", 0) or 0),
            float(deal.get("price", 0) or 0),
        )
    )
    return filtered_deals


def get_premium_notification_context(deals):
    recipients = [r for r in get_premium_recipients() if r.get("telegram_enabled")]
    premium_deals = filter_premium_deals(deals)
    return {
        "recipients": recipients,
        "deals": premium_deals,
        "min_score": PREMIUM_MIN_SCORE,
    }
