from services.deal_service import DealService


class DealsController:
    def __init__(self, deal_service=None):
        self.deal_service = deal_service or DealService()

    def create_deal(
        self,
        user_id,
        product_id,
        original_price,
        negotiated_price,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        return self.deal_service.create_user_deal(
            user_id=user_id,
            product_id=product_id,
            original_price=original_price,
            negotiated_price=negotiated_price,
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )

    def get_deals(self):
        return self.deal_service.list_deals()

    def get_deal_preview(
        self,
        product,
        user_clicks,
        user_id=None,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        return self.deal_service.build_deal_preview(
            product=product,
            user_clicks=user_clicks,
            user_id=user_id,
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )

    def get_ai_deals(
        self,
        user_id,
        user_clicks,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        return self.deal_service.get_ai_deals_for_user(
            user_id=user_id,
            user_clicks=user_clicks,
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )

    def accept_deal(
        self,
        user_id,
        deal,
        commission_mode="basic",
        commission_percent=10.0,
    ):
        return self.deal_service.accept_deal(
            user_id=user_id,
            deal=deal,
            commission_mode=commission_mode,
            commission_percent=commission_percent,
        )

    def get_personalized_deals(self, user_id, **kwargs):
        return self.deal_service.get_personalized_deals(user_id, **kwargs)
