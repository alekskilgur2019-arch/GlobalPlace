import sys
import time

from database import (
    create_deal,
    create_detected_deals,
    get_all_deals,
    get_funnel_stats,
    get_product_by_id,
    get_recent_user_interactions,
    get_recent_user_searches,
    get_user_behavior,
    get_user_preferences,
    init_db,
)
from services.ai_service import evaluate_deal_for_user, generate_ai_deals
from services.product_service import ProductService
from services.telegram_service import notify_new_deals
from services.user_behavior_service import track_user_product_click, track_user_product_deal


DEFAULT_DISCOUNT_THRESHOLD_PCT = 25.0
MIN_GROUP_SIZE = 2
MIN_PRICE_EUR = 20.0
MIN_DEAL_SCORE = 60.0
MAX_DEALS_PER_RUN = 10
DEFAULT_DUPLICATE_WINDOW_HOURS = 24
MAX_PERSONALIZED_DEALS = 5

SOURCE_WEIGHTS = {
    "ebay": 1.0,
    "willhaben": 1.0,
    "amazon": 0.95,
}


def _normalize_product_name(name):
    return " ".join(str(name or "").strip().lower().split())


def _tokenize_text(text):
    normalized = _normalize_product_name(text)
    return [token for token in normalized.split() if len(token) >= 3]


def _is_relevant_product(product, min_price):
    name = str(product.get("name") or "").strip()
    url = str(product.get("url") or "").strip()
    source = str(product.get("source") or "").strip()
    price = product.get("price")

    if len(name) < 4 or not any(char.isalpha() for char in name):
        return False
    if not url or not source:
        return False

    try:
        return float(price) >= float(min_price)
    except (TypeError, ValueError):
        return False


def _group_products_by_name(products, min_price):
    grouped = {}

    for product in products:
        if product.get("id") is None or not _is_relevant_product(product, min_price):
            continue

        normalized_name = _normalize_product_name(product["name"])
        if not normalized_name:
            continue

        normalized_price = round(float(product["price"]), 2)
        dedupe_key = (
            normalized_name,
            str(product["source"]).strip().lower(),
            normalized_price,
            str(product["url"]).strip(),
        )

        bucket = grouped.setdefault(normalized_name, {"items": [], "seen": set()})
        if dedupe_key in bucket["seen"]:
            continue

        bucket["seen"].add(dedupe_key)
        bucket["items"].append(
            {
                "product_id": product["id"],
                "name": product["name"],
                "price": normalized_price,
                "url": product["url"],
                "source": product["source"],
                "image": product.get("image", ""),
            }
        )

    return {group_key: bucket["items"] for group_key, bucket in grouped.items()}


def _calculate_average_price(items):
    return round(sum(item["price"] for item in items) / len(items), 2)


def _get_source_weight(source):
    return SOURCE_WEIGHTS.get(str(source or "").strip().lower(), 0.9)


def _score_deal(discount_pct, average_price, current_price, source):
    discount_score = min(max(discount_pct, 0.0) * 2.0, 60.0)
    value_gap = max(average_price - current_price, 0.0)
    value_score = min((value_gap / max(average_price, 1.0)) * 30.0, 30.0)
    source_score = 10.0 * _get_source_weight(source)
    return round(min(discount_score + value_score + source_score, 100.0), 1)


