from adapters.base_adapter import BaseAdapter


class WillhabenAdapter(BaseAdapter):
    def search_products(self, query):
        return [
            {
                "name": "AirPods Pro",
                "price": 200,
                "url": "https://www.willhaben.at/mock/airpods-pro",
                "source": "Willhaben",
                "image": "https://via.placeholder.com/150?text=AirPods+Pro",
            },
            {
                "name": "Nike Sneakers",
                "price": 120,
                "url": "https://www.willhaben.at/mock/nike-sneakers",
                "source": "Willhaben",
                "image": "https://via.placeholder.com/150?text=Nike+Sneakers",
            },
        ]
