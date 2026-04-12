import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from controllers.product_search_controller import ProductSearchController
from services.offer_ranking import select_best_offer
from services.product_family import derive_display_name, derive_family_key
from services.product_service import ProductService


class ProductFamilyAndRankingTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_PATH
        database.DB_PATH = str(Path(self.temp_dir.name) / "test_database.db")
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.old_db_path
        self.temp_dir.cleanup()

    def test_family_key_is_deterministic(self):
        self.assertEqual(
            derive_family_key("MacBook Pro M1 13"),
            derive_family_key("MacBook Pro M1 13"),
        )

    def test_similar_names_resolve_to_same_family(self):
        expected = "macbook-pro-m1"
        self.assertEqual(derive_family_key("MacBook Pro M1 13"), expected)
        self.assertEqual(derive_family_key("Apple MacBook Pro M1"), expected)
        self.assertEqual(derive_family_key("MacBook Pro M1 2020"), expected)
        self.assertEqual(derive_display_name("Apple MacBook Pro M1"), "Macbook Pro M1")

    def test_unrelated_products_do_not_share_family(self):
        self.assertNotEqual(
            derive_family_key("MacBook Pro M1"),
            derive_family_key("AirPods Pro"),
        )

    def test_best_offer_selection_is_deterministic(self):
        offers = [
            {
                "id": 2,
                "name": "MacBook Pro M1",
                "price": 980,
                "source": "ebay",
                "condition": "good",
            },
            {
                "id": 1,
                "name": "MacBook Pro M1",
                "price": 999,
                "source": "amazon",
                "condition": "new",
            },
        ]
        self.assertEqual(select_best_offer(offers)["id"], 1)

    def test_lower_price_wins_when_condition_same(self):
        offers = [
            {"id": 1, "price": 999, "source": "ebay", "condition": "good"},
            {"id": 2, "price": 950, "source": "ebay", "condition": "good"},
        ]
        self.assertEqual(select_best_offer(offers)["id"], 2)

    def test_source_priority_resolves_ties(self):
        offers = [
            {"id": 1, "price": 999, "source": "ebay", "condition": "good"},
            {"id": 2, "price": 999, "source": "amazon", "condition": "good"},
        ]
        self.assertEqual(select_best_offer(offers)["id"], 2)

    def test_unknown_condition_is_handled_safely(self):
        offers = [
            {"id": 1, "price": 999, "source": "other", "condition": None},
            {"id": 2, "price": 1000, "source": "other", "condition": "used"},
        ]
        self.assertEqual(select_best_offer(offers)["id"], 2)

    def test_family_page_includes_only_same_family_offers(self):
        product_service = ProductService()
        product_service.create_product(
            name="MacBook Pro M1 13",
            price=999,
            source="ebay",
            url="https://www.ebay.com/itm/123456789012",
        )
        product_service.create_product(
            name="Apple MacBook Pro M1",
            price=970,
            source="amazon",
            url="https://www.amazon.com/dp/B012345678",
        )
        product_service.create_product(
            name="AirPods Pro",
            price=219,
            source="ebay",
            url="https://www.ebay.com/itm/123456789013",
        )

        page = ProductSearchController(product_service=product_service).get_family_page(
            family_key="macbook-pro-m1"
        )
        offer_names = [page["best_offer"]["name"]] + [offer["name"] for offer in page["other_offers"]]
        self.assertIn("MacBook Pro M1 13", offer_names)
        self.assertIn("Apple MacBook Pro M1", offer_names)
        self.assertNotIn("AirPods Pro", offer_names)


if __name__ == "__main__":
    unittest.main()
