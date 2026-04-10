from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def search_products(self, query):
        """
        Return list of dicts with keys:
        name, price, url, source, image
        """
        raise NotImplementedError
