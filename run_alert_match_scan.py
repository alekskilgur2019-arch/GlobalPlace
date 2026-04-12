from database import init_db
from services.notification_service import NotificationService


def main():
    init_db()
    service = NotificationService()
    execution_settings_response = service.get_scan_execution_settings()
    execution_settings = execution_settings_response["settings"]
    result = service.notify_alert_matching_deals()

    print(
        "Auto scan enabled:",
        execution_settings["auto_scan_enabled"],
    )
    print(
        "Scan interval minutes:",
        execution_settings["scan_interval_minutes"],
    )
    print(result["message"])
    print(f"Users processed: {result['users_processed']}")
    print(f"Matches found: {result['matches_found']}")
    print(f"Notifications sent: {result['notifications_sent']}")


if __name__ == "__main__":
    main()
