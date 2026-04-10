import hashlib
import random

import streamlit as st

from database import (
    create_deal,
    create_alert,
    create_user,
    delete_alert,
    delete_product,
    delete_user,
    get_admin_analytics,
    get_all_deals,
    get_all_products,
    get_all_users,
    get_user_by_username,
    get_user_alerts,
    add_user_preference,
    get_user_preferences,
    get_user_behavior,
    insert_products,
    increment_funnel_stat,
    promote_user_to_admin,
    update_product_price,
    get_funnel_stats,
    update_user_behavior_click,
    update_user_behavior_deal,
)
from services.product_service import ProductService


service = ProductService()

translations = {
    "EN": {
        "title": "GlobalPlace",
        "search": "Search products",
        "load": "Load products",
        "search_btn": "Search",
        "seller": "Seller Dashboard",
        "add_product": "Add product",
        "price": "Price",
        "source": "Source",
        "profit": "Profit",
        "language": "Language",
        "navigation": "Navigation",
        "go_to": "Go to",
        "marketplace": "Marketplace",
        "no_products": "No products found.",
        "open": "Open",
        "loaded_products": "Loaded {count} products.",
        "load_failed": "Failed to load products: {err}",
        "search_failed": "Search failed: {err}",
        "seller_header": "Aleksandr | Profit: +{profit} EUR | Active listings: {count}",
        "avg_profit": "Average profit per product",
        "avg_sell_time": "Average time to sell",
        "best_product": "Best performing product",
        "worst_product": "Worst performing product",
        "days": "days",
        "my_products": "My Products",
        "no_db_products": "No products in database. Add products or load marketplace data.",
        "market": "Market",
        "optimize_price": "Optimize price",
        "find_better_deal": "Find better deal",
        "open_listing": "Open listing",
        "price_suggestion": "Suggested price for {name}: {price} EUR",
        "cheaper_found": "Found cheaper alternative for {name}: {price} EUR",
        "market_insights": "Market Insights",
        "product_name": "Product name",
        "url": "URL",
        "fill_required": "Please fill in product name and URL.",
        "added_ok": "Product '{name}' added successfully.",
        "add_failed": "Failed to add product: {err}",
        "seller_source": "Seller",
        "overpriced": "Overpriced",
        "underpriced": "Underpriced",
        "good": "Good",
        "active_listings": "Active listings",
        "insight_1": "📈 Demand for AirPods is rising",
        "insight_2": "📉 Nike prices are dropping",
        "insight_3": "🔥 Electronics category is trending",
        "insight_4": "🛒 Budget products convert faster this week",
        "insight_5": "📊 Mid-range listings are getting more clicks",
        "insight_6": "⚡ Listings with lower prices sell quicker",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "register_btn": "Register",
        "logout": "Logout",
        "logged_in_as": "Logged in as: {username}",
        "invalid_credentials": "Invalid username or password.",
        "register_success": "Registration successful. You can login now.",
        "user_exists": "Username already exists.",
        "auth_required": "Please login or register to continue.",
        "original": "Original",
        "new_price": "New",
        "you_saved": "You saved",
        "platform_fee": "Platform fee",
        "accept_deal": "Accept deal",
        "deal_saved": "Deal saved.",
        "admin_panel": "Admin Panel",
        "access_denied": "Access denied",
        "track_search": "Track this search",
        "track": "Track",
        "target_price_optional": "Target price (optional)",
        "alert_saved": "Alert saved.",
        "my_alerts": "My Alerts",
        "delete_alert": "Delete alert",
        "deal_found_tracked": "🔥 Deal found for your tracked item!",
    },
    "RU": {
        "title": "GlobalPlace",
        "search": "Поиск товаров",
        "load": "Загрузить товары",
        "search_btn": "Найти",
        "seller": "Панель продавца",
        "add_product": "Добавить товар",
        "price": "Цена",
        "source": "Источник",
        "profit": "Прибыль",
        "language": "Язык",
        "navigation": "Навигация",
        "go_to": "Перейти",
        "marketplace": "Маркетплейс",
        "no_products": "Товары не найдены.",
        "open": "Открыть",
        "loaded_products": "Загружено товаров: {count}.",
        "load_failed": "Ошибка загрузки товаров: {err}",
        "search_failed": "Ошибка поиска: {err}",
        "seller_header": "Aleksandr | Прибыль: +{profit} EUR | Активных объявлений: {count}",
        "avg_profit": "Средняя прибыль на товар",
        "avg_sell_time": "Среднее время продажи",
        "best_product": "Лучший товар",
        "worst_product": "Худший товар",
        "days": "дней",
        "my_products": "Мои товары",
        "no_db_products": "В базе нет товаров. Добавьте товар или загрузите данные маркетплейса.",
        "market": "Рынок",
        "optimize_price": "Оптимизировать цену",
        "find_better_deal": "Найти выгоднее",
        "open_listing": "Открыть объявление",
        "price_suggestion": "Рекомендованная цена для {name}: {price} EUR",
        "cheaper_found": "Найдена более дешевая альтернатива для {name}: {price} EUR",
        "market_insights": "Инсайты рынка",
        "product_name": "Название товара",
        "url": "URL",
        "fill_required": "Пожалуйста, заполните название товара и URL.",
        "added_ok": "Товар '{name}' успешно добавлен.",
        "add_failed": "Ошибка добавления товара: {err}",
        "seller_source": "Продавец",
        "overpriced": "Завышена",
        "underpriced": "Занижена",
        "good": "Хорошая",
        "active_listings": "Активные объявления",
        "insight_1": "📈 Спрос на AirPods растет",
        "insight_2": "📉 Цены на Nike снижаются",
        "insight_3": "🔥 Категория электроники в тренде",
        "insight_4": "🛒 Бюджетные товары продаются быстрее на этой неделе",
        "insight_5": "📊 Товары среднего сегмента получают больше кликов",
        "insight_6": "⚡ Объявления с низкой ценой продаются быстрее",
        "login": "Вход",
        "register": "Регистрация",
        "username": "Имя пользователя",
        "password": "Пароль",
        "login_btn": "Войти",
        "register_btn": "Зарегистрироваться",
        "logout": "Выйти",
        "logged_in_as": "Вы вошли как: {username}",
        "invalid_credentials": "Неверное имя пользователя или пароль.",
        "register_success": "Регистрация успешна. Теперь можно войти.",
        "user_exists": "Пользователь уже существует.",
        "auth_required": "Пожалуйста, войдите или зарегистрируйтесь.",
        "original": "Изначально",
        "new_price": "Новая цена",
        "you_saved": "Вы сэкономили",
        "platform_fee": "Комиссия платформы",
        "accept_deal": "Принять сделку",
        "deal_saved": "Сделка сохранена.",
        "admin_panel": "Панель администратора",
        "access_denied": "Доступ запрещен",
        "track_search": "Отслеживать этот поиск",
        "track": "Отслеживать",
        "target_price_optional": "Целевая цена (необязательно)",
        "alert_saved": "Алерт сохранен.",
        "my_alerts": "Мои алерты",
        "delete_alert": "Удалить алерт",
        "deal_found_tracked": "🔥 Найдена выгодная сделка по вашему отслеживанию!",
    },
}


