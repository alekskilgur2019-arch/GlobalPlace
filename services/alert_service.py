from database import (
    create_alert,
    delete_alert,
    get_user_alert_by_query,
    get_user_alerts,
    update_alert_target_price,
)


class AlertService:
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

    def _validate_alert_id(self, alert_id):
        if alert_id is None:
            return {
                "ok": False,
                "message": "Alert id is required.",
            }

        try:
            normalized_alert_id = int(alert_id)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "message": "Alert id must be a valid integer.",
            }

        if normalized_alert_id <= 0:
            return {
                "ok": False,
                "message": "Alert id must be greater than 0.",
            }

        return {
            "ok": True,
            "alert_id": normalized_alert_id,
        }

    def _validate_query(self, query):
        normalized_query = str(query or "").strip()
        if not normalized_query:
            return {
                "ok": False,
                "message": "Query is required.",
            }

        return {
            "ok": True,
            "query": normalized_query,
        }

    def _validate_target_price(self, target_price):
        normalized_target_price = None
        if target_price is not None:
            try:
                normalized_target_price = float(target_price)
            except (TypeError, ValueError):
                return {
                    "ok": False,
                    "message": "Target price must be a number.",
                }

            if normalized_target_price <= 0:
                return {
                    "ok": False,
                    "message": "Target price must be greater than 0.",
                }

        return {
            "ok": True,
            "target_price": normalized_target_price,
        }

    def create_user_alert(self, user_id, query, target_price=None):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "alert_id": None,
            }

        query_validation = self._validate_query(query)
        if not query_validation["ok"]:
            return {
                "ok": False,
                "message": query_validation["message"],
                "alert_id": None,
            }

        target_price_validation = self._validate_target_price(target_price)
        if not target_price_validation["ok"]:
            return {
                "ok": False,
                "message": target_price_validation["message"],
                "alert_id": None,
            }

        existing_alert = get_user_alert_by_query(
            user_validation["user_id"],
            query_validation["query"],
        )
        if existing_alert:
            return {
                "ok": False,
                "message": "Duplicate alert already exists for this query.",
                "alert_id": existing_alert[0],
                "duplicate": True,
            }

        alert_id = create_alert(
            user_validation["user_id"],
            query_validation["query"],
            target_price_validation["target_price"],
        )
        return {
            "ok": True,
            "message": "Alert created.",
            "alert_id": alert_id,
            "duplicate": False,
        }

    def list_user_alerts(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "alerts": [],
            }

        rows = get_user_alerts(user_validation["user_id"])
        alerts = [
            {
                "id": row[0],
                "query": row[1],
                "target_price": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]
        return {
            "ok": True,
            "message": "Alerts loaded.",
            "alerts": alerts,
        }

    def delete_user_alert(self, user_id, alert_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
            }

        alert_validation = self._validate_alert_id(alert_id)
        if not alert_validation["ok"]:
            return {
                "ok": False,
                "message": alert_validation["message"],
            }

        deleted_count = delete_alert(
            alert_validation["alert_id"],
            user_validation["user_id"],
        )
        if deleted_count <= 0:
            return {
                "ok": False,
                "message": "Alert not found.",
            }

        return {
            "ok": True,
            "message": "Alert deleted.",
        }

    def update_user_alert_target_price(self, user_id, alert_id, target_price):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
            }

        alert_validation = self._validate_alert_id(alert_id)
        if not alert_validation["ok"]:
            return {
                "ok": False,
                "message": alert_validation["message"],
            }

        target_price_validation = self._validate_target_price(target_price)
        if not target_price_validation["ok"]:
            return {
                "ok": False,
                "message": target_price_validation["message"],
            }

        updated_count = update_alert_target_price(
            alert_validation["alert_id"],
            user_validation["user_id"],
            target_price_validation["target_price"],
        )
        if updated_count <= 0:
            return {
                "ok": False,
                "message": "Alert not found.",
            }

        return {
            "ok": True,
            "message": "Alert updated.",
            "alert_id": alert_validation["alert_id"],
        }
