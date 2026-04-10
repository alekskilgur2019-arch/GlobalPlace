from adapters.base_adapter import BaseAdapter


class EbayAdapter(BaseAdapter):
    def search_products(self, query):
        return [
            {
                "name": "AirPods Pro",
                "price": 200,
                "url": "https://www.ebay.com/mock/airpods-pro",
                "source": "eBay",
                "image": "https://via.placeholder.com/150?text=AirPods+Pro",
            },
            {
                "name": "Nike Sneakers",
                "price": 120,
                "url": "https://www.ebay.com/mock/nike-sneakers",
                "source": "eBay",
                "image": "https://via.placeholder.com/150?text=Nike+Sneakers",
            },
        ]