def t(key):
    lang = st.session_state.get("lang", "EN")
    return translations[lang].get(key, key)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_user_type():
    clicks_find_cheaper = int(st.session_state.get("clicks_find_cheaper", 0))
    clicks_get_deal = int(st.session_state.get("clicks_get_deal", 0))
    deals_completed = int(st.session_state.get("deals_completed", 0))

    if clicks_get_deal > 2:
        user_type = "decisive"
    elif clicks_find_cheaper > 3 and deals_completed == 0:
        user_type = "hesitant"
    else:
        user_type = "browser"

    st.session_state["user_type"] = user_type
    return user_type


def render_products(products):
    if not products:
        st.info(t("no_products"))
        return

    for product in products:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"**{product['name']}**")
            col2.write(f"{product['price']} EUR")
            col3.write(product["source"])
            col4.link_button(t("open"), product["url"])


def get_external_products(query):
    external_products = []
    for adapter in service.adapters:
        external_products.extend(adapter.search_products(query))
    return external_products


def get_marketplace_products(query):
    db_products = service.search(query=query)
    external_products = get_external_products(query)
    normalized_external = []
    for idx, product in enumerate(external_products):
        normalized_external.append(
            {
                "id": product.get("id", -(idx + 1)),
                "name": product["name"],
                "price": product["price"],
                "url": product["url"],
                "source": product["source"],
                "image": product.get("image", ""),
                "user_id": None,
            }
        )
    return db_products + normalized_external


