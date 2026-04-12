import json

from controllers.notification_controller import NotificationController
from database import init_db


def main():
    init_db()
    controller = NotificationController()
    result = controller.run_scheduled_alert_matching_deals()
    scheduled_status_response = controller.get_scheduled_run_status()
    scheduled_status = scheduled_status_response["status"]

    output = {
        "auto_scan_enabled": result["auto_scan_enabled"],
        "scan_interval_minutes": result["scan_interval_minutes"],
        "skipped": result["skipped"],
        "users_processed": result["users_processed"],
        "matches_found": result["matches_found"],
        "notifications_sent": result["notifications_sent"],
        "message": result["message"],
        "last_scheduled_run_at": scheduled_status["last_scheduled_run_at"],
        "last_scheduled_run_status": scheduled_status["last_scheduled_run_status"],
        "last_error_message": scheduled_status["last_error_message"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
