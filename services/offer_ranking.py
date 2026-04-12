CONDITION_PRIORITY = {
    "new": 6,
    "like_new": 5,
    "excellent": 4,
    "good": 3,
    "fair": 2,
    "used": 1,
    "unknown": 0,
}

SOURCE_PRIORITY = {
    "apple": 5,
    "amazon": 4,
    "bestbuy": 3,
    "ebay": 2,
    "willhaben": 1,
    "other": 0,
}

SOURCE_EFFECTIVE_PRICE_FACTORS = {
    "apple": 0.95,
    "amazon": 0.94,
    "bestbuy": 0.93,
    "ebay": 0.92,
    "willhaben": 0.90,
    "other": 0.95,
}


def _normalize_condition(condition):
    normalized = str(condition or "").strip().lower().replace(" ", "_")
    return normalized if normalized in CONDITION_PRIORITY else "unknown"


def _normalize_source(source):
    normalized = str(source or "").strip().lower()
    return normalized if normalized in SOURCE_PRIORITY else "other"


def build_offer_sort_key(offer):
    condition = _normalize_condition(offer.get("condition"))
    source = _normalize_source(offer.get("source"))
    price = float(offer.get("price", 0) or 0)
    effective_price = round(
        price * SOURCE_EFFECTIVE_PRICE_FACTORS.get(source, 0.95),
        2,
    )
    return (
        -CONDITION_PRIORITY.get(condition, 0),
        price,
        -SOURCE_PRIORITY.get(source, 0),
        effective_price,
        int(offer.get("id", 0) or 0),
        str(offer.get("created_at") or ""),
    )


def select_best_offer(offers):
    normalized_offers = list(offers or [])
    if not normalized_offers:
        return None
    return sorted(normalized_offers, key=build_offer_sort_key)[0]
