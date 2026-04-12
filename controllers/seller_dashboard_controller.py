from services.seller_dashboard_service import SellerDashboardService


class SellerDashboardController:
    def __init__(self, seller_dashboard_service=None):
        self.seller_dashboard_service = seller_dashboard_service or SellerDashboardService()

    def get_dashboard_data(self, user_id):
        return self.seller_dashboard_service.get_dashboard_data(user_id)
