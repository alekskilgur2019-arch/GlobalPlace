from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: float
    url: str
    source: str
    image: str = ""
