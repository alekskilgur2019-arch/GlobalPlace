from database import init_db
from services.product_service import ProductService


def main():
    init_db()
    product_service = ProductService()
    result = product_service.create_product(
        name="MacBook Pro M1",
        price=999,
        original_price=1100,
        source="eBay",
        url="https://example.com/macbook-pro-m1",
        condition="New",
    )

    print(result["message"])
    print(result["product"])


if __name__ == "__main__":
    main()
