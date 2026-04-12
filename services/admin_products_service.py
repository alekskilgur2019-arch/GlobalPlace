from database import delete_product, get_all_products, update_product_price


class AdminProductsService:
    def _validate_product_id(self, product_id):
        if product_id is None:
            return {"ok": False, "message": "Product id is required."}
        try:
            normalized_product_id = int(product_id)
        except (TypeError, ValueError):
            return {"ok": False, "message": "Product id must be a valid integer."}
        if normalized_product_id <= 0:
            return {"ok": False, "message": "Product id must be greater than 0."}
        return {"ok": True, "product_id": normalized_product_id}

    def _validate_price(self, price):
        try:
            normalized_price = float(price)
        except (TypeError, ValueError):
            return {"ok": False, "message": "Price must be a number."}
        if normalized_price <= 0:
            return {"ok": False, "message": "Price must be greater than 0."}
        return {"ok": True, "price": normalized_price}

    def list_products(self):
        rows = get_all_products()
        products = [
            {
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "url": row[3],
                "source": row[4],
                "image": row[5],
                "user_id": row[6],
                "created_at": row[7],
            }
            for row in rows
        ]
        return {"ok": True, "products": products}

    def update_price(self, product_id, new_price):
        product_validation = self._validate_product_id(product_id)
        if not product_validation["ok"]:
            return {"ok": False, "message": product_validation["message"]}
        price_validation = self._validate_price(new_price)
        if not price_validation["ok"]:
            return {"ok": False, "message": price_validation["message"]}
        updated_count = update_product_price(
            product_validation["product_id"],
            price_validation["price"],
        )
        if updated_count <= 0:
            return {"ok": False, "message": "Product not found."}
        return {"ok": True, "message": "Product updated."}

    def delete_product(self, product_id):
        product_validation = self._validate_product_id(product_id)
        if not product_validation["ok"]:
            return {"ok": False, "message": product_validation["message"]}
        deleted_count = delete_product(product_validation["product_id"])
        if deleted_count <= 0:
            return {"ok": False, "message": "Product not found."}
        return {"ok": True, "message": "Product deleted."}
