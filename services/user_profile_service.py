import os
import uuid
from datetime import datetime, timedelta

from database import (
    add_user_preference,
    clear_user_telegram_chat_id,
    create_telegram_connect_token,
    expire_unused_telegram_connect_tokens_for_user,
    get_latest_active_telegram_connect_token_for_user,
    get_user_behavior,
    get_user_by_telegram_chat_id,
    get_user_email_verified,
    get_user_preferences,
    get_telegram_connect_token,
    get_user_telegram_chat_id,
    mark_telegram_connect_token_used,
    set_user_telegram_chat_id,
)
from services.telegram_service import get_telegram_bot_username, send_telegram_message


class UserProfileService:
    TEST_TELEGRAM_MESSAGE = "✅ GlobalPlace Telegram connection works."
    TELEGRAM_CONNECT_TOKEN_TTL_MINUTES = 15

    def _validate_user_id(self, user_id):
        if user_id is None:
            return {
                "ok": False,
                "message": "User id is required.",
            }

        try:
            normalized_user_id = int(user_id)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "message": "User id must be a valid integer.",
            }

        if normalized_user_id <= 0:
            return {
                "ok": False,
                "message": "User id must be greater than 0.",
            }

        return {
            "ok": True,
            "user_id": normalized_user_id,
        }

    def _validate_telegram_chat_id(self, telegram_chat_id):
        normalized_chat_id = str(telegram_chat_id or "").strip()
        if not normalized_chat_id:
            return {
                "ok": False,
                "message": "Telegram chat id is required.",
            }

        return {
            "ok": True,
            "telegram_chat_id": normalized_chat_id,
        }

    def _parse_timestamp(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace(" ", "T"))
        except ValueError:
            return None

    def _is_connect_token_expired(self, created_at):
        parsed_created_at = self._parse_timestamp(created_at)
        if parsed_created_at is None:
            return True

        expires_at = parsed_created_at + timedelta(
            minutes=self.TELEGRAM_CONNECT_TOKEN_TTL_MINUTES
        )
        return datetime.utcnow() > expires_at

    def _get_telegram_bot_username(self):
        return get_telegram_bot_username()

    def _get_globalplace_website_url(self):
        return (
            str(os.getenv("GLOBALPLACE_WEBSITE_URL") or "").strip()
            or "http://localhost:8501"
        )

    def _build_telegram_connect_url(self, connect_token):
        bot_username = self._get_telegram_bot_username()
        if not bot_username:
            return ""
        return f"https://t.me/{bot_username}?start={connect_token}"

    def add_search_preference(self, user_id, query):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return user_validation

        normalized_query = str(query or "").strip()
        if not normalized_query:
            return {
                "ok": False,
                "message": "Query is required.",
            }

        add_user_preference(user_validation["user_id"], normalized_query)
        return {
            "ok": True,
            "message": "Preference saved.",
        }

    def get_preferences(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": True,
                "preferences": [],
            }

        rows = get_user_preferences(user_validation["user_id"])
        preferences = [
            {
                "id": row[0],
                "query": row[1],
                "created_at": row[2],
            }
            for row in rows
        ]
        return {
            "ok": True,
            "preferences": preferences,
        }

    def get_behavior(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": True,
                "behavior": None,
            }

        behavior = get_user_behavior(user_validation["user_id"])
        if not behavior:
            return {
                "ok": True,
                "behavior": None,
            }

        return {
            "ok": True,
            "behavior": {
                "user_id": behavior[0],
                "viewed_product": behavior[1],
                "product_category": behavior[2],
                "avg_discount_preference": behavior[3],
                "last_deal_date": behavior[4],
                "clicks_count": behavior[5],
                "updated_at": behavior[6],
                "excluded_category": behavior[7],
            },
        }

    def save_telegram_chat_id(self, user_id, telegram_chat_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return user_validation

        chat_validation = self._validate_telegram_chat_id(telegram_chat_id)
        if not chat_validation["ok"]:
            return chat_validation

        updated_count = set_user_telegram_chat_id(
            user_validation["user_id"],
            chat_validation["telegram_chat_id"],
        )
        if updated_count <= 0:
            return {
                "ok": False,
                "message": "User not found.",
            }

        return {
            "ok": True,
            "message": "Telegram chat id saved.",
            "telegram_chat_id": chat_validation["telegram_chat_id"],
        }

    def get_telegram_chat_id(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "telegram_chat_id": "",
            }

        telegram_chat_id = get_user_telegram_chat_id(user_validation["user_id"]) or ""
        return {
            "ok": True,
            "message": "Telegram chat id loaded.",
            "telegram_chat_id": str(telegram_chat_id),
        }

    def get_telegram_connection_status(self, user_id):
        chat_id_response = self.get_telegram_chat_id(user_id)
        if not chat_id_response["ok"]:
            return {
                "ok": False,
                "message": chat_id_response["message"],
                "connected": False,
                "telegram_chat_id": "",
            }

        telegram_chat_id = str(chat_id_response.get("telegram_chat_id") or "").strip()
        return {
            "ok": True,
            "message": "Telegram connection status loaded.",
            "connected": bool(telegram_chat_id),
            "telegram_chat_id": telegram_chat_id,
        }

    def get_or_create_telegram_connect_link(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "connected": False,
                "connect_url": "",
            }

        connection_status = self.get_telegram_connection_status(user_validation["user_id"])
        if connection_status["connected"]:
            return {
                "ok": True,
                "message": "Telegram is already connected.",
                "connected": True,
                "connect_url": "",
                "telegram_chat_id": connection_status["telegram_chat_id"],
            }

        bot_username = self._get_telegram_bot_username()
        if not bot_username:
            return {
                "ok": False,
                "message": "Telegram bot username is not configured.",
                "connected": False,
                "connect_url": "",
            }

        existing_token_row = get_latest_active_telegram_connect_token_for_user(
            user_validation["user_id"]
        )
        if existing_token_row and not self._is_connect_token_expired(existing_token_row[4]):
            connect_token = existing_token_row[2]
        else:
            expire_unused_telegram_connect_tokens_for_user(user_validation["user_id"])
            connect_token = str(uuid.uuid4())
            create_telegram_connect_token(user_validation["user_id"], connect_token)
            print(
                f"telegram_connect_token_generated user_id={user_validation['user_id']} token={connect_token}"
            )

        return {
            "ok": True,
            "message": "Telegram connect link is ready.",
            "connected": False,
            "connect_token": connect_token,
            "connect_url": self._build_telegram_connect_url(connect_token),
            "expires_in_minutes": self.TELEGRAM_CONNECT_TOKEN_TTL_MINUTES,
        }

    def link_telegram_chat_by_connect_token(self, connect_token, telegram_chat_id):
        normalized_token = str(connect_token or "").strip()
        if not normalized_token:
            return {
                "ok": False,
                "message": "Telegram connect token is required.",
            }

        chat_validation = self._validate_telegram_chat_id(telegram_chat_id)
        if not chat_validation["ok"]:
            return chat_validation

        token_row = get_telegram_connect_token(normalized_token)
        print(f"telegram_connect_token_received token={normalized_token}")
        if not token_row:
            print("telegram_connect_token_lookup_result missing")
            return {
                "ok": False,
                "message": "This Telegram connection link is invalid.",
            }

        token_user_id = int(token_row[1])
        token_is_used = bool(token_row[3])
        token_created_at = token_row[4]
        print(
            "telegram_connect_token_lookup_result "
            f"user_id={token_user_id} is_used={token_is_used} created_at={token_created_at}"
        )
        if token_is_used:
            print("telegram_connect_token_validation failed_reason=used")
            return {
                "ok": False,
                "message": "This Telegram connection link was already used.",
            }
        if self._is_connect_token_expired(token_created_at):
            print("telegram_connect_token_validation failed_reason=expired")
            return {
                "ok": False,
                "message": "This Telegram connection link has expired.",
            }

        existing_chat_owner = get_user_by_telegram_chat_id(
            chat_validation["telegram_chat_id"]
        )
        if existing_chat_owner and int(existing_chat_owner[0]) != token_user_id:
            existing_username = str(existing_chat_owner[1] or "")
            existing_password = str(existing_chat_owner[2] or "")
            if (
                existing_username == f"tg_{chat_validation['telegram_chat_id']}"
                and not existing_password
            ):
                clear_user_telegram_chat_id(existing_chat_owner[0])
                print(
                    "telegram_connect_token_validation released_shadow_user "
                    f"user_id={existing_chat_owner[0]}"
                )
            else:
                print("telegram_connect_token_validation failed_reason=chat_already_linked")
                return {
                    "ok": False,
                    "message": "This Telegram chat is already linked to another account.",
                }

        try:
            updated_count = set_user_telegram_chat_id(
                token_user_id,
                chat_validation["telegram_chat_id"],
            )
        except Exception:
            return {
                "ok": False,
                "message": "This Telegram chat is already linked to another account.",
            }

        if updated_count <= 0:
            print("telegram_connect_token_validation failed_reason=user_not_found")
            return {
                "ok": False,
                "message": "User not found for this Telegram connection link.",
            }

        mark_telegram_connect_token_used(normalized_token)
        print(
            "telegram_connect_token_validation success "
            f"user_id={token_user_id} telegram_chat_id={chat_validation['telegram_chat_id']}"
        )
        return {
            "ok": True,
            "message": "Telegram linked successfully.",
            "user_id": token_user_id,
            "telegram_chat_id": chat_validation["telegram_chat_id"],
        }

    def get_telegram_onboarding_context(self):
        website_url = self._get_globalplace_website_url()
        return {
            "ok": True,
            "message": "Telegram onboarding context loaded.",
            "website_url": website_url,
        }

    def get_seller_access_status(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "seller_access_enabled": False,
                "email_verified": False,
            }

        email_verified = get_user_email_verified(user_validation["user_id"])
        return {
            "ok": True,
            "message": "Seller access status loaded.",
            "seller_access_enabled": bool(email_verified),
            "email_verified": bool(email_verified),
        }

    def send_telegram_test_message(self, user_id):
        connection_status = self.get_telegram_connection_status(user_id)
        if not connection_status["ok"]:
            return {
                "ok": False,
                "message": connection_status["message"],
            }

        telegram_chat_id = str(connection_status.get("telegram_chat_id") or "").strip()
        if not telegram_chat_id:
            return {
                "ok": False,
                "message": "Telegram is not connected yet.",
            }

        sent = send_telegram_message(
            self.TEST_TELEGRAM_MESSAGE,
            chat_id=telegram_chat_id,
        )
        if not sent:
            return {
                "ok": False,
                "message": "Failed to send Telegram test message.",
            }

        return {
            "ok": True,
            "message": "Telegram test message sent.",
            "telegram_chat_id": telegram_chat_id,
        }