def run_ai_agent(user_id):
    prefs = get_user_preferences(user_id)
    if not prefs:
        st.session_state["ai_deals"] = []
        return

    user_clicks = int(st.session_state.get("user_find_cheaper_clicks", 0))
    candidates = get_marketplace_products("")

    deals_by_key = {}
    for _, pref_query, _ in prefs:
        q = (pref_query or "").strip().lower()
        if not q:
            continue
        for product in candidates:
            if q not in str(product.get("name", "")).lower():
                continue
            discount, discount_pct, reason = smart_discount(
                float(product["price"]), user_clicks, user_id=user_id
            )
            new_price = round(float(product["price"]) * (1 - discount), 2)
            saving = round(float(product["price"]) - new_price, 2)
            if new_price < float(product["price"]):
                key = (product.get("id"), q)
                deals_by_key[key] = {
                    "id": product.get("id", 0),
                    "name": product["name"],
                    "url": product.get("url", ""),
                    "source": product.get("source", ""),
                    "image": product.get("image", ""),
                    "original_price": float(product["price"]),
                    "new_price": new_price,
                    "saving": saving,
                    "discount_pct": discount_pct,
                    "reason": reason,
                }

    st.session_state["ai_deals"] = list(deals_by_key.values())


def render_ai_deals(user_id):
    ai_deals = st.session_state.get("ai_deals") or []
    if not ai_deals:
        return

    st.success("🔥 AI found deals for you!")
    user_type = get_user_type()
    for idx, deal in enumerate(ai_deals):
        with st.container():
            col_img, col_info = st.columns([1, 2.2])
            image_url = deal.get("image") or "https://via.placeholder.com/150"
            col_img.image(image_url, width=150)
            col_info.subheader(deal["name"])
            col_info.markdown(
                f"<div style='color:#9aa0a6; font-size:13px;'><s>{t('original')}: {deal['original_price']} EUR</s></div>",
                unsafe_allow_html=True,
            )
            col_info.markdown(
                f"<div style='color:#16a34a; font-size:28px; font-weight:800;'>{t('new_price')}: {deal['new_price']} EUR</div>",
                unsafe_allow_html=True,
            )
            save_pct = round((deal["saving"] / deal["original_price"]) * 100, 1) if deal["original_price"] > 0 else 0
            col_info.markdown(
                f"<div style='font-size:22px; font-weight:800;'>💰 {t('you_saved')} {deal['saving']}€ ({save_pct}%)</div>",
                unsafe_allow_html=True,
            )
            col_info.markdown(f"🤖 Discount: {deal.get('discount_pct', 0)}%")
            if user_type == "hesitant":
                col_info.markdown("🤖 AI analyzed multiple offers")
                col_info.markdown("✔ Recommended option")
            elif user_type == "browser":
                col_info.markdown(f"💰 {t('you_saved')} {deal['saving']}€")
                col_info.markdown("💡 Good deal right now")
            col_info.write(deal.get("reason", ""))

            if st.button("🔥 Get this deal", key=f"ai_get_{idx}_{deal.get('id',0)}", use_container_width=True):
                increment_funnel_stat("get_deal_clicks", 1)
                st.session_state["clicks_get_deal"] = int(st.session_state.get("clicks_get_deal", 0)) + 1
                update_user_behavior_click(user_id)
                saving, commission = calculate_commission(deal["original_price"], deal["new_price"])
                create_deal(
                    user_id=user_id,
                    product_id=int(deal.get("id") or 0),
                    original_price=deal["original_price"],
                    negotiated_price=deal["new_price"],
                    saving=saving,
                    commission=commission,
                )
                increment_funnel_stat("completed_deals", 1)
                st.session_state["deals_completed"] = int(st.session_state.get("deals_completed", 0)) + 1
                accepted_pct = (saving / deal["original_price"] * 100) if deal["original_price"] > 0 else 0
                update_user_behavior_deal(user_id, accepted_pct, product_category=None)
                st.success(f"🎉 Deal completed! {t('you_saved')} {saving}€")


