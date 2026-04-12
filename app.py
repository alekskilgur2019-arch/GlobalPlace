import hashlib
import random

import streamlit as st

from controllers.admin_users_controller import AdminUsersController
from controllers.admin_products_controller import AdminProductsController
from controllers.analytics_controller import AnalyticsController
from controllers.alerts_controller import AlertsController
from controllers.auth_controller import AuthController
from controllers.deals_controller import DealsController
from controllers.funnel_controller import FunnelController
from controllers.notification_controller import NotificationController
from controllers.product_search_controller import ProductSearchController
from controllers.seller_dashboard_controller import SellerDashboardController
from controllers.seller_products_controller import SellerProductsController
from controllers.user_profile_controller import UserProfileController
from services.search import get_original_query_for_display
from services.product_service import ProductService


service = ProductService()
product_search_controller = ProductSearchController()
analytics_controller = AnalyticsController()
admin_users_controller = AdminUsersController()
admin_products_controller = AdminProductsController()
alerts_controller = AlertsController()
auth_controller = AuthController()
deals_controller = DealsController()
funnel_controller = FunnelController()
notification_controller = NotificationController()
seller_dashboard_controller = SellerDashboardController()
seller_products_controller = SellerProductsController()
user_profile_controller = UserProfileController()

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
        "alerts_page": "Alerts",
        "ai_deals_page": "AI Deals",
        "profile_page": "Profile",
        "seller_entry": "Seller panel",
        "become_seller": "Become a seller",
        "seller_verification_required": "Seller access requires email verification.",
        "seller_verification_pending": "Seller verification is not available yet in self-service.",
        "telegram_settings": "Telegram settings",
        "telegram_connected": "Telegram connected.",
        "telegram_not_connected": "Telegram is not connected yet.",
        "connect_telegram": "Get Telegram notifications",
        "connect_telegram_help": "Open the bot and press Start. This link expires in 15 minutes.",
        "telegram_connect_failed": "Telegram connection link is unavailable right now.",
        "telegram_manual_fallback": "Manual Telegram setup (fallback)",
        "telegram_chat_id": "Telegram chat ID",
        "save_telegram": "Save Telegram",
        "send_test_message": "Send test message",
        "enter_product_name": "Enter a product name.",
        "search_not_found_title": "I couldn't find {query}.",
        "search_not_found_help": "You can track this item and get informed when it appears.",
        "track_this_item": "Track this item",
        "already_tracking_item": "You are already tracking this item.",
        "already_tracking_item_connected": "Telegram is already connected. You will receive notifications if a matching item appears.",
        "already_tracking_item_not_connected": "This item is already being tracked, but Telegram is not connected yet.",
        "connect_telegram_for_alerts": "Connect Telegram to receive notifications.",
        "open_profile_telegram": "Open Telegram settings",
        "best_offer": "Best offer",
        "other_offers": "Other offers",
        "best_offer_badge": "Best offer right now",
        "product_family_empty": "No offers found for this product family.",
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
        "alerts_page": "Алерты",
        "ai_deals_page": "AI сделки",
        "profile_page": "Профиль",
        "seller_entry": "Панель продавца",
        "become_seller": "Стать продавцом",
        "seller_verification_required": "Для доступа продавца требуется подтверждение email.",
        "seller_verification_pending": "Самостоятельная верификация продавца пока недоступна.",
        "telegram_settings": "Настройки Telegram",
        "telegram_connected": "Telegram подключён.",
        "telegram_not_connected": "Telegram пока не подключён.",
        "connect_telegram": "Получать уведомления в Telegram",
        "connect_telegram_help": "Откройте бота и нажмите Start. Ссылка действует 15 минут.",
        "telegram_connect_failed": "Ссылка для подключения Telegram сейчас недоступна.",
        "telegram_manual_fallback": "Ручная настройка Telegram (запасной вариант)",
        "telegram_chat_id": "Telegram chat ID",
        "save_telegram": "Сохранить Telegram",
        "send_test_message": "Отправить тестовое сообщение",
        "enter_product_name": "Введите название товара.",
        "search_not_found_title": "Я не смог найти {query}.",
        "search_not_found_help": "Вы можете отслеживать этот товар и узнать, когда он появится.",
        "track_this_item": "Отслеживать этот товар",
        "already_tracking_item": "Вы уже отслеживаете этот товар.",
        "already_tracking_item_connected": "Telegram уже подключён. Вы получите уведомление, если появится подходящий товар.",
        "already_tracking_item_not_connected": "Этот товар уже отслеживается, но Telegram пока не подключён.",
        "connect_telegram_for_alerts": "Подключите Telegram, чтобы получать уведомления.",
        "open_profile_telegram": "Открыть настройки Telegram",
        "best_offer": "Лучшее предложение",
        "other_offers": "Другие предложения",
        "best_offer_badge": "Лучшее предложение сейчас",
        "product_family_empty": "Для этой товарной семьи предложения не найдены.",
    },
}


