from services.notification_service import NotificationService


class NotificationController:
    def __init__(self, notification_service=None):
        self.notification_service = notification_service or NotificationService()

    def notify_alert_matching_deals(self):
        return self.notification_service.notify_alert_matching_deals()

    def get_notification_policy(self):
        return self.notification_service.get_notification_policy()

    def save_notification_policy(self, max_notifications_per_user, cooldown_hours):
        return self.notification_service.save_notification_policy(
            max_notifications_per_user=max_notifications_per_user,
            cooldown_hours=cooldown_hours,
        )

    def get_scan_execution_settings(self):
        return self.notification_service.get_scan_execution_settings()

    def save_scan_execution_settings(self, auto_scan_enabled, scan_interval_minutes):
        return self.notification_service.save_scan_execution_settings(
            auto_scan_enabled=auto_scan_enabled,
            scan_interval_minutes=scan_interval_minutes,
        )

    def run_scheduled_alert_matching_deals(self):
        return self.notification_service.run_scheduled_alert_matching_deals()

    def get_scheduled_run_status(self):
        return self.notification_service.get_scheduled_run_status()
