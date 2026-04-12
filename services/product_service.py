from adapters.ebay import EbayAdapter
from adapters.willhaben import WillhabenAdapter
from database import (
    get_offers_by_family_key,
    get_products_missing_family,
    init_db,
    insert_products,
    insert_products_if_missing,
    search_products,
    update_product_family_fields,
)
from services.offer_ranking import (
    CONDITION_PRIORITY,
    SOURCE_PRIORITY,
    build_offer_sort_key,
    select_best_offer,
)
from services.product_family import derive_display_name, derive_family_key
from services.search import is_exact_match, is_prefix_token_match, normalize


class ProductService:
    def __init__(self):
        self.adapters = [WillhabenAdapter(), EbayAdapter()]
        init_db()
        self._ensure_product_family_fields()

    def _get_search_candidate_name(self, product):
        return product.get("display_name") or product.get("name") or ""

    def _filter_products_by_query(self, products, query):
        normalized_query = normalize(query)
        if not normalized_query:
            return []

        exact_matches = [
            product
            for product in products
            if is_exact_match(normalized_query, self._get_search_candidate_name(product))
        ]
        if exact_matches:
            return exact_matches

        return [
            product
            for product in products
            if is_prefix_token_match(normalized_query, self._get_search_candidate_name(product))
        ]

    def _ensure_product_family_fields(self):
        rows = get_products_missing_family()
        for product_id, name in rows:
            family_key = derive_family_key(name)
            display_name = derive_display_name(name)
            if family_key and display_name:
                update_product_family_fields(product_id, family_key, display_name)

    def _annotate_offer(self, product):
        normalized_source = str(product.get("source") or "").strip().lower()
        normalized_condition = str(product.get("condition") or "").strip().lower().replace(" ", "_")
        return {
            **product,
            "url": str(product.get("url") or "").strip(),
            "condition": str(product.get("condition") or "Unknown"),
            "family_key": product.get("family_key") or derive_family_key(product.get("name")),
            "display_name": product.get("display_name") or derive_display_name(product.get("name")),
            "condition_rank": CONDITION_PRIORITY.get(
                normalized_condition if normalized_condition in CONDITION_PRIORITY else "unknown",
                0,
            ),
            "source_rank": SOURCE_PRIORITY.get(
                normalized_source if normalized_source in SOURCE_PRIORITY else "other",
                0,
            ),
        }

    def rank_products(self, products):
        annotated_products = [self._annotate_offer(product) for product in products or []]
        ranked_products = sorted(annotated_products, key=build_offer_sort_key)
        for index, product in enumerate(ranked_products):
            product["is_best_offer"] = index == 0
        return ranked_products

    def select_best_offer(self, products):
        ranked_products = self.rank_products(products)
        best_offer = select_best_offer(ranked_products)
        if not best_offer:
            return None
        return next(
            (
                product
                for product in ranked_products
                if int(product.get("id", 0) or 0) == int(best_offer.get("id", 0) or 0)
            ),
            best_offer,
        )

    def load_products(self, query="", user_id=None):
        all_products = []
        for adapter in self.adapters:
            products = adapter.search_products(query)
            all_products.extend(products)

        inserted_count = insert_products(all_products, user_id=user_id)
        return inserted_count

    def add_product(self, product, user_id=None):
        normalized_product = {
            "name": str(product.get("name", "")).strip(),
            "price": float(product.get("price", 0)),
            "url": str(product.get("url", "")).strip(),
            "source": str(product.get("source", "")).strip(),
            "image": str(product.get("image", "")).strip(),
            "family_key": derive_family_key(product.get("name", "")),
            "display_name": derive_display_name(product.get("name", "")),
            "user_id": product.get("user_id", user_id),
        }
        inserted_count = insert_products([normalized_product], user_id=user_id)
        return {
            "ok": inserted_count > 0,
            "message": "Product added." if inserted_count > 0 else "Failed to add product.",
        }

    def create_product(
        self,
        name,
        price,
        source,
        url,
        condition="New",
        original_price=None,
        user_id=None,
    ):
        normalized_product = {
            "name": str(name or "").strip(),
            "price": float(price or 0),
            "url": str(url or "").strip(),
            "source": str(source or "").strip(),
            "image": "",
            "family_key": derive_family_key(name),
            "display_name": derive_display_name(name),
            "user_id": user_id,
        }
        inserted_count = insert_products_if_missing([normalized_product], user_id=user_id)
        return {
            "ok": inserted_count > 0,
            "message": "Product added." if inserted_count > 0 else "Product already exists.",
            "product": {
                **normalized_product,
                "condition": str(condition or "").strip() or "New",
                "original_price": (
                    float(original_price) if original_price is not None else None
                ),
            },
        }

    def search(self, query, user_id=None):
        rows = search_products(query, user_id=user_id)
        return [
            {
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "url": row[3],
                "source": row[4],
                "image": row[5] or "",
                "family_key": row[6] or derive_family_key(row[1]),
                "display_name": row[7] or derive_display_name(row[1]),
                "condition": "Unknown",
                "user_id": row[8],
                "created_at": row[9],
            }
            for row in rows
        ]

    def get_offers_by_family_key(self, family_key, user_id=None):
        rows = get_offers_by_family_key(family_key, user_id=user_id)
        return self.rank_products(
            [
                {
                    "id": row[0],
                    "name": row[1],
                    "price": row[2],
                    "url": row[3],
                    "source": row[4],
                    "image": row[5] or "",
                    "family_key": row[6] or derive_family_key(row[1]),
                    "display_name": row[7] or derive_display_name(row[1]),
                    "condition": "Unknown",
                    "user_id": row[8],
                    "created_at": row[9],
                }
                for row in rows
            ]
        )

    def get_external_products(self, query=""):
        external_products = []
        for adapter in self.adapters:
            external_products.extend(adapter.search_products(query))
        return external_products

    def search_marketplace_products(self, query="", filters=None, user_id=None):
        filters = filters or {}

        db_products = self.search(query="", user_id=user_id)
        external_products = self.get_external_products(query=query)

        normalized_external = []
        for idx, product in enumerate(external_products):
            normalized_external.append(
                {
                    "id": product.get("id", -(idx + 1)),
                    "name": product["name"],
                    "price": product["price"],
                    "url": product["url"],
                    "source": product["source"],
                    "image": product.get("image", ""),
                    "family_key": product.get("family_key") or derive_family_key(product["name"]),
                    "display_name": product.get("display_name") or derive_display_name(product["name"]),
                    "condition": product.get("condition", "Unknown"),
                    "user_id": None,
                }
            )

        results = db_products + normalized_external
        results = self._filter_products_by_query(results, query)

        source_filter = str(filters.get("source", "")).strip()
        if source_filter:
            results = [item for item in results if item.get("source") == source_filter]

        return self.rank_products(results)