def render_deal_block(product, user_id, key_prefix):
    user_clicks = int(st.session_state.get("user_find_cheaper_clicks", 0))
    discount, discount_pct, reason = smart_discount(
        float(product["price"]), user_clicks, user_id=user_id
    )
    better_deal = round(float(product["price"]) * (1 - discount), 2)
    saving, commission = calculate_commission(product["price"], better_deal)
    saving_pct = round((saving / product["price"]) * 100, 1) if product["price"] > 0 else 0
    cta_variant = st.session_state.get("ab_variant", "A")
    cta_text = "🔥 Get this deal" if cta_variant == "A" else f"💰 Save {saving}€ now"
    user_type = get_user_type()

    st.markdown(
        f"<div style='color:#9aa0a6; font-size:14px;'><s>{t('original')}: {product['price']} EUR</s></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:#16a34a; font-size:30px; font-weight:800;'>{t('new_price')}: {better_deal} EUR</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:16px; font-weight:700;'>🤖 Discount: {discount_pct}%</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:24px; font-weight:800;'>💰 {t('you_saved')} {saving}€ ({saving_pct}%)</div>",
        unsafe_allow_html=True,
    )
    if user_type == "hesitant":
        st.markdown("🤖 AI analyzed multiple offers")
        st.markdown("✔ Recommended option")
    elif user_type == "browser":
        st.markdown(f"💰 {t('you_saved')} {saving}€")
        st.markdown("💡 Good deal right now")
    st.write(reason)

    if st.button(cta_text, key=f"{key_prefix}_accept_{product['id']}", use_container_width=True):
        increment_funnel_stat("get_deal_clicks", 1)
        st.session_state["clicks_get_deal"] = int(st.session_state.get("clicks_get_deal", 0)) + 1
        update_user_behavior_click(user_id)
        create_deal(
            user_id=user_id,
            product_id=product["id"],
            original_price=product["price"],
            negotiated_price=better_deal,
            saving=saving,
            commission=commission,
        )
        increment_funnel_stat("completed_deals", 1)
        st.session_state["deals_completed"] = int(st.session_state.get("deals_completed", 0)) + 1
        accepted_pct = (saving / float(product["price"]) * 100) if float(product["price"]) > 0 else 0
        update_user_behavior_deal(user_id, accepted_pct, product_category=None)
        st.success(f"🎉 Deal completed! {t('you_saved')} {saving}€")


