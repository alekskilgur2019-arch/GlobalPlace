import json
import os

from openai import OpenAI


DEFAULT_AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


def generate_ai_deals(preferences, products, build_preview):
    deals_by_key = {}

    for preference in preferences or []:
        if isinstance(preference, dict):
            query = preference.get("query")
        elif isinstance(preference, (list, tuple)) and len(preference) >= 2:
            query = preference[1]
        else:
            query = preference

        normalized_query = str(query or "").strip().lower()
        if not normalized_query:
            continue

        for product in products or []:
            if normalized_query not in str(product.get("name", "")).lower():
                continue

            preview_response = build_preview(product)
            if not preview_response or not preview_response.get("ok"):
                continue

            preview = preview_response["deal"]
            if float(preview["new_price"]) >= float(product["price"]):
                continue

            key = (product.get("id"), normalized_query)
            deals_by_key[key] = {
                "id": product.get("id", 0),
                "name": product["name"],
                "url": product.get("url", ""),
                "source": product.get("source", ""),
                "image": product.get("image", ""),
                "original_price": preview["original_price"],
                "new_price": preview["new_price"],
                "saving": preview["saving"],
                "saving_pct": preview["saving_pct"],
                "discount_pct": preview["discount_pct"],
                "score": preview["score"],
                "reason": preview["reason"],
            }

    return list(deals_by_key.values())


def _fallback_evaluation(deal):
    base_score = float(deal.get("score", 0) or 0)
    return {
        "relevant": base_score >= 60.0,
        "score": round(max(0.0, min(base_score, 100.0)), 1),
        "reason": "Fallback scoring based on existing recommendation logic.",
    }


def _fallback_notification_decision(user_profile, deal):
    score = float(deal.get("score", 0) or 0)
    has_interest = bool(
        user_profile.get("preferences")
        or user_profile.get("recent_searches")
        or user_profile.get("clicked_products")
    )
    should_send = score >= 85.0 and has_interest
    return {
        "send": should_send,
        "priority": "high" if should_send else "low",
        "reason": "Fallback notification decision based on score and user interest signals.",
    }


def _build_user_message(user_profile, deal):
    payload = {
        "user_preferences": user_profile.get("preferences", []),
        "recent_searches": user_profile.get("recent_searches", []),
        "clicked_products": user_profile.get("clicked_products", []),
        "deal": {
            "name": deal.get("name"),
            "price": deal.get("price"),
            "average_price": deal.get("average_price"),
            "discount_pct": deal.get("discount_pct"),
            "source": deal.get("source"),
            "score": deal.get("score"),
            "url": deal.get("url"),
        },
    }
    return (
        "Evaluate whether this deal is relevant for the user.\n"
        "Return JSON only in this format:\n"
        '{"relevant": true, "score": 0, "reason": "short explanation"}\n\n'
        f"{json.dumps(payload, ensure_ascii=True)}"
    )


def _build_notification_message(user_profile, deal):
    payload = {
        "user_preferences": user_profile.get("preferences", []),
        "recent_searches": user_profile.get("recent_searches", []),
        "clicked_products": user_profile.get("clicked_products", []),
        "behavior_categories": user_profile.get("behavior_categories", []),
        "excluded_categories": user_profile.get("excluded_categories", []),
        "deal": {
            "name": deal.get("name"),
            "price": deal.get("price"),
            "score": deal.get("score"),
            "discount_pct": deal.get("discount_pct"),
            "source": deal.get("source"),
            "reason": deal.get("ai_reason") or deal.get("reason"),
            "url": deal.get("url"),
        },
    }
    return (
        "Decide whether this deal is important enough to notify the user about right now.\n"
        "Return JSON only in this format:\n"
        '{"send": true, "priority": "high", "reason": "short explanation"}\n\n'
        f"{json.dumps(payload, ensure_ascii=True)}"
    )


def _parse_ai_response(response):
    content = getattr(response, "output_text", "") or ""
    parsed = json.loads(content)
    return {
        "relevant": bool(parsed.get("relevant", False)),
        "score": round(float(parsed.get("score", 0) or 0), 1),
        "reason": str(parsed.get("reason", "")).strip() or "AI evaluation completed.",
    }


def _parse_notification_response(response):
    content = getattr(response, "output_text", "") or ""
    parsed = json.loads(content)
    priority = str(parsed.get("priority", "low")).strip().lower()
    if priority not in {"high", "medium", "low"}:
        priority = "low"
    return {
        "send": bool(parsed.get("send", False)),
        "priority": priority,
        "reason": str(parsed.get("reason", "")).strip() or "AI notification decision completed.",
    }


def evaluate_deal_for_user(user_profile, deal):
    try:
        client = OpenAI()
        response = client.responses.create(
            model=DEFAULT_AI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are a recommendation engine. "
                                "Your job is to decide if a product is relevant for a user."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_user_message(user_profile, deal),
                        }
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "deal_recommendation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "relevant": {"type": "boolean"},
                            "score": {"type": "number"},
                            "reason": {"type": "string"},
                        },
                        "required": ["relevant", "score", "reason"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        result = _parse_ai_response(response)
        result["score"] = round(max(0.0, min(result["score"], 100.0)), 1)
        return result
    except Exception:
        return _fallback_evaluation(deal)


def should_send_deal(user_profile, deal):
    try:
        client = OpenAI()
        response = client.responses.create(
            model=DEFAULT_AI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are a notification decision engine. "
                                "Decide whether a user should be notified about a deal right now."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_notification_message(user_profile, deal),
                        }
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "deal_notification_decision",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "send": {"type": "boolean"},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                            "reason": {"type": "string"},
                        },
                        "required": ["send", "priority", "reason"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        return _parse_notification_response(response)
    except Exception:
        return _fallback_notification_decision(user_profile, deal)
