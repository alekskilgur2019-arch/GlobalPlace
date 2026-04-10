from adapters.ebay import EbayAdapter
from adapters.willhaben import WillhabenAdapter
from database import init_db, insert_products, search_products


class ProductService:
    def __init__(self):
        self.adapters = [WillhabenAdapter(), EbayAdapter()]
        init_db()

    def load_products(self, query="", user_id=None):
        all_products = []
        for adapter in self.adapters:
            products = adapter.search_products(query)
            all_products.extend(products)

        inserted_count = insert_products(all_products, user_id=user_id)
        return inserted_count

    def search(self, query, user_id=None):
        rows = search_products(query, user_id=user_id)
        return [
            {
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "url": row[3],
                "source": row[4],
                "image": row[5] or "",
                "user_id": row[6],
                "created_at": row[7],
            }
            for row in rows
        ]
