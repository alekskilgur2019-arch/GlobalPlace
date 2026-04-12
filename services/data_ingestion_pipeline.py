from adapters.ebay import EbayAdapter
from adapters.willhaben import WillhabenAdapter
from database import init_db, insert_products


def get_adapters():
    return [WillhabenAdapter(), EbayAdapter()]


def fetch_products(query=""):
    products = []
    for adapter in get_adapters():
        products.extend(adapter.search_products(query))
    return products


def normalize_products(products):
    normalized_products = []
    for product in products or []:
        if not product.get("name") or not product.get("url") or not product.get("source"):
            continue

        try:
            price = float(product["price"])
        except (TypeError, ValueError, KeyError):
            continue

        normalized_products.append(
            {
                "name": str(product["name"]).strip(),
                "price": price,
                "url": str(product["url"]).strip(),
                "source": str(product["source"]).strip(),
                "image": str(product.get("image", "")).strip(),
            }
        )
    return normalized_products


def store_products(products, user_id=None):
    if not products:
        return 0
    init_db()
    return insert_products(products, user_id=user_id)


def run_ingestion_pipeline(query="", user_id=None):
    raw_products = fetch_products(query=query)
    normalized_products = normalize_products(raw_products)
    stored_count = store_products(normalized_products, user_id=user_id)
    return {
        "fetched_count": len(raw_products),
        "normalized_count": len(normalized_products),
        "stored_count": stored_count,
        "products": normalized_products,
    }
