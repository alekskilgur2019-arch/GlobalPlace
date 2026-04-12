from services.analytics_service import AnalyticsService


class AnalyticsController:
    def __init__(self, analytics_service=None):
        self.analytics_service = analytics_service or AnalyticsService()

    def get_admin_dashboard_analytics(self):
        return self.analytics_service.get_admin_dashboard_analytics()
