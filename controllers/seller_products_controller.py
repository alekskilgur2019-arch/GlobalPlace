from services.product_service import ProductService


class SellerProductsController:
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()

    def add_product(self, product, user_id=None):
        return self.product_service.add_product(product, user_id=user_id)
