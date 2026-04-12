from services.product_service import ProductService


class SellerDashboardService:
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()

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

    def _normalize_products(self, products):
        normalized_products = []
        for product in products:
            try:
                price = float(product["price"])
            except (TypeError, ValueError, KeyError):
                continue

            normalized_products.append(
                {
                    **product,
                    "price": price,
                }
            )
        return normalized_products

    def _build_metrics(self, products):
        active_listings = len(products)
        if not products:
            return {
                "active_listings": 0,
                "average_listing_price": None,
                "min_listing_price": None,
                "max_listing_price": None,
                "total_listings_value": 0.0,
            }

        prices = [product["price"] for product in products]
        return {
            "active_listings": active_listings,
            "average_listing_price": round(sum(prices) / len(prices), 2),
            "min_listing_price": round(min(prices), 2),
            "max_listing_price": round(max(prices), 2),
            "total_listings_value": round(sum(prices), 2),
        }

    def get_dashboard_data(self, user_id):
        user_validation = self._validate_user_id(user_id)
        if not user_validation["ok"]:
            return {
                "ok": False,
                "message": user_validation["message"],
                "products": [],
                "metrics": {},
            }

        products = self.product_service.search("", user_id=user_validation["user_id"])
        normalized_products = self._normalize_products(products)
        metrics = self._build_metrics(normalized_products)

        return {
            "ok": True,
            "message": "Seller dashboard loaded.",
            "products": normalized_products,
            "metrics": metrics,
        }
