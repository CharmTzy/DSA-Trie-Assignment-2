from __future__ import annotations

import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from catalog_search import CatalogSearch
from trie import Trie, normalize_text


class TrieTests(unittest.TestCase):
    def test_normalize_text(self) -> None:
        self.assertEqual(normalize_text("  Greek-Yogurt!! "), "greek yogurt")

    def test_prefix_search_returns_inserted_products(self) -> None:
        trie = Trie()
        trie.insert("apple", 1)
        trie.insert("application", 2)

        result = trie.search("app")

        self.assertEqual(result.product_ids, {1, 2})
        self.assertEqual(result.node_visits, 3)


class CatalogSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.search_engine = CatalogSearch()

    def test_alias_search_finds_matching_product(self) -> None:
        payload = self.search_engine.search("yog")
        result_names = {product["name"] for product in payload["results"]}

        self.assertIn("Greek Yogurt Vanilla", result_names)

    def test_category_filter_limits_results(self) -> None:
        payload = self.search_engine.search("", category="Snacks")

        self.assertTrue(payload["results"])
        self.assertTrue(all(product["category"] == "Snacks" for product in payload["results"]))

    def test_unknown_prefix_returns_no_results(self) -> None:
        payload = self.search_engine.search("zzzzzz")

        self.assertEqual(payload["results"], [])
        self.assertEqual(payload["total_matches"], 0)


if __name__ == "__main__":
    unittest.main()
