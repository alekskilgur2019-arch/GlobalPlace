import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from services.product_service import ProductService
from services.search import get_original_query_for_display, normalize_search_text


class SearchMatchingTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_PATH
        database.DB_PATH = str(Path(self.temp_dir.name) / "test_database.db")
        database.init_db()
        self.product_service = ProductService()
        self.product_service.adapters = []

    def tearDown(self):
        database.DB_PATH = self.old_db_path
        self.temp_dir.cleanup()

    def _seed_macbook_products(self):
        self.product_service.create_product(
            name="MacBook Pro M1",
            price=999,
            source="eBay",
            url="https://www.ebay.com/itm/123456789012",
        )
        self.product_service.create_product(
            name="MacBook Pro M2",
            price=1199,
            source="eBay",
            url="https://www.ebay.com/itm/123456789013",
        )
        self.product_service.create_product(
            name="MacBook Air M1",
            price=899,
            source="eBay",
            url="https://www.ebay.com/itm/123456789014",
        )

    def test_exact_match_still_works(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="MacBook Pro M1")
        self.assertEqual([item["display_name"] for item in results], ["Macbook Pro M1"])

    def test_safe_prefix_match_returns_family_results(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="MacBook Pro")
        self.assertEqual(
            [item["display_name"] for item in results],
            ["Macbook Pro M1", "Macbook Pro M2"],
        )

    def test_macbook_query_matches_canonical_product(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="macbook pro m1")
        self.assertEqual([item["display_name"] for item in results], ["Macbook Pro M1"])

    def test_mac_book_query_matches_same_canonical_product(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="mac book pro m1")
        self.assertEqual([item["display_name"] for item in results], ["Macbook Pro M1"])

    def test_unrelated_family_is_not_returned(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="MacBook Air")
        self.assertEqual([item["display_name"] for item in results], ["Macbook Air M1"])

    def test_short_noisy_query_does_not_match_broadly(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="Pro")
        self.assertEqual(results, [])

    def test_empty_result_stays_empty_when_no_safe_match_exists(self):
        self._seed_macbook_products()
        results = self.product_service.search_marketplace_products(query="Unknown Query")
        self.assertEqual(results, [])

    def test_empty_state_uses_original_user_query(self):
        self.assertEqual(
            get_original_query_for_display("  MacBook Pro  "),
            "MacBook Pro",
        )
        self.assertEqual(
            get_original_query_for_display("macbook pro m1"),
            "macbook pro m1",
        )

    def test_normalizer_merges_mac_book_into_macbook(self):
        self.assertEqual(
            normalize_search_text("mac book pro m1"),
            "macbook pro m1",
        )
        self.assertEqual(
            normalize_search_text("macbook pro m1"),
            "macbook pro m1",
        )


if __name__ == "__main__":
    unittest.main()