class DealService:
    def _validate_user_id(self, user_id):
        if user_id is None:
            return {"ok": False, "message": "User id is required."}
        try:
            normalized_user_id = int(user_id)
        except (TypeError, ValueError):
            return {"ok": False, "message": "User id must be a valid integer."}
        if normalized_user_id <= 0:
            return {"ok": False, "message": "User id must be greater than 0."}
        return {"ok": True, "user_id": normalized_user_id}

    def _validate_product_id(self, product_id):
        if product_id is None:
            return {"ok": False, "message": "Product id is required."}
        try:
            normalized_product_id = int(product_id)
        except (TypeError, ValueError):
            return {"ok": False, "message": "Product id must be a valid integer."}
        if normalized_product_id <= 0:
            return {"ok": False, "message": "Product id must be greater than 0."}
        return {"ok": True, "product_id": normalized_product_id}

    def _validate_price(self, value, field_name):
        if value is None:
            return {"ok": False, "message": f"{field_name} is required."}
        try:
            normalized_price = float(value)
        except (TypeError, ValueError):
            return {"ok": False, "message": f"{field_name} must be a number."}
        if normalized_price <= 0:
            return {"ok": False, "message": f"{field_name} must be greater than 0."}
        return {"ok": True, "price": normalized_price}

    def _get_discount_decision(self, price, user_clicks, behavior=None):
        normalized_price = float(price)
        normalized_clicks = int(user_clicks or 0)

        if normalized_price < 50:
            base = 0.05
        elif normalized_price < 200:
            base = 0.10
        elif normalized_price < 500:
            base = 0.15
        else:
            base = 0.20

        boost = 0.05 if normalized_clicks >= 2 else 0.0
        behavior_adjustment = 0.0
        if behavior:
            avg_pref = float(behavior[3] or 0)
            if avg_pref > 15:
                behavior_adjustment = 0.05
            elif 0 < avg_pref < 10:
                behavior_adjustment = -0.03

        discount = min(max(base + boost + behavior_adjustment, 0.02), 0.40)
        reason = "AI found seller flexibility due to market conditions"
        if boost > 0:
            reason = f"{reason} (+behavior boost)"
        if behavior_adjustment > 0:
            reason = f"{reason} (+preference learning)"
        elif behavior_adjustment < 0:
            reason = f"{reason} (-decisive adjustment)"

        return {
            "discount": discount,
            "discount_pct": round(discount * 100, 0),
            "reason": reason,
        }

    def _calculate_deal_financials(
        self,
        original_price,
        negotiated_price,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        saving = round(float(original_price) - float(negotiated_price), 2)
        if saving <= 0:
            return {
                "ok": False,
                "message": "Negotiated price must be lower than original price.",
            }

        normalized_mode = str(commission_mode or "basic").strip().lower()
        normalized_percent = float(commission_percent or 10.0) / 100.0

        if normalized_mode == "advanced":
            commission = saving * normalized_percent
        else:
            if saving < 20:
                commission = saving * 0.05
            elif saving < 100:
                commission = saving * 0.10
            else:
                commission = saving * 0.15

        return {
            "ok": True,
            "saving": round(saving, 2),
            "commission": round(commission, 2),
        }

    def _score_preview_deal(self, discount_pct, saving, price, user_clicks):
        normalized_discount_pct = max(float(discount_pct or 0), 0.0)
        normalized_saving = max(float(saving or 0), 0.0)
        normalized_price = max(float(price or 0), 0.0)
        normalized_clicks = int(user_clicks or 0)

        base_score = min(normalized_discount_pct * 2.0, 60.0)
        saving_score = min(normalized_saving / 2.0, 25.0)

        if normalized_price < 50:
            price_weight = 3.0
        elif normalized_price < 200:
            price_weight = 6.0
        elif normalized_price < 500:
            price_weight = 8.0
        else:
            price_weight = 10.0

        click_bonus = 5.0 if normalized_clicks >= 2 else 0.0

        total_score = base_score + saving_score + price_weight + click_bonus
        return round(max(0.0, min(total_score, 100.0)), 1)

    def _build_social_proof(self):
        funnel_stats = get_funnel_stats()
        views_today = int(funnel_stats.get("visits", 0))
        deals_completed_today = int(funnel_stats.get("completed_deals", 0))
        return {
            "views_today": views_today,
            "deals_completed_today": deals_completed_today,
        }

    def build_deal_preview(
        self,
        product,
        user_clicks,
        user_id=None,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        price_validation = self._validate_price(product.get("price"), "Price")
        if not price_validation["ok"]:
            return {"ok": False, "message": price_validation["message"]}

        behavior = None
        if user_id is not None:
            behavior = get_user_behavior(user_id)

        discount_data = self._get_discount_decision(
            price=price_validation["price"],
            user_clicks=user_clicks,
            behavior=behavior,
        )
        negotiated_price = round(
            price_validation["price"] * (1 - discount_data["discount"]),
            2,
        )
        financials = self._calculate_deal_financials(
            original_price=price_validation["price"],
            negotiated_price=negotiated_price,
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )
        if not financials["ok"]:
            return {"ok": False, "message": financials["message"]}

        saving_pct = 0.0
        if price_validation["price"] > 0:
            saving_pct = round(
                (financials["saving"] / price_validation["price"]) * 100,
                1,
            )
        score = self._score_preview_deal(
            discount_pct=discount_data["discount_pct"],
            saving=financials["saving"],
            price=price_validation["price"],
            user_clicks=user_clicks,
        )
        social_proof = self._build_social_proof()

        return {
            "ok": True,
            "message": "Deal preview calculated.",
            "deal": {
                **product,
                "original_price": price_validation["price"],
                "negotiated_price": negotiated_price,
                "new_price": negotiated_price,
                "discount_pct": discount_data["discount_pct"],
                "reason": discount_data["reason"],
                "saving": financials["saving"],
                "commission": financials["commission"],
                "saving_pct": saving_pct,
                "score": score,
                "views_today": social_proof["views_today"],
                "deals_completed_today": social_proof["deals_completed_today"],
            },
        }

    def create_user_deal(
        self,
        user_id,
        product_id,
        original_price,
        negotiated_price,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {"ok": False, "message": user_validation["message"], "deal_id": None}

        product_validation = self._validate_product_id(product_id)
        if not product_validation["ok"]:
            return {"ok": False, "message": product_validation["message"], "deal_id": None}

        original_price_validation = self._validate_price(original_price, "Original price")
        if not original_price_validation["ok"]:
            return {"ok": False, "message": original_price_validation["message"], "deal_id": None}

        negotiated_price_validation = self._validate_price(negotiated_price, "Negotiated price")
        if not negotiated_price_validation["ok"]:
            return {"ok": False, "message": negotiated_price_validation["message"], "deal_id": None}

        product = get_product_by_id(product_validation["product_id"])
        if not product:
            return {"ok": False, "message": "Product not found.", "deal_id": None}

        financials = self._calculate_deal_financials(
            original_price_validation["price"],
            negotiated_price_validation["price"],
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )
        if not financials["ok"]:
            return {"ok": False, "message": financials["message"], "deal_id": None}

        deal_id = create_deal(
            user_validation["user_id"],
            product_validation["product_id"],
            original_price_validation["price"],
            negotiated_price_validation["price"],
            financials["saving"],
            financials["commission"],
        )
        return {
            "ok": True,
            "message": "Deal created.",
            "deal_id": deal_id,
            "saving": financials["saving"],
            "commission": financials["commission"],
        }

    def accept_deal(
        self,
        user_id,
        deal,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        create_result = self.create_user_deal(
            user_id=user_id,
            product_id=int(deal.get("id") or 0),
            original_price=deal["original_price"],
            negotiated_price=deal["new_price"],
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )
        if not create_result["ok"]:
            return create_result

        saving = create_result["saving"]
        accepted_pct = 0.0
        if float(deal["original_price"]) > 0:
            accepted_pct = (saving / float(deal["original_price"])) * 100

        track_user_product_click(user_id, deal["name"])
        track_user_product_deal(user_id, deal["name"], accepted_pct)

        return {
            "ok": True,
            "message": "Deal accepted.",
            "saving": saving,
            "commission": create_result["commission"],
            "accepted_discount_pct": round(accepted_pct, 2),
        }

    def get_ai_deals_for_user(
        self,
        user_id,
        user_clicks,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "deals": [],
            }

        preferences = get_user_preferences(user_validation["user_id"])
        if not preferences:
            return {
                "ok": True,
                "message": "No preferences found.",
                "deals": [],
            }

        product_service = ProductService()
        products = product_service.search_marketplace_products(query="")

        def build_preview(product):
            return self.build_deal_preview(
                product=product,
                user_clicks=user_clicks,
                user_id=user_validation["user_id"],
                commission_mode=commission_mode,
                commission_percent=commission_percent,
            )

        deals = generate_ai_deals(
            preferences=preferences,
            products=products,
            build_preview=build_preview,
        )
        return {
            "ok": True,
            "message": "AI deals prepared.",
            "deals": deals,
        }

    def list_deals(self):
        rows = get_all_deals()
        deals = [
            {
                "id": row[0],
                "product_id": row[1],
                "user_id": row[2],
                "original_price": row[3],
                "negotiated_price": row[4],
                "saving": row[5],
                "commission": row[6],
                "created_at": row[7],
            }
            for row in rows
        ]
        return {
            "ok": True,
            "message": "Deals loaded.",
            "deals": deals,
        }

    def get_personalized_deals(self, user_id, **kwargs):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "best_deal": None,
                "deals": [],
            }

        result = get_personalized_deals(user_validation["user_id"], **kwargs)
        return {
            "ok": True,
            "message": "Personalized deals loaded.",
            "best_deal": result["best_deal"],
            "deals": result["relevant_deals"],
            "signals": result["signals"],
        }


def _build_deal(item, average_price, discount_pct):
    return {
        "product_id": item["product_id"],
        "name": item["name"],
        "price": item["price"],
        "average_price": average_price,
        "discount_pct": round(discount_pct, 2),
        "source": item["source"],
        "url": item["url"],
        "score": _score_deal(
            discount_pct=discount_pct,
            average_price=average_price,
            current_price=item["price"],
            source=item["source"],
        ),
    }


def _extract_preference_terms(preferences):
    terms = set()
    for _, query, _ in preferences or []:
        for token in _tokenize_text(query):
            terms.add(token)
    return terms


def _extract_behavior_profile(behavior):
    if not behavior:
        return {
            "category_terms": set(),
            "excluded_terms": set(),
            "clicks": 0,
        }

    category = behavior[2] or ""
    clicks = int(behavior[5] or 0)
    excluded_category = behavior[7] or ""
    return {
        "category_terms": set(_tokenize_text(category)),
        "excluded_terms": set(_tokenize_text(excluded_category)),
        "clicks": clicks,
    }


def _build_user_profile(user_id, preferences, behavior_profile):
    recent_searches = get_recent_user_searches(user_id)
    recent_interactions = get_recent_user_interactions(user_id)
    clicked_products = []
    for interaction_type, query, raw_text, _ in recent_interactions:
        if interaction_type in {"message", "feedback_like", "feedback_dislike"}:
            value = query or raw_text
            if value:
                clicked_products.append(value)

    return {
        "preferences": [query for _, query, _ in preferences or []],
        "recent_searches": recent_searches,
        "clicked_products": clicked_products[:10],
        "behavior_categories": sorted(behavior_profile["category_terms"]),
        "excluded_categories": sorted(behavior_profile["excluded_terms"]),
        "clicks": behavior_profile["clicks"],
    }


def _calculate_personalization_boost(deal, preference_terms, behavior_profile):
    name_terms = set(_tokenize_text(deal.get("name", "")))
    interest_matches = name_terms.intersection(preference_terms)
    category_matches = name_terms.intersection(behavior_profile["category_terms"])
    excluded_matches = name_terms.intersection(behavior_profile["excluded_terms"])

    preference_boost = min(len(interest_matches) * 8.0, 20.0)
    behavior_boost = min(len(category_matches) * 10.0, 15.0)
    click_boost = 0.0
    if category_matches and behavior_profile["clicks"] > 0:
        click_boost = min(float(behavior_profile["clicks"]) * 1.5, 10.0)
    dislike_penalty = min(len(excluded_matches) * 18.0, 30.0)

    total_boost = round(preference_boost + behavior_boost + click_boost - dislike_penalty, 1)
    return {
        "personalization_boost": total_boost,
        "interest_matches": sorted(interest_matches),
        "category_matches": sorted(category_matches),
        "excluded_matches": sorted(excluded_matches),
    }


def _personalize_deal(deal, preference_terms, behavior_profile):
    boost_data = _calculate_personalization_boost(
        deal=deal,
        preference_terms=preference_terms,
        behavior_profile=behavior_profile,
    )
    return {
        **deal,
        **boost_data,
        "base_score": float(deal.get("score", 0)),
    }


def _apply_ai_personalization(user_profile, personalized_deal):
    ai_result = evaluate_deal_for_user(user_profile, personalized_deal)
    ai_score = round(
        max(
            0.0,
            min(
                float(ai_result.get("score", personalized_deal["base_score"]) or personalized_deal["base_score"]),
                100.0,
            ),
        ),
        1,
    )
    return {
        **personalized_deal,
        "ai_relevant": bool(ai_result.get("relevant", False)),
        "ai_reason": ai_result.get("reason", ""),
        "ai_score": ai_score,
        "score": ai_score,
    }


def _is_relevant_for_user(personalized_deal):
    if "ai_relevant" in personalized_deal:
        if not personalized_deal["ai_relevant"]:
            return False
        return True

    if personalized_deal.get("excluded_matches"):
        return False

    return bool(
        personalized_deal.get("interest_matches")
        or personalized_deal.get("category_matches")
        or personalized_deal.get("personalization_boost", 0) > 0
    )


def _select_high_quality_deals(deals, min_score, max_deals):
    high_quality_deals = [deal for deal in deals if deal["score"] >= float(min_score)]
    high_quality_deals.sort(
        key=lambda deal: (-deal["score"], -deal["discount_pct"], deal["price"])
    )
    return high_quality_deals[: int(max_deals)]


def find_profitable_deals(
    products,
    discount_threshold_pct=DEFAULT_DISCOUNT_THRESHOLD_PCT,
    min_price=MIN_PRICE_EUR,
    min_score=MIN_DEAL_SCORE,
    max_deals=MAX_DEALS_PER_RUN,
):
    grouped_products = _group_products_by_name(products, min_price=min_price)
    candidate_deals = []

    for _, items in grouped_products.items():
        if len(items) < MIN_GROUP_SIZE:
            continue

        average_price = _calculate_average_price(items)
        if average_price <= 0:
            continue

        for item in items:
            discount_pct = ((average_price - item["price"]) / average_price) * 100
            if discount_pct < float(discount_threshold_pct):
                continue

            candidate_deals.append(
                _build_deal(
                    item=item,
                    average_price=average_price,
                    discount_pct=discount_pct,
                )
            )

    return _select_high_quality_deals(
        deals=candidate_deals,
        min_score=min_score,
        max_deals=max_deals,
    )


def run_auto_deal_scan(
    load_from_adapters=False,
    discount_threshold_pct=DEFAULT_DISCOUNT_THRESHOLD_PCT,
    duplicate_window_hours=DEFAULT_DUPLICATE_WINDOW_HOURS,
    min_price=MIN_PRICE_EUR,
    min_score=MIN_DEAL_SCORE,
    max_deals=MAX_DEALS_PER_RUN,
):
    init_db()
    product_service = ProductService()

    if load_from_adapters:
        product_service.load_products(query="")

    products = product_service.search(query="")
    detected_deals = find_profitable_deals(
        products=products,
        discount_threshold_pct=discount_threshold_pct,
        min_price=min_price,
        min_score=min_score,
        max_deals=max_deals,
    )
    stored_deals = create_detected_deals(
        detected_deals,
        duplicate_window_hours=duplicate_window_hours,
    )
    notifications_sent = notify_new_deals(stored_deals) if stored_deals else 0

    return {
        "products_scanned": len(products),
        "deals_found": len(detected_deals),
        "deals_stored": len(stored_deals),
        "notifications_sent": notifications_sent,
        "deals": detected_deals,
        "stored_deals": stored_deals,
    }


def get_personalized_deals(
    user_id,
    discount_threshold_pct=DEFAULT_DISCOUNT_THRESHOLD_PCT,
    min_price=MIN_PRICE_EUR,
    min_score=MIN_DEAL_SCORE,
    max_deals=MAX_DEALS_PER_RUN,
    max_relevant_deals=MAX_PERSONALIZED_DEALS,
    use_ai=True,
):
    init_db()
    product_service = ProductService()
    base_deals = find_profitable_deals(
        products=product_service.search(query=""),
        discount_threshold_pct=discount_threshold_pct,
        min_price=min_price,
        min_score=min_score,
        max_deals=max_deals,
    )

    preferences = get_user_preferences(user_id)
    behavior = get_user_behavior(user_id)
    preference_terms = _extract_preference_terms(preferences)
    behavior_profile = _extract_behavior_profile(behavior)
    user_profile = _build_user_profile(user_id, preferences, behavior_profile)

    personalized_deals = [
        _personalize_deal(
            deal=deal,
            preference_terms=preference_terms,
            behavior_profile=behavior_profile,
        )
        for deal in base_deals
    ]
    personalized_deals = [
        _apply_ai_personalization(user_profile, deal) if use_ai else deal
        for deal in personalized_deals
    ]
    personalized_deals = [
        deal
        for deal in personalized_deals
        if _is_relevant_for_user(deal) and float(deal.get("score", 0) or 0) >= float(min_score)
    ]
    personalized_deals.sort(
        key=lambda deal: (-deal["score"], -deal["personalization_boost"], deal["price"])
    )
    relevant_deals = personalized_deals[: int(max_relevant_deals)]
    best_deal = relevant_deals[0] if relevant_deals else None

    return {
        "user_id": user_id,
        "best_deal": best_deal,
        "relevant_deals": relevant_deals,
        "signals": {
            "user_profile": user_profile,
            "preferences": sorted(preference_terms),
            "behavior_categories": sorted(behavior_profile["category_terms"]),
            "excluded_categories": sorted(behavior_profile["excluded_terms"]),
            "clicks": behavior_profile["clicks"],
        },
    }


def run_auto_deal_scan_loop(
    interval_seconds=300,
    load_from_adapters=False,
    discount_threshold_pct=DEFAULT_DISCOUNT_THRESHOLD_PCT,
    duplicate_window_hours=DEFAULT_DUPLICATE_WINDOW_HOURS,
    min_price=MIN_PRICE_EUR,
    min_score=MIN_DEAL_SCORE,
    max_deals=MAX_DEALS_PER_RUN,
):
    while True:
        run_auto_deal_scan(
            load_from_adapters=load_from_adapters,
            discount_threshold_pct=discount_threshold_pct,
            duplicate_window_hours=duplicate_window_hours,
            min_price=min_price,
            min_score=min_score,
            max_deals=max_deals,
        )
        time.sleep(interval_seconds)


def _print_scan_result(result):
    print(f"Products scanned: {result['products_scanned']}")
    print(f"Deals found: {result['deals_found']}")
    print(f"Deals stored: {result['deals_stored']}")
    print(f"Notifications sent: {result['notifications_sent']}")

    for deal in result["deals"]:
        print(
            f"- {deal['name']} | price={deal['price']} | avg={deal['average_price']} "
            f"| discount={deal['discount_pct']}% | score={deal['score']} | source={deal['source']}"
        )


if __name__ == "__main__":
    load_from_adapters = "--load-products" in sys.argv
    result = run_auto_deal_scan(load_from_adapters=load_from_adapters)
    _print_scan_result(result)
