from database import get_all_products, init_db, update_product_url
from services.product_urls import is_invalid_listing_url
from services.product_urls import is_generated_listing_url


def main():
    init_db()
    updated = 0
    for product in get_all_products():
        product_id, name, _, url, source, *_rest = product
        if not is_invalid_listing_url(url) and not is_generated_listing_url(name, source, url):
            continue
        repaired_url = ""
        if repaired_url == url:
            continue
        update_product_url(product_id, repaired_url)
        updated += 1

    print(f"Updated product URLs: {updated}")


if __name__ == "__main__":
    main()