def t(key):
    lang = st.session_state.get("lang", "EN")
    return translations[lang].get(key, key)


def render_open_button(product, user_id, key):
    product_url = str(product.get("url") or "").strip()
    if not product_url:
        return
    st.link_button(
        t("open"),
        product_url,
        use_container_width=True,
    )
def render_telegram_connect_link(connect_url):
    if not connect_url:
        return

    st.markdown(
        (
            f'<a href="{connect_url}" target="_blank" '
            'style="display:block; width:100%; text-align:center; '
            'padding:0.7rem 1rem; border-radius:0.5rem; '
            'background:#1f6feb; color:#ffffff; text-decoration:none; '
            'font-weight:600;">'
            f'{t("connect_telegram")}</a>'
        ),
        unsafe_allow_html=True,
    )


def render_alert_creation_feedback(create_alert_response, user_id, connect_key_suffix):
    if create_alert_response["ok"]:
        st.success(t("alert_saved"))
        return

    if not create_alert_response.get("duplicate"):
        st.error(create_alert_response["message"])
        return

    st.info(t("already_tracking_item"))
    telegram_status = user_profile_controller.get_telegram_connection_status(user_id)
    if telegram_status.get("connected"):
        st.caption(t("already_tracking_item_connected"))
        return

    st.caption(t("already_tracking_item_not_connected"))
    st.caption(t("connect_telegram_for_alerts"))
    connect_response = user_profile_controller.get_or_create_telegram_connect_link(user_id)
    if connect_response["ok"] and connect_response.get("connect_url"):
        render_telegram_connect_link(connect_response["connect_url"])
        return

    if st.button(
        t("open_profile_telegram"),
        key=f"open_profile_telegram_alert_{connect_key_suffix}",
        use_container_width=True,
    ):
        st.session_state["current_page"] = "profile"
        st.rerun()


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


def get_commission_settings():
    return {
        "commission_mode": st.session_state.get("commission_mode", "basic"),
        "commission_percent": float(st.session_state.get("commission_percent", 10.0)),
    }


def render_products(products):
    if not products:
        st.info(t("no_products"))
        return

    current_user_id = st.session_state.get("user_id")
    for index, product in enumerate(products):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"**{product.get('display_name') or product['name']}**")
            col2.write(f"{product['price']} EUR")
            col3.write(product["source"])
            with col4:
                render_open_button(product, current_user_id, key=f"open_list_{index}_{product['id']}")


def get_marketplace_products(query):
    response = product_search_controller.search_products(query=query)
    return response["results"]