def marketplace_page():
    st.title(t("title"))
    query = st.text_input(t("search"))

    if "results" not in st.session_state:
        st.session_state["results"] = []

    current_user_id = st.session_state.get("user_id")
    user_type = get_user_type()
    st.write("User type:", user_type)
    if "ai_deals" not in st.session_state:
        st.session_state["ai_deals"] = []

    if st.session_state.get("ai_agent_autorun", True):
        run_ai_agent(current_user_id)

    if st.button(t("search_btn")):
        try:
            if query.strip():
                add_user_preference(current_user_id, query.strip())
            st.session_state["results"] = get_marketplace_products(query=query)
            run_ai_agent(current_user_id)
        except Exception as exc:
            st.error(t("search_failed").format(err=exc))

    render_ai_deals(current_user_id)
    st.subheader(t("track_search"))
    with st.form("track_search_form"):
        track_query = st.text_input(t("search"), value=query or "", key="track_query_input")
        track_target_price = st.number_input(
            t("target_price_optional"),
            min_value=0.0,
            value=0.0,
            step=1.0,
        )
        track_submitted = st.form_submit_button(t("track"))
    if track_submitted and track_query.strip():
        target_price_value = float(track_target_price) if track_target_price > 0 else None
        create_alert(current_user_id, track_query.strip(), target_price_value)
        st.success(t("alert_saved"))

    alerts = get_user_alerts(current_user_id)
    st.subheader(t("my_alerts"))
    if alerts:
        for alert in alerts:
            alert_id, alert_query, alert_target_price, _ = alert
            with st.container():
                a1, a2, a3 = st.columns([3, 2, 1.2])
                a1.write(alert_query)
                a2.write("-" if alert_target_price is None else f"{alert_target_price} EUR")
                if a3.button(t("delete_alert"), key=f"delete_alert_{alert_id}"):
                    delete_alert(alert_id, current_user_id)
                    st.rerun()

    if not st.session_state["results"]:
        return

    has_alert_match = False
    for idx, product in enumerate(st.session_state["results"]):
        product_name_lower = product["name"].lower()
        for alert in alerts:
            _, alert_query, alert_target_price, _ = alert
            if alert_query.lower() in product_name_lower:
                if alert_target_price is None or product["price"] <= alert_target_price:
                    has_alert_match = True
                    break

        with st.container():
            col_img, col_info = st.columns([1, 2.2])
            image_url = product.get("image") or "https://via.placeholder.com/150"
            col_img.image(image_url, width=150)
            col_info.subheader(product["name"])
            col_info.markdown(
                f"<div style='color:#9aa0a6; font-size:13px;'><s>{t('original')}: {product['price']} EUR</s></div>",
                unsafe_allow_html=True,
            )
            user_clicks = int(st.session_state.get("user_find_cheaper_clicks", 0))
            preview_discount, preview_discount_pct, preview_reason = smart_discount(
                float(product["price"]), user_clicks, user_id=current_user_id
            )
            preview_new = round(float(product["price"]) * (1 - preview_discount), 2)
            preview_save = round(float(product["price"]) - preview_new, 2)
            preview_pct = round((preview_save / product["price"]) * 100, 1) if product["price"] > 0 else 0
            col_info.markdown(
                f"<div style='color:#16a34a; font-size:28px; font-weight:800;'>{t('new_price')}: {preview_new} EUR</div>",
                unsafe_allow_html=True,
            )
            col_info.markdown(
                f"<div style='font-size:15px; font-weight:700;'>🤖 Discount: {preview_discount_pct}%</div>",
                unsafe_allow_html=True,
            )
            col_info.write(preview_reason)
            col_info.markdown(
                f"<div style='font-size:22px; font-weight:800;'>💰 {t('you_saved')} {preview_save}€ ({preview_pct}%)</div>",
                unsafe_allow_html=True,
            )
            col_info.write(f"{t('source')}: {product['source']}")
            if user_type == "hesitant":
                col_info.markdown("🤖 AI analyzed multiple offers")
                col_info.markdown("✔ Recommended option")
            elif user_type == "browser":
                col_info.markdown(f"💰 {t('you_saved')} {preview_save}€")
                col_info.markdown("💡 Good deal right now")
            action_col1, action_col2 = col_info.columns([1, 1.6])
            action_col1.link_button(t("open"), product["url"])
            if action_col2.button(t("find_better_deal"), key=f"market_deal_{idx}_{product['id']}", use_container_width=True):
                increment_funnel_stat("find_cheaper_clicks", 1)
                st.session_state["clicks_find_cheaper"] = int(st.session_state.get("clicks_find_cheaper", 0)) + 1
                st.session_state["user_find_cheaper_clicks"] = int(
                    st.session_state.get("user_find_cheaper_clicks", 0)
                ) + 1
                update_user_behavior_click(current_user_id)
                render_deal_block(product, current_user_id, "market")
    if has_alert_match:
        st.success(t("deal_found_tracked"))


def get_market_average(price):
    fluctuation = random.uniform(-0.1, 0.1)
    return round(price * (1 + fluctuation), 2)


def get_status(price, market_price):
    if price > market_price * 1.05:
        return t("overpriced")
    if price < market_price * 0.95:
        return t("underpriced")
    return t("good")


def calculate_profit(price):
    return round(price - (price * 0.8), 2)


