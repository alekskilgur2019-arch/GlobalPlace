from services.product_service import ProductService
from services.product_family import derive_display_name


class ProductSearchController:
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()

    def search_products(self, query="", filters=None, user_id=None):
        normalized_query = str(query or "").strip()
        normalized_filters = filters or {}
        results = self.product_service.search_marketplace_products(
            query=normalized_query,
            filters=normalized_filters,
            user_id=user_id,
        )
        return {
            "query": normalized_query,
            "filters": normalized_filters,
            "count": len(results),
            "results": results,
        }

    def get_family_page(self, family_key, user_id=None):
        normalized_family_key = str(family_key or "").strip().lower()
        offers = self.product_service.get_offers_by_family_key(
            normalized_family_key,
            user_id=user_id,
        )
        best_offer = self.product_service.select_best_offer(offers)
        other_offers = [
            offer
            for offer in offers
            if not best_offer or int(offer.get("id", 0) or 0) != int(best_offer.get("id", 0) or 0)
        ]
        display_name = (
            (best_offer or {}).get("display_name")
            or derive_display_name(normalized_family_key.replace("-", " "))
        )
        return {
            "family_key": normalized_family_key,
            "display_name": display_name,
            "best_offer": best_offer,
            "other_offers": other_offers,
        }