def render_ai_deals(user_id):
    ai_deals = st.session_state.get("ai_deals") or []
    if not ai_deals:
        return

    st.success("🔥 AI found deals for you!")
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

            if st.button("🔥 Get this deal", key=f"ai_get_{idx}_{deal.get('id',0)}", use_container_width=True):
                funnel_controller.increment_stat("get_deal_clicks", 1)
                st.session_state["clicks_get_deal"] = int(st.session_state.get("clicks_get_deal", 0)) + 1
                commission_settings = get_commission_settings()
                accept_result = deals_controller.accept_deal(
                    user_id=user_id,
                    deal=deal,
                    commission_mode=commission_settings["commission_mode"],
                    commission_percent=commission_settings["commission_percent"],
                )
                if not accept_result["ok"]:
                    st.error(accept_result["message"])
                    continue
                saving = accept_result["saving"]
                funnel_controller.increment_stat("completed_deals", 1)
                st.session_state["deals_completed"] = int(st.session_state.get("deals_completed", 0)) + 1
                st.success(f"🎉 Deal completed! {t('you_saved')} {saving}€")


def render_top_deals(user_id):
    ai_deals = st.session_state.get("ai_deals") or []
    if not ai_deals:
        return

    top_deals = sorted(
        ai_deals,
        key=lambda deal: float(deal.get("score", 0) or 0),
        reverse=True,
    )[:5]
    if not top_deals:
        return

    previous_ai_deals = st.session_state.get("ai_deals")
    st.subheader("🔥 Top deals for you")
    st.session_state["ai_deals"] = top_deals
    render_ai_deals(user_id)
    st.session_state["ai_deals"] = previous_ai_deals


def render_deal_block(product, user_id, key_prefix):
    user_clicks = int(st.session_state.get("user_find_cheaper_clicks", 0))
    commission_settings = get_commission_settings()
    preview_response = deals_controller.get_deal_preview(
        product=product,
        user_clicks=user_clicks,
        user_id=user_id,
        commission_mode=commission_settings["commission_mode"],
        commission_percent=commission_settings["commission_percent"],
    )
    if not preview_response["ok"]:
        st.error(preview_response["message"])
        return

    preview = preview_response["deal"]
    better_deal = preview["negotiated_price"]
    saving = preview["saving"]
    saving_pct = preview["saving_pct"]
    cta_variant = st.session_state.get("ab_variant", "A")
    cta_text = "🔥 Get this deal" if cta_variant == "A" else f"💰 Save {saving}€ now"

    st.markdown(
        f"<div style='color:#9aa0a6; font-size:14px;'><s>{t('original')}: {product['price']} EUR</s></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:#16a34a; font-size:30px; font-weight:800;'>{t('new_price')}: {better_deal} EUR</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:24px; font-weight:800;'>💰 {t('you_saved')} {saving}€ ({saving_pct}%)</div>",
        unsafe_allow_html=True,
    )

    if st.button(cta_text, key=f"{key_prefix}_accept_{product['id']}", use_container_width=True):
        funnel_controller.increment_stat("get_deal_clicks", 1)
        st.session_state["clicks_get_deal"] = int(st.session_state.get("clicks_get_deal", 0)) + 1
        accept_result = deals_controller.accept_deal(
            user_id=user_id,
            deal=preview,
            commission_mode=commission_settings["commission_mode"],
            commission_percent=commission_settings["commission_percent"],
        )
        if not accept_result["ok"]:
            st.error(accept_result["message"])
            return
        funnel_controller.increment_stat("completed_deals", 1)
        st.session_state["deals_completed"] = int(st.session_state.get("deals_completed", 0)) + 1
        st.success(f"🎉 Deal completed! {t('you_saved')} {saving}€")


def alerts_page():
    st.title(t("alerts_page"))

    current_user_id = st.session_state.get("user_id")
    with st.form("alerts_page_track_search_form"):
        track_query = st.text_input(t("search"), key="alerts_page_query_input")
        track_target_price = st.number_input(
            t("target_price_optional"),
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="alerts_page_target_price_input",
        )
        track_submitted = st.form_submit_button(t("track"))

    if track_submitted and track_query.strip():
        target_price_value = float(track_target_price) if track_target_price > 0 else None
        create_alert_response = alerts_controller.create_alert(
            user_id=current_user_id,
            query=track_query.strip(),
            target_price=target_price_value,
        )
        render_alert_creation_feedback(
            create_alert_response=create_alert_response,
            user_id=current_user_id,
            connect_key_suffix="alerts_page",
        )

    alerts_response = alerts_controller.get_alerts(current_user_id)
    if not alerts_response["ok"]:
        st.error(alerts_response["message"])
        return

    alerts = alerts_response.get("alerts", [])
    st.subheader(t("my_alerts"))
    if not alerts:
        st.info("No alerts yet.")
        return

    for alert in alerts:
        alert_id = alert["id"]
        alert_query = alert["query"]
        alert_target_price = alert["target_price"]
        with st.container():
            a1, a2, a3 = st.columns([3, 2, 1.2])
            a1.write(alert_query)
            a2.write("-" if alert_target_price is None else f"{alert_target_price} EUR")
            if a3.button(t("delete_alert"), key=f"alerts_page_delete_{alert_id}"):
                delete_response = alerts_controller.delete_alert(
                    user_id=current_user_id,
                    alert_id=alert_id,
                )
                if delete_response["ok"]:
                    st.rerun()
                else:
                    st.error(delete_response["message"])


def ai_deals_page():
    st.title(t("ai_deals_page"))

    current_user_id = st.session_state.get("user_id")
    commission_settings = get_commission_settings()
    ai_deals_response = deals_controller.get_ai_deals(
        user_id=current_user_id,
        user_clicks=int(st.session_state.get("user_find_cheaper_clicks", 0)),
        commission_mode=commission_settings["commission_mode"],
        commission_percent=commission_settings["commission_percent"],
    )
    st.session_state["ai_deals"] = ai_deals_response.get("deals", [])

    render_top_deals(current_user_id)
    render_ai_deals(current_user_id)


def profile_page():
    st.title(t("profile_page"))

    st.write(t("logged_in_as").format(username=st.session_state["user"]))
    seller_access_response = user_profile_controller.get_seller_access_status(
        st.session_state.get("user_id")
    )
    seller_access_enabled = seller_access_response.get("seller_access_enabled", False)
    telegram_response = user_profile_controller.get_telegram_connection_status(
        st.session_state.get("user_id")
    )
    default_telegram_chat_id = telegram_response.get("telegram_chat_id", "")
    telegram_connected = telegram_response.get("connected", False)

    st.subheader(t("telegram_settings"))
    if telegram_connected:
        st.success(t("telegram_connected"))
        st.caption(default_telegram_chat_id)
    else:
        st.info(t("telegram_not_connected"))
        connect_response = user_profile_controller.get_or_create_telegram_connect_link(
            st.session_state.get("user_id")
        )
        if connect_response["ok"] and connect_response.get("connect_url"):
            render_telegram_connect_link(connect_response["connect_url"])
            st.caption(t("connect_telegram_help"))
        else:
            st.warning(
                connect_response.get("message") or t("telegram_connect_failed")
            )

    if telegram_connected:
        if st.button(
            t("send_test_message"),
            key="profile_send_telegram_test_message",
        ):
            test_response = user_profile_controller.send_telegram_test_message(
                st.session_state.get("user_id")
            )
            if test_response["ok"]:
                st.success(test_response["message"])
            else:
                st.error(test_response["message"])

    with st.expander(t("telegram_manual_fallback")):
        telegram_chat_id = st.text_input(
            t("telegram_chat_id"),
            value=default_telegram_chat_id,
            key="profile_telegram_chat_id_input",
        )
        if st.button(t("save_telegram"), key="profile_save_telegram_chat_id"):
            save_response = user_profile_controller.save_telegram_chat_id(
                st.session_state.get("user_id"),
                telegram_chat_id,
            )
            if save_response["ok"]:
                st.success(save_response["message"])
            else:
                st.error(save_response["message"])

    st.caption(t("become_seller"))
    if st.button(
        t("seller_entry"),
        key="profile_open_seller_panel",
        disabled=not seller_access_enabled,
    ):
        st.session_state["seller_mode_enabled"] = True
        st.session_state["current_page"] = "seller"
        st.rerun()
    if not seller_access_enabled:
        st.caption(t("seller_verification_required"))
        st.caption(t("seller_verification_pending"))

    st.subheader("Alert notifications")
    if st.button("Run Telegram alert check", key="profile_run_telegram_alert_check"):
        notification_result = notification_controller.notify_alert_matching_deals()
        if notification_result["ok"]:
            st.success(notification_result["message"])
            st.write(f"Users processed: {notification_result['users_processed']}")
            st.write(f"Matches found: {notification_result['matches_found']}")
            st.write(f"Notifications sent: {notification_result['notifications_sent']}")
        else:
            st.error(notification_result["message"])


def marketplace_page():
    st.title(t("title"))
    query = st.text_input(t("search"), key="marketplace_search_query")

    if "results" not in st.session_state:
        st.session_state["results"] = []
    if "last_marketplace_query" not in st.session_state:
        st.session_state["last_marketplace_query"] = ""
    if "last_marketplace_query_raw" not in st.session_state:
        st.session_state["last_marketplace_query_raw"] = ""

    current_user_id = st.session_state.get("user_id")
    if "ai_deals" not in st.session_state:
        st.session_state["ai_deals"] = []

    if st.button(t("search_btn")):
        try:
            original_query = get_original_query_for_display(query)
            if not original_query:
                st.session_state["results"] = []
                st.session_state["last_marketplace_query"] = ""
                st.session_state["last_marketplace_query_raw"] = ""
                st.info(t("enter_product_name"))
                return

            normalized_query = original_query
            user_profile_controller.add_search_preference(current_user_id, normalized_query)
            st.session_state["results"] = get_marketplace_products(query=normalized_query)
            st.session_state["last_marketplace_query"] = normalized_query
            st.session_state["last_marketplace_query_raw"] = original_query
        except Exception as exc:
            st.error(t("search_failed").format(err=exc))

    alerts_response = alerts_controller.get_alerts(current_user_id)
    alerts = alerts_response.get("alerts", [])

    if not st.session_state["results"]:
        last_marketplace_query = st.session_state.get("last_marketplace_query_raw", "").strip()
        if last_marketplace_query:
            st.info(t("search_not_found_title").format(query=last_marketplace_query))
            st.caption(t("search_not_found_help"))
            if st.button(t("track_this_item"), key="marketplace_track_missing_item"):
                create_alert_response = alerts_controller.create_alert(
                    user_id=current_user_id,
                    query=last_marketplace_query,
                    target_price=None,
                )
                render_alert_creation_feedback(
                    create_alert_response=create_alert_response,
                    user_id=current_user_id,
                    connect_key_suffix="marketplace_empty_state",
                )
        return

    render_products(st.session_state["results"])


def admin_panel_page():
    if st.session_state.get("user_role") != "admin":
        st.error(t("access_denied"))
        return

    st.title(t("admin_panel"))

    policy_response = notification_controller.get_notification_policy()
    policy = policy_response.get("policy", {})
    execution_settings_response = notification_controller.get_scan_execution_settings()
    execution_settings = execution_settings_response.get("settings", {})
    scheduled_run_status_response = notification_controller.get_scheduled_run_status()
    scheduled_run_status = scheduled_run_status_response.get("status", {})

    st.subheader("Notification policy")
    with st.form("notification_policy_form"):
        max_notifications_per_user = st.text_input(
            "Max notifications per user",
            value=""
            if policy.get("max_notifications_per_user") is None
            else str(policy["max_notifications_per_user"]),
            help="Leave empty to keep current unlimited behavior.",
        )
        cooldown_hours = st.text_input(
            "Cooldown hours",
            value=""
            if policy.get("cooldown_hours") is None
            else str(policy["cooldown_hours"]),
            help="Leave empty to keep current no-cooldown behavior.",
        )
        notification_policy_submitted = st.form_submit_button("Save notification policy")

    if notification_policy_submitted:
        save_policy_response = notification_controller.save_notification_policy(
            max_notifications_per_user=max_notifications_per_user,
            cooldown_hours=cooldown_hours,
        )
        if save_policy_response["ok"]:
            st.success(save_policy_response["message"])
            st.rerun()
        else:
            st.error(save_policy_response["message"])

    st.subheader("Alert scan execution")
    with st.form("scan_execution_settings_form"):
        auto_scan_enabled = st.checkbox(
            "Auto scan enabled",
            value=bool(execution_settings.get("auto_scan_enabled", False)),
        )
        scan_interval_minutes = st.text_input(
            "Scan interval minutes",
            value=str(execution_settings.get("scan_interval_minutes", 60)),
            help="Prepared for future cron integration. Manual scan still works independently.",
        )
        scan_execution_submitted = st.form_submit_button("Save scan execution settings")

    if scan_execution_submitted:
        save_execution_response = notification_controller.save_scan_execution_settings(
            auto_scan_enabled=auto_scan_enabled,
            scan_interval_minutes=scan_interval_minutes,
        )
        if save_execution_response["ok"]:
            st.success(save_execution_response["message"])
            st.rerun()
        else:
            st.error(save_execution_response["message"])

    st.subheader("Scheduled scan status")
    st.write(
        "Last scheduled run at:",
        scheduled_run_status.get("last_scheduled_run_at") or "-",
    )
    st.write(
        "Last scheduled run status:",
        scheduled_run_status.get("last_scheduled_run_status") or "-",
    )
    status_cols = st.columns(3)
    status_cols[0].metric(
        "Last users processed",
        scheduled_run_status.get("last_users_processed", 0),
    )
    status_cols[1].metric(
        "Last matches found",
        scheduled_run_status.get("last_matches_found", 0),
    )
    status_cols[2].metric(
        "Last notifications sent",
        scheduled_run_status.get("last_notifications_sent", 0),
    )
    last_error_message = scheduled_run_status.get("last_error_message") or ""
    if last_error_message:
        st.caption(f"Last error: {last_error_message}")

    st.subheader("Telegram alert notifications")
    if st.button("Run Telegram alert scan", key="admin_run_telegram_alert_scan"):
        notification_result = notification_controller.notify_alert_matching_deals()
        if notification_result["ok"]:
            st.success(notification_result["message"])
            st.write(f"Users processed: {notification_result['users_processed']}")
            st.write(f"Matches found: {notification_result['matches_found']}")
            st.write(f"Notifications sent: {notification_result['notifications_sent']}")
        else:
            st.error(notification_result["message"])

    st.subheader("Analytics")
    analytics_response = analytics_controller.get_admin_dashboard_analytics()
    analytics = analytics_response["overview"]
    metrics_cols = st.columns(4)
    metrics_cols[0].metric("Total users", analytics["total_users"])
    metrics_cols[1].metric("Total products", analytics["total_products"])
    metrics_cols[2].metric("Total deals", analytics["total_deals"])
    metrics_cols[3].metric("Total revenue", f"{analytics['total_revenue']} EUR")

    st.subheader("Conversion Funnel")
    funnel = analytics_response["funnel"]
    funnel_steps = funnel["steps"]
    visits = funnel_steps[0]["value"]
    step2 = funnel_steps[1]["value"]
    step3 = funnel_steps[2]["value"]
    step4 = funnel_steps[3]["value"]

    fcols = st.columns(4)
    fcols[0].metric("Visits", visits)
    fcols[1].metric("Clicked Find Cheaper", step2)
    fcols[2].metric("Clicked Get Deal", step3)
    fcols[3].metric("Completed Deals", step4)

    transitions = funnel["transitions"]
    r12 = transitions[0]["conversion_rate"]
    r23 = transitions[1]["conversion_rate"]
    r34 = transitions[2]["conversion_rate"]

    rcols = st.columns(3)
    rcols[0].metric("Step 1 → 2", f"{r12}%")
    rcols[1].metric("Step 2 → 3", f"{r23}%")
    rcols[2].metric("Step 3 → 4", f"{r34}%")

    worst_transition = funnel["worst_transition"]
    if worst_transition and worst_transition["drop_off_rate"] > 50:
        st.warning(
            "⚠️ High drop-off at this step: "
            f"{worst_transition['label']} ({worst_transition['drop_off_rate']}%)"
        )

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
    users_response = admin_users_controller.get_users()
    if not users_response["ok"]:
        st.error(users_response["message"])
        return

    users = users_response.get("users", [])
    st.dataframe(
        users,
        use_container_width=True,
    )
    for user in users:
        user_id = user["id"]
        username = user["username"]
        role = user["role"]
        with st.container():
            c1, c2, c3 = st.columns([3, 1.3, 1.3])
            c1.write(f"#{user_id} {username} ({role})")
            if role != "admin":
                if c2.button("Promote to admin", key=f"promote_{user_id}"):
                    promote_result = admin_users_controller.promote_user(
                        acting_admin_user_id=st.session_state.get("user_id"),
                        target_user_id=user_id,
                    )
                    if promote_result["ok"]:
                        st.rerun()
                    else:
                        st.error(promote_result["message"])
            else:
                c2.write("admin")

            current_user_id = st.session_state.get("user_id")
            if user_id != current_user_id:
                if c3.button("Delete user", key=f"delete_user_{user_id}"):
                    delete_result = admin_users_controller.delete_user(
                        acting_admin_user_id=current_user_id,
                        target_user_id=user_id,
                    )
                    if delete_result["ok"]:
                        st.rerun()
                    else:
                        st.error(delete_result["message"])
            else:
                c3.write("self")

    st.subheader("Products management")
    products_response = admin_products_controller.get_products()
    products = products_response.get("products", [])
    st.dataframe(
        products,
        use_container_width=True,
    )
    for product in products:
        product_id, name, price = product["id"], product["name"], product["price"]
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
                update_result = admin_products_controller.update_price(
                    product_id,
                    float(new_price),
                )
                if update_result["ok"]:
                    st.rerun()
                else:
                    st.error(update_result["message"])
            if c3.button("Delete product", key=f"delete_product_{product_id}"):
                delete_result = admin_products_controller.delete_product(product_id)
                if delete_result["ok"]:
                    st.rerun()
                else:
                    st.error(delete_result["message"])

    st.subheader("Deals management")
    deals_response = deals_controller.get_deals()
    deals = deals_response.get("deals", [])
    st.dataframe(
        deals,
        use_container_width=True,
    )


def seller_dashboard_page():
    st.title(t("seller"))

    user_id = st.session_state.get("user_id")
    dashboard_response = seller_dashboard_controller.get_dashboard_data(user_id)
    if not dashboard_response["ok"]:
        st.error(dashboard_response["message"])
        return

    products = dashboard_response.get("products", [])
    metrics = dashboard_response.get("metrics", {})

    st.subheader(f"{t('active_listings')}: {metrics.get('active_listings', 0)}")

    metric_cols = st.columns(4)
    metric_cols[0].metric(
        "Average listing price",
        "-"
        if metrics.get("average_listing_price") is None
        else f"{metrics['average_listing_price']} EUR",
    )
    metric_cols[1].metric(
        "Min listing price",
        "-"
        if metrics.get("min_listing_price") is None
        else f"{metrics['min_listing_price']} EUR",
    )
    metric_cols[2].metric(
        "Max listing price",
        "-"
        if metrics.get("max_listing_price") is None
        else f"{metrics['max_listing_price']} EUR",
    )
    metric_cols[3].metric(
        "Total listings value",
        f"{metrics.get('total_listings_value', 0.0)} EUR",
    )

    st.subheader(t("my_products"))
    if not products:
        st.info(t("no_db_products"))
    else:
        for idx, product in enumerate(products):
            with st.container():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{product['name']}**")
                col2.write(f"{product['price']} EUR")

                action_col1, action_col2 = st.columns([1.2, 3])
                if action_col1.button(t("find_better_deal"), key=f"deal_{idx}_{product['id']}"):
                    render_deal_block(product, user_id, "seller")
                action_col2.link_button(t("open_listing"), product["url"])

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
                    add_product_result = seller_products_controller.add_product(
                        {
                            "name": product_name.strip(),
                            "price": float(product_price),
                            "url": product_url.strip(),
                            "source": t("seller_source"),
                            "image": image_url.strip(),
                            "user_id": user_id,
                        },
                        user_id=user_id,
                    )
                    if add_product_result["ok"]:
                        st.success(t("added_ok").format(name=product_name))
                    else:
                        st.error(t("add_failed").format(err=add_product_result["message"]))
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
            login_result = auth_controller.login(username.strip(), password)
            if login_result["ok"]:
                user = login_result["user"]
                st.session_state["user"] = user["username"]
                st.session_state["user_id"] = user["id"]
                st.session_state["user_role"] = user["role"]
                st.session_state["seller_mode_enabled"] = False
                st.session_state["current_page"] = "marketplace"
                st.rerun()
            else:
                st.error(t("invalid_credentials"))

    with register_tab:
        with st.form("register_form"):
            username = st.text_input(t("username"), key="register_username")
            password = st.text_input(t("password"), type="password", key="register_password")
            submitted = st.form_submit_button(t("register_btn"))
        if submitted:
            register_result = auth_controller.register(username.strip(), password)
            if register_result["ok"]:
                login_result = auth_controller.login(username.strip(), password)
                if login_result["ok"]:
                    user = login_result["user"]
                    st.session_state["user"] = user["username"]
                    st.session_state["user_id"] = user["id"]
                    st.session_state["user_role"] = user["role"]
                    st.session_state["seller_mode_enabled"] = False
                    st.session_state["current_page"] = "marketplace"
                    st.rerun()
                st.success(t("register_success"))
            else:
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
    if "seller_mode_enabled" not in st.session_state:
        st.session_state["seller_mode_enabled"] = False
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "marketplace"
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
        funnel_controller.increment_stat("visits", 1)

    st.sidebar.title(t("navigation"))
    st.sidebar.write(t("logged_in_as").format(username=st.session_state["user"]))

    nav_options = [
        ("marketplace", t("marketplace")),
        ("alerts", t("alerts_page")),
        ("ai_deals", t("ai_deals_page")),
        ("profile", t("profile_page")),
    ]
    if st.session_state.get("seller_mode_enabled"):
        nav_options.append(("seller", t("seller_entry")))
    if st.session_state.get("user_role") == "admin":
        nav_options.append(("admin", t("admin_panel")))
    nav_options.append(("logout", t("logout")))

    nav_keys = [key for key, _ in nav_options]
    nav_label_map = {key: label for key, label in nav_options}
    current_page = st.session_state.get("current_page", "marketplace")
    current_index = nav_keys.index(current_page) if current_page in nav_keys else 0
    selected_page = st.sidebar.radio(
        t("go_to"),
        nav_keys,
        index=current_index,
        format_func=lambda key: nav_label_map.get(key, key),
    )
    st.session_state["current_page"] = selected_page

    if selected_page == "logout":
        del st.session_state["user"]
        del st.session_state["user_id"]
        if "user_role" in st.session_state:
            del st.session_state["user_role"]
        if "seller_mode_enabled" in st.session_state:
            del st.session_state["seller_mode_enabled"]
        if "current_page" in st.session_state:
            del st.session_state["current_page"]
        st.rerun()
    elif selected_page == "marketplace":
        marketplace_page()
    elif selected_page == "alerts":
        alerts_page()
    elif selected_page == "ai_deals":
        ai_deals_page()
    elif selected_page == "admin":
        admin_panel_page()
    elif selected_page == "profile":
        profile_page()
    else:
        seller_dashboard_page()


if __name__ == "__main__":
    main()