def calculate_commission(original_price, negotiated_price):
    saving = original_price - negotiated_price

    if saving <= 0:
        return 0, 0

    mode = st.session_state.get("commission_mode", "basic")
    custom_percent = st.session_state.get("commission_percent", 10.0) / 100.0

    if mode == "advanced":
        commission = saving * custom_percent
    else:
        if saving < 20:
            commission = saving * 0.05
        elif saving < 100:
            commission = saving * 0.10
        else:
            commission = saving * 0.15

    return round(saving, 2), round(commission, 2)


def smart_discount(price, user_clicks, user_id=None):
    if price < 50:
        base = 0.05
    elif price < 200:
        base = 0.10
    elif price < 500:
        base = 0.15
    else:
        base = 0.20

    boost = 0.05 if user_clicks >= 2 else 0.0
    behavior_adjustment = 0.0

    if user_id is not None:
        behavior = get_user_behavior(user_id)
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
    return discount, round(discount * 100, 0), reason


def admin_panel_page():
    if st.session_state.get("user_role") != "admin":
        st.error(t("access_denied"))
        return

    st.title(t("admin_panel"))

    st.subheader("Analytics")
    analytics = get_admin_analytics()
    metrics_cols = st.columns(4)
    metrics_cols[0].metric("Total users", analytics["total_users"])
    metrics_cols[1].metric("Total products", analytics["total_products"])
    metrics_cols[2].metric("Total deals", analytics["total_deals"])
    metrics_cols[3].metric("Total revenue", f"{analytics['total_revenue']} EUR")

    st.subheader("Conversion Funnel")
    funnel = get_funnel_stats()
    visits = funnel["visits"]
    step2 = funnel["find_cheaper_clicks"]
    step3 = funnel["get_deal_clicks"]
    step4 = funnel["completed_deals"]

    fcols = st.columns(4)
    fcols[0].metric("Visits", visits)
    fcols[1].metric("Clicked Find Cheaper", step2)
    fcols[2].metric("Clicked Get Deal", step3)
    fcols[3].metric("Completed Deals", step4)

    def rate(a, b):
        return 0.0 if a <= 0 else round((b / a) * 100, 1)

    r12 = rate(visits, step2)
    r23 = rate(step2, step3)
    r34 = rate(step3, step4)

    rcols = st.columns(3)
    rcols[0].metric("Step 1 → 2", f"{r12}%")
    rcols[1].metric("Step 2 → 3", f"{r23}%")
    rcols[2].metric("Step 3 → 4", f"{r34}%")

    drop12 = 0.0 if visits <= 0 else (1 - (step2 / visits)) * 100
    drop23 = 0.0 if step2 <= 0 else (1 - (step3 / step2)) * 100
    drop34 = 0.0 if step3 <= 0 else (1 - (step4 / step3)) * 100

    drops = [("Step 1 → 2", drop12), ("Step 2 → 3", drop23), ("Step 3 → 4", drop34)]
    worst_step, worst_drop = max(drops, key=lambda x: x[1])
    if worst_drop > 50:
        st.warning(f"⚠️ High drop-off at this step: {worst_step} ({round(worst_drop, 1)}%)")

    st.subheader("Commission controls")
    st.session_state["commission_mode"] = st.radio(
        "Commission mode",
        ["basic", "advanced"],
        index=0 if st.session_state.get("commission_mode", "basic") == "basic" else 1,
        horizontal=True,
    )
    st.session_state["commission_percent"] = st.number_input(
        "Commission percent (advanced)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.get("commission_percent", 10.0)),
        step=1.0,
    )

    st.subheader("Users management")
    users = get_all_users()
    st.dataframe(
        [{"id": u[0], "username": u[1], "role": u[2], "created_at": u[3]} for u in users],
        use_container_width=True,
    )
    for user in users:
        user_id, username, role, _ = user
        with st.container():
            c1, c2, c3 = st.columns([3, 1.3, 1.3])
            c1.write(f"#{user_id} {username} ({role})")
            if role != "admin":
                if c2.button("Promote to admin", key=f"promote_{user_id}"):
                    promote_user_to_admin(user_id)
                    st.rerun()
            else:
                c2.write("admin")

            current_user_id = st.session_state.get("user_id")
            if user_id != current_user_id:
                if c3.button("Delete user", key=f"delete_user_{user_id}"):
                    delete_user(user_id)
                    st.rerun()
            else:
                c3.write("self")

    st.subheader("Products management")
    products = get_all_products()
    st.dataframe(
        [
            {
                "id": p[0],
                "name": p[1],
                "price": p[2],
                "url": p[3],
                "source": p[4],
                "image": p[5],
                "user_id": p[6],
                "created_at": p[7],
            }
            for p in products
        ],
        use_container_width=True,
    )
    for product in products:
        product_id, name, price = product[0], product[1], product[2]
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1.2])
            c1.write(f"#{product_id} {name}")
            new_price = c2.number_input(
                "Edit price",
                min_value=0.0,
                value=float(price),
                step=1.0,
                key=f"price_edit_{product_id}",
            )
            if c2.button("Save price", key=f"save_price_{product_id}"):
                update_product_price(product_id, float(new_price))
                st.rerun()
            if c3.button("Delete product", key=f"delete_product_{product_id}"):
                delete_product(product_id)
                st.rerun()

    st.subheader("Deals management")
    deals = get_all_deals()
    st.dataframe(
        [
            {
                "id": d[0],
                "product_id": d[1],
                "user_id": d[2],
                "original_price": d[3],
                "negotiated_price": d[4],
                "saving": d[5],
                "commission": d[6],
                "date": d[7],
            }
            for d in deals
        ],
        use_container_width=True,
    )


