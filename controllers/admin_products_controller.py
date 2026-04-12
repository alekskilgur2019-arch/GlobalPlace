from services.admin_products_service import AdminProductsService


class AdminProductsController:
    def __init__(self, admin_products_service=None):
        self.admin_products_service = admin_products_service or AdminProductsService()

    def get_products(self):
        return self.admin_products_service.list_products()

    def update_price(self, product_id, new_price):
        return self.admin_products_service.update_price(product_id, new_price)

    def delete_product(self, product_id):
        return self.admin_products_service.delete_product(product_id)
