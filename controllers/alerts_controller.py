from services.alert_service import AlertService


class AlertsController:
    def __init__(self, alert_service=None):
        self.alert_service = alert_service or AlertService()

    def create_alert(self, user_id, query, target_price=None):
        return self.alert_service.create_user_alert(
            user_id=user_id,
            query=query,
            target_price=target_price,
        )

    def get_alerts(self, user_id):
        return self.alert_service.list_user_alerts(user_id)

    def delete_alert(self, user_id, alert_id):
        return self.alert_service.delete_user_alert(
            user_id=user_id,
            alert_id=alert_id,
        )