def seller_dashboard_page():
    st.title(t("seller"))

    user_id = st.session_state.get("user_id")
    products = service.search("", user_id=user_id)

    enriched_products = []
    for product in products:
        market_avg = get_market_average(product["price"])
        profit = calculate_profit(product["price"])
        status = get_status(product["price"], market_avg)
        enriched_products.append(
            {
                **product,
                "market_avg": market_avg,
                "profit": profit,
                "status": status,
            }
        )

    total_profit = round(sum(p["profit"] for p in enriched_products), 2)
    active_listings = len(enriched_products)
    st.subheader(
        t("seller_header").format(profit=total_profit, count=active_listings)
    )

    if enriched_products:
        avg_profit = round(total_profit / len(enriched_products), 2)
        avg_time_to_sell = round(sum(random.randint(3, 21) for _ in enriched_products) / len(enriched_products), 1)
        best_product = max(enriched_products, key=lambda p: p["profit"])["name"]
        worst_product = min(enriched_products, key=lambda p: p["profit"])["name"]
    else:
        avg_profit = 0
        avg_time_to_sell = 0
        best_product = "-"
        worst_product = "-"

    metric_cols = st.columns(4)
    metric_cols[0].metric(t("avg_profit"), f"{avg_profit} EUR")
    metric_cols[1].metric(t("avg_sell_time"), f"{avg_time_to_sell} {t('days')}")
    metric_cols[2].metric(t("best_product"), best_product)
    metric_cols[3].metric(t("worst_product"), worst_product)

    st.subheader(t("my_products"))
    if not enriched_products:
        st.info(t("no_db_products"))
    else:
        for idx, product in enumerate(enriched_products):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1.3, 1.2, 1.1])
                col1.write(f"**{product['name']}**")
                col2.write(f"{product['price']} EUR")
                col3.write(f"{t('market')}: {product['market_avg']} EUR")
                col4.write(product["status"])
                col5.write(f"{t('profit')}: {product['profit']} EUR")

                action_col1, action_col2, action_col3 = st.columns([1.2, 1.2, 3])
                if action_col1.button(t("optimize_price"), key=f"opt_{idx}_{product['id']}"):
                    recommended_price = round(product["market_avg"] * 0.95, 2)
                    st.info(
                        t("price_suggestion").format(
                            name=product["name"], price=recommended_price
                        )
                    )
                if action_col2.button(t("find_better_deal"), key=f"deal_{idx}_{product['id']}"):
                    render_deal_block(product, user_id, "seller")
                action_col3.link_button(t("open_listing"), product["url"])

    st.subheader(t("market_insights"))
    insights_pool = [
        t("insight_1"),
        t("insight_2"),
        t("insight_3"),
        t("insight_4"),
        t("insight_5"),
        t("insight_6"),
    ]
    for insight in random.sample(insights_pool, k=min(5, len(insights_pool))):
        st.write(insight)

    if "show_add_product_form" not in st.session_state:
        st.session_state["show_add_product_form"] = False

    if st.button("+ Add product"):
        st.session_state["show_add_product_form"] = not st.session_state["show_add_product_form"]

    if st.session_state["show_add_product_form"]:
        st.subheader(t("add_product"))
        with st.form("add_product_form"):
            product_name = st.text_input(t("product_name"))
            product_price = st.number_input(t("price"), min_value=0.0, step=1.0)
            product_url = st.text_input(t("url"))
            image_url = st.text_input("Image URL")
            submitted = st.form_submit_button(t("add_product"))

        if submitted:
            if not product_name.strip() or not product_url.strip():
                st.error(t("fill_required"))
            else:
                try:
                    insert_products(
                        [
                            {
                                "name": product_name.strip(),
                                "price": float(product_price),
                                "url": product_url.strip(),
                                "source": t("seller_source"),
                                "image": image_url.strip(),
                                "user_id": user_id,
                            }
                        ],
                        user_id=user_id,
                    )
                    st.success(t("added_ok").format(name=product_name))
                except Exception as exc:
                    st.error(t("add_failed").format(err=exc))


