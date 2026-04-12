import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.product_urls import (
    is_generated_listing_url,
    is_invalid_listing_url,
    is_search_results_url,
    is_valid_listing_url,
    validate_listing_url,
)


class ProductUrlsTest(unittest.TestCase):
    def test_valid_direct_listing_url_is_allowed(self):
        url = "https://www.ebay.com/itm/123456789012"
        self.assertTrue(is_valid_listing_url(url))
        self.assertEqual(validate_listing_url(url), url)

    def test_willhaben_detail_style_url_is_allowed(self):
        url = "https://www.willhaben.at/iad/kaufen-und-verkaufen/d/macbook-pro-m1-123456789012"
        self.assertTrue(is_valid_listing_url(url))

    def test_search_results_url_is_detected(self):
        self.assertTrue(is_search_results_url("https://www.ebay.com/sch/i.html?_nkw=MacBook+Pro+M1"))
        self.assertTrue(is_search_results_url("https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?keyword=AirPods"))

    def test_search_results_url_is_rejected(self):
        url = "https://www.ebay.com/sch/i.html?_nkw=MacBook+Pro+M1"
        self.assertFalse(is_valid_listing_url(url))
        self.assertEqual(validate_listing_url(url), "")

    def test_placeholder_url_is_rejected(self):
        self.assertTrue(is_invalid_listing_url("https://example.com/macbook-pro-m1"))
        self.assertEqual(validate_listing_url("https://example.com/macbook-pro-m1"), "")

    def test_search_url_is_not_accepted_for_product_creation(self):
        from services.product_service import ProductService

        result = ProductService().create_product(
            name="MacBook Pro M1",
            price=999,
            source="eBay",
            url="https://www.ebay.com/sch/i.html?_nkw=MacBook+Pro+M1",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "A real listing URL is required.")

    def test_legacy_generated_listing_url_is_detected(self):
        self.assertTrue(
            is_generated_listing_url(
                "MacBook Pro M1",
                "eBay",
                "https://www.ebay.com/itm/889453543639",
            )
        )


if __name__ == "__main__":
    unittest.main()
