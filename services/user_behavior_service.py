from database import (
    update_user_behavior_click,
    update_user_behavior_deal,
    update_user_behavior_feedback,
)


CATEGORY_KEYWORDS = {
    "phones": ["iphone", "samsung", "pixel", "oneplus", "smartphone", "phone", "galaxy"],
    "headphones": ["airpods", "sony", "bose", "sennheiser", "jabra", "headphones"],
    "laptops": ["macbook", "dell", "lenovo", "thinkpad", "spectre", "laptop"],
    "electronics": ["camera", "tv", "smartwatch", "hub", "vr", "electronic"],
}


def infer_product_category(product_name):
    normalized_name = str(product_name or "").strip().lower()
    if not normalized_name:
        return None

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_name for keyword in keywords):
            return category

    tokens = [token for token in normalized_name.split() if len(token) >= 4]
    return tokens[0] if tokens else None


def track_user_product_click(user_id, product_name):
    product_category = infer_product_category(product_name)
    return update_user_behavior_click(user_id, product_category=product_category)


def track_user_product_deal(user_id, product_name, accepted_discount_pct):
    product_category = infer_product_category(product_name)
    return update_user_behavior_deal(
        user_id,
        accepted_discount_pct,
        product_category=product_category,
    )


def track_user_feedback(user_id, product_name, liked):
    product_category = infer_product_category(product_name)
    return update_user_behavior_feedback(
        user_id,
        product_category=product_category,
        liked=liked,
    )