def auth_page():
    st.title(t("title"))
    st.info(t("auth_required"))
    login_tab, register_tab = st.tabs([t("login"), t("register")])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input(t("username"), key="login_username")
            password = st.text_input(t("password"), type="password", key="login_password")
            submitted = st.form_submit_button(t("login_btn"))
        if submitted:
            user = get_user_by_username(username.strip())
            if user and user[2] == hash_password(password):
                st.session_state["user"] = user[1]
                st.session_state["user_id"] = user[0]
                st.session_state["user_role"] = user[3] or "user"
                st.rerun()
            else:
                st.error(t("invalid_credentials"))

    with register_tab:
        with st.form("register_form"):
            username = st.text_input(t("username"), key="register_username")
            password = st.text_input(t("password"), type="password", key="register_password")
            submitted = st.form_submit_button(t("register_btn"))
        if submitted:
            try:
                create_user(username.strip(), hash_password(password))
                st.success(t("register_success"))
            except Exception:
                st.error(t("user_exists"))


def main():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "EN"

    st.sidebar.selectbox(
        "Language",
        ["EN", "RU"],
        key="lang",
    )

    if "user" not in st.session_state or "user_id" not in st.session_state:
        auth_page()
        return

    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "user"
    if "commission_mode" not in st.session_state:
        st.session_state["commission_mode"] = "basic"
    if "commission_percent" not in st.session_state:
        st.session_state["commission_percent"] = 10.0
    if "ab_variant" not in st.session_state:
        st.session_state["ab_variant"] = random.choice(["A", "B"])
    if "clicks_find_cheaper" not in st.session_state:
        st.session_state["clicks_find_cheaper"] = 0
    if "clicks_get_deal" not in st.session_state:
        st.session_state["clicks_get_deal"] = 0
    if "deals_completed" not in st.session_state:
        st.session_state["deals_completed"] = 0
    if "counted_visit" not in st.session_state:
        st.session_state["counted_visit"] = True
        increment_funnel_stat("visits", 1)

    st.sidebar.title(t("navigation"))
    st.sidebar.write(t("logged_in_as").format(username=st.session_state["user"]))
    nav_items = [t("marketplace"), t("seller")]
    if st.session_state.get("user_role") == "admin":
        nav_items.append(t("admin_panel"))
    nav_items.append(t("logout"))
    page = st.sidebar.radio(t("go_to"), nav_items)

    if page == t("logout"):
        del st.session_state["user"]
        del st.session_state["user_id"]
        if "user_role" in st.session_state:
            del st.session_state["user_role"]
        st.rerun()
    elif page == t("marketplace"):
        marketplace_page()
    elif page == t("admin_panel"):
        admin_panel_page()
    else:
        seller_dashboard_page()


if __name__ == "__main__":
    main()