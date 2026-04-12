import re
from datetime import datetime, timedelta

from database import (
    clear_alert_notification_logs_for_user,
    clear_notification_delivery_state,
    get_all_telegram_users,
    get_last_notification_time,
    get_notification_setting,
    get_user_alerts,
    get_user_behavior,
    has_alert_notification_been_sent,
    mark_alert_notification_sent,
    set_notification_setting,
    update_last_notification_time,
)
from services.events import log_event, normalize_product_family_key
from services.deal_service import DealService
from services.product_service import ProductService
from services.telegram_service import send_alert_match


class NotificationService:
    MATCH_STOPWORDS = {"the", "for", "and", "with"}
    POLICY_KEYS = {
        "max_notifications_per_user": "max_notifications_per_user",
        "cooldown_hours": "cooldown_hours",
    }
    EXECUTION_KEYS = {
        "auto_scan_enabled": "auto_scan_enabled",
        "scan_interval_minutes": "scan_interval_minutes",
    }
    SCHEDULED_STATUS_KEYS = {
        "last_scheduled_run_at": "last_scheduled_run_at",
        "last_scheduled_run_status": "last_scheduled_run_status",
        "last_users_processed": "last_users_processed",
        "last_matches_found": "last_matches_found",
        "last_notifications_sent": "last_notifications_sent",
        "last_error_message": "last_error_message",
    }

    def __init__(self, product_service=None, deal_service=None):
        self.product_service = product_service or ProductService()
        self.deal_service = deal_service or DealService()

    def _parse_timestamp(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace(" ", "T"))
        except ValueError:
            return None

    def _now_iso(self):
        return datetime.now().isoformat(timespec="seconds")

    def _normalize_max_notifications_per_user(self, value):
        normalized = str(value or "").strip()
        if not normalized:
            return None

        try:
            parsed = int(normalized)
        except (TypeError, ValueError):
            return None

        return parsed if parsed > 0 else None

    def _normalize_cooldown_hours(self, value):
        normalized = str(value or "").strip()
        if not normalized:
            return None

        try:
            parsed = float(normalized)
        except (TypeError, ValueError):
            return None

        return parsed if parsed >= 0 else None

    def _normalize_auto_scan_enabled(self, value):
        if isinstance(value, bool):
            return value

        normalized = str(value or "").strip().lower()
        if not normalized:
            return False

        return normalized in {"1", "true", "yes", "on"}

    def _normalize_scan_interval_minutes(self, value):
        normalized = str(value or "").strip()
        if not normalized:
            return 60

        try:
            parsed = int(normalized)
        except (TypeError, ValueError):
            return None

        return parsed if parsed > 0 else None

    def _normalize_scheduled_run_status(self, value):
        normalized = str(value or "").strip().lower()
        if normalized in {"success", "skipped", "failed"}:
            return normalized
        return None

    def _build_recipient_key(self, telegram_chat_id):
        return f"tg:{telegram_chat_id}"

    def _normalize_match_text(self, value):
        normalized = str(value or "").strip().lower()
        if not normalized:
            return ""

        normalized = re.sub(r"[.\-_/]+", " ", normalized)
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _tokenize_match_text(self, value, apply_stopword_filter=False):
        normalized = self._normalize_match_text(value)
        if not normalized:
            return []

        tokens = [token for token in normalized.split(" ") if token]
        if not apply_stopword_filter or len(tokens) <= 1:
            return tokens

        filtered_tokens = [
            token for token in tokens if token not in self.MATCH_STOPWORDS
        ]
        return filtered_tokens or tokens

    def _is_weak_alert_query(self, query):
        normalized_query = self._normalize_match_text(query)
        if not normalized_query:
            return True

        query_tokens = self._tokenize_match_text(
            normalized_query,
            apply_stopword_filter=True,
        )
        if not query_tokens:
            return True

        if len(query_tokens) == 1 and len(query_tokens[0]) < 4:
            return True

        return False

    def _matches_alert_query(self, alert_query, product_name):
        normalized_query = self._normalize_match_text(alert_query)
        normalized_product_name = self._normalize_match_text(product_name)
        if not normalized_query or not normalized_product_name:
            return False

        if self._is_weak_alert_query(normalized_query):
            return False

        query_tokens = self._tokenize_match_text(
            normalized_query,
            apply_stopword_filter=True,
        )
        product_tokens = self._tokenize_match_text(normalized_product_name)
        if not query_tokens or not product_tokens:
            return False

        if len(query_tokens) > 1:
            phrase_pattern = f" {normalized_query} "
            normalized_product_phrase = f" {normalized_product_name} "
            if phrase_pattern in normalized_product_phrase:
                return True

        product_token_set = set(product_tokens)
        return all(token in product_token_set for token in query_tokens)

    def _is_in_cooldown(self, telegram_chat_id, cooldown_hours):
        if cooldown_hours is None:
            return False

        last_sent_at = self._parse_timestamp(
            get_last_notification_time(self._build_recipient_key(telegram_chat_id))
        )
        if last_sent_at is None:
            return False

        cooldown_until = last_sent_at + timedelta(hours=float(cooldown_hours))
        return datetime.now() < cooldown_until

    def _sort_matches(self, matches):
        return sorted(
            matches,
            key=lambda match: (
                -float(match.get("score", 0) or 0),
                float(match.get("price", 0) or 0),
                int(match.get("product_id", 0) or 0),
            ),
        )

    def get_notification_policy(self):
        max_notifications_per_user = self._normalize_max_notifications_per_user(
            get_notification_setting(self.POLICY_KEYS["max_notifications_per_user"])
        )
        cooldown_hours = self._normalize_cooldown_hours(
            get_notification_setting(self.POLICY_KEYS["cooldown_hours"])
        )
        return {
            "ok": True,
            "message": "Notification policy loaded.",
            "policy": {
                "max_notifications_per_user": max_notifications_per_user,
                "cooldown_hours": cooldown_hours,
            },
        }

    def get_scan_execution_settings(self):
        auto_scan_enabled = self._normalize_auto_scan_enabled(
            get_notification_setting(self.EXECUTION_KEYS["auto_scan_enabled"])
        )
        scan_interval_minutes = self._normalize_scan_interval_minutes(
            get_notification_setting(self.EXECUTION_KEYS["scan_interval_minutes"])
        )
        return {
            "ok": True,
            "message": "Scan execution settings loaded.",
            "settings": {
                "auto_scan_enabled": auto_scan_enabled,
                "scan_interval_minutes": scan_interval_minutes,
            },
        }

    def save_scan_execution_settings(self, auto_scan_enabled, scan_interval_minutes):
        normalized_auto_scan_enabled = self._normalize_auto_scan_enabled(auto_scan_enabled)
        normalized_scan_interval_minutes = self._normalize_scan_interval_minutes(
            scan_interval_minutes
        )

        raw_scan_interval_minutes = str(scan_interval_minutes or "").strip()
        if raw_scan_interval_minutes and normalized_scan_interval_minutes is None:
            return {
                "ok": False,
                "message": "Scan interval minutes must be a positive integer.",
            }

        set_notification_setting(
            self.EXECUTION_KEYS["auto_scan_enabled"],
            "1" if normalized_auto_scan_enabled else "0",
        )
        set_notification_setting(
            self.EXECUTION_KEYS["scan_interval_minutes"],
            normalized_scan_interval_minutes,
        )
        return {
            "ok": True,
            "message": "Scan execution settings saved.",
            "settings": {
                "auto_scan_enabled": normalized_auto_scan_enabled,
                "scan_interval_minutes": normalized_scan_interval_minutes,
            },
        }

    def get_scheduled_run_status(self):
        return {
            "ok": True,
            "message": "Scheduled run status loaded.",
            "status": {
                "last_scheduled_run_at": get_notification_setting(
                    self.SCHEDULED_STATUS_KEYS["last_scheduled_run_at"]
                ),
                "last_scheduled_run_status": self._normalize_scheduled_run_status(
                    get_notification_setting(
                        self.SCHEDULED_STATUS_KEYS["last_scheduled_run_status"]
                    )
                ),
                "last_users_processed": int(
                    get_notification_setting(self.SCHEDULED_STATUS_KEYS["last_users_processed"])
                    or 0
                ),
                "last_matches_found": int(
                    get_notification_setting(self.SCHEDULED_STATUS_KEYS["last_matches_found"])
                    or 0
                ),
                "last_notifications_sent": int(
                    get_notification_setting(
                        self.SCHEDULED_STATUS_KEYS["last_notifications_sent"]
                    )
                    or 0
                ),
                "last_error_message": get_notification_setting(
                    self.SCHEDULED_STATUS_KEYS["last_error_message"]
                )
                or "",
            },
        }

    def _save_scheduled_run_status(
        self,
        run_status,
        users_processed=0,
        matches_found=0,
        notifications_sent=0,
        error_message="",
    ):
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_scheduled_run_at"],
            self._now_iso(),
        )
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_scheduled_run_status"],
            run_status,
        )
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_users_processed"],
            int(users_processed or 0),
        )
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_matches_found"],
            int(matches_found or 0),
        )
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_notifications_sent"],
            int(notifications_sent or 0),
        )
        set_notification_setting(
            self.SCHEDULED_STATUS_KEYS["last_error_message"],
            str(error_message or "").strip(),
        )

    def save_notification_policy(self, max_notifications_per_user, cooldown_hours):
        normalized_max_notifications = self._normalize_max_notifications_per_user(
            max_notifications_per_user
        )
        normalized_cooldown_hours = self._normalize_cooldown_hours(cooldown_hours)

        raw_max_notifications = str(max_notifications_per_user or "").strip()
        raw_cooldown_hours = str(cooldown_hours or "").strip()
        if raw_max_notifications and normalized_max_notifications is None:
            return {
                "ok": False,
                "message": "Max notifications per user must be a positive integer.",
            }
        if raw_cooldown_hours and normalized_cooldown_hours is None:
            return {
                "ok": False,
                "message": "Cooldown hours must be a non-negative number.",
            }

        set_notification_setting(
            self.POLICY_KEYS["max_notifications_per_user"],
            normalized_max_notifications,
        )
        set_notification_setting(
            self.POLICY_KEYS["cooldown_hours"],
            normalized_cooldown_hours,
        )
        return {
            "ok": True,
            "message": "Notification policy saved.",
            "policy": {
                "max_notifications_per_user": normalized_max_notifications,
                "cooldown_hours": normalized_cooldown_hours,
            },
        }

    def _get_user_clicks(self, user_id):
        behavior = get_user_behavior(user_id)
        if not behavior:
            return 0
        return int(behavior[5] or 0)

    def _build_alert_match(self, user_id, alert, product):
        user_clicks = self._get_user_clicks(user_id)
        preview_response = self.deal_service.build_deal_preview(
            product=product,
            user_clicks=user_clicks,
            user_id=user_id,
        )
        if not preview_response["ok"]:
            return None

        preview = preview_response["deal"]
        family_query = str(alert.get("query") or product.get("display_name") or product.get("name") or "").strip()
        family_key = str(product.get("family_key") or "").strip()
        display_name = str(product.get("display_name") or family_query).strip()
        return {
            "alert_id": alert["id"],
            "alert_query": alert["query"],
            "product_family_key": family_key or normalize_product_family_key(family_query),
            "family_query": family_query,
            "display_name": display_name,
            "target_price": alert["target_price"],
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "score": preview.get("score"),
            "url": str(product.get("url") or "").strip(),
            "offer_url": product["url"],
            "source": product.get("source"),
            "condition": product.get("condition"),
            "effective_price": product.get("effective_price"),
            "offer_score": product.get("offer_score"),
            "is_best_offer": product.get("is_best_offer", False),
        }

    def _find_matches_for_user(self, user_id, alerts, products):
        matches = []

        for alert in alerts:
            alert_query = alert.get("query")
            if not self._normalize_match_text(alert_query):
                continue

            target_price = alert.get("target_price")
            matched_products = []
            for product in products:
                product_name = product.get("name")
                if not self._matches_alert_query(alert_query, product_name):
                    continue
                if target_price is not None and float(product["price"]) > float(target_price):
                    continue
                if has_alert_notification_been_sent(user_id, alert["id"], product["id"]):
                    continue

                matched_products.append(product)

            best_product = self.product_service.select_best_offer(matched_products)
            if not best_product:
                continue

            match = self._build_alert_match(user_id, alert, best_product)
            if match:
                matches.append(match)

        return matches

    def preview_alert_matches_for_user(self, user_id):
        alerts_rows = get_user_alerts(user_id)
        alerts = [
            {
                "id": alert_row[0],
                "query": alert_row[1],
                "target_price": alert_row[2],
                "created_at": alert_row[3],
            }
            for alert_row in alerts_rows
        ]
        products = self.product_service.search_marketplace_products(query="")
        matches = self._find_matches_for_user(user_id, alerts, products)
        return {
            "ok": True,
            "alerts": alerts,
            "matches": matches,
        }

    def clear_user_notification_state(self, user_id, telegram_chat_id):
        cleared_logs = clear_alert_notification_logs_for_user(user_id)
        cleared_delivery_state = clear_notification_delivery_state(
            self._build_recipient_key(telegram_chat_id)
        )
        return {
            "ok": True,
            "cleared_logs": cleared_logs,
            "cleared_delivery_state": cleared_delivery_state,
        }

    def notify_alert_matching_deals(self):
        policy_response = self.get_notification_policy()
        policy = policy_response["policy"]
        max_notifications_per_user = policy["max_notifications_per_user"]
        cooldown_hours = policy["cooldown_hours"]

        products = self.product_service.search_marketplace_products(query="")
        users = get_all_telegram_users()

        total_matches = 0
        total_notifications_sent = 0
        users_processed = 0

        for row in users:
            user_id = row[0]
            telegram_chat_id = row[2]
            if not telegram_chat_id:
                continue

            alerts_rows = get_user_alerts(user_id)
            alerts = [
                {
                    "id": alert_row[0],
                    "query": alert_row[1],
                    "target_price": alert_row[2],
                    "created_at": alert_row[3],
                }
                for alert_row in alerts_rows
            ]
            if not alerts:
                continue

            users_processed += 1
            if self._is_in_cooldown(telegram_chat_id, cooldown_hours):
                continue

            matches = self._find_matches_for_user(user_id, alerts, products)
            matches = self._sort_matches(matches)
            total_matches += len(matches)
            if max_notifications_per_user is not None:
                matches = matches[:max_notifications_per_user]

            sent_for_user = 0
            for match in matches:
                if send_alert_match(match, telegram_chat_id):
                    sent_for_user += 1
                    total_notifications_sent += 1
                    log_event(
                        user_id=user_id,
                        event_type="notification_sent",
                        product_family_key=match["product_family_key"],
                        offer_id=match.get("product_id"),
                        price=match.get("price"),
                    )
                    mark_alert_notification_sent(
                        user_id=user_id,
                        alert_id=match["alert_id"],
                        product_id=match["product_id"],
                    )
            if sent_for_user > 0:
                update_last_notification_time(self._build_recipient_key(telegram_chat_id))

        return {
            "ok": True,
            "message": "Alert match notifications processed.",
            "users_processed": users_processed,
            "matches_found": total_matches,
            "notifications_sent": total_notifications_sent,
        }

    def run_scheduled_alert_matching_deals(self):
        execution_settings_response = self.get_scan_execution_settings()
        execution_settings = execution_settings_response["settings"]

        result = {
            "ok": True,
            "message": "Scheduled alert scan skipped.",
            "skipped": False,
            "auto_scan_enabled": execution_settings["auto_scan_enabled"],
            "scan_interval_minutes": execution_settings["scan_interval_minutes"],
            "users_processed": 0,
            "matches_found": 0,
            "notifications_sent": 0,
        }

        if not execution_settings["auto_scan_enabled"]:
            result["skipped"] = True
            self._save_scheduled_run_status(
                run_status="skipped",
                users_processed=0,
                matches_found=0,
                notifications_sent=0,
                error_message="",
            )
            return result

        try:
            scan_result = self.notify_alert_matching_deals()
            final_result = {
                "ok": bool(scan_result.get("ok", True)),
                "message": scan_result.get("message", "Alert match notifications processed."),
                "skipped": False,
                "auto_scan_enabled": execution_settings["auto_scan_enabled"],
                "scan_interval_minutes": execution_settings["scan_interval_minutes"],
                "users_processed": int(scan_result.get("users_processed", 0) or 0),
                "matches_found": int(scan_result.get("matches_found", 0) or 0),
                "notifications_sent": int(scan_result.get("notifications_sent", 0) or 0),
            }
            self._save_scheduled_run_status(
                run_status="success",
                users_processed=final_result["users_processed"],
                matches_found=final_result["matches_found"],
                notifications_sent=final_result["notifications_sent"],
                error_message="",
            )
            return final_result
        except Exception as exc:
            error_message = str(exc)
            self._save_scheduled_run_status(
                run_status="failed",
                users_processed=0,
                matches_found=0,
                notifications_sent=0,
                error_message=error_message,
            )
            return {
                "ok": False,
                "message": "Scheduled alert scan failed.",
                "skipped": False,
                "auto_scan_enabled": execution_settings["auto_scan_enabled"],
                "scan_interval_minutes": execution_settings["scan_interval_minutes"],
                "users_processed": 0,
                "matches_found": 0,
                "notifications_sent": 0,
                "error_message": error_message,
            }
