from __future__ import annotations

from dataclasses import asdict, dataclass

from trie import Trie, normalize_text


@dataclass(frozen=True, slots=True)
class Product:
    product_id: int
    name: str
    category: str
    aisle: str
    price: float
    in_stock: bool
    description: str
    popularity: int
    aliases: tuple[str, ...]


CATALOG: tuple[Product, ...] = (
    Product(1, "Greek Yogurt Vanilla", "Dairy", "Aisle 2", 2.95, True, "Protein-rich vanilla yogurt cup.", 94, ("Greek Yogurt", "Yogurt", "Vanilla Yogurt")),
    Product(2, "Wholemeal Bread", "Bakery", "Aisle 5", 3.20, True, "Fresh wholemeal sandwich loaf.", 88, ("Bread", "Whole Wheat Bread", "Loaf")),
    Product(3, "Banana", "Produce", "Aisle 1", 1.10, True, "Sweet ripe bananas sold by bunch.", 96, ("Bananas", "Yellow Banana", "Fruit")),
    Product(4, "Fuji Apple", "Produce", "Aisle 1", 1.35, True, "Crisp red apples for snacks.", 91, ("Apple", "Red Apple", "Fuji")),
    Product(5, "Brown Eggs 12 Pack", "Dairy", "Aisle 2", 4.50, True, "Free-range brown eggs.", 89, ("Eggs", "Egg Carton", "12 Eggs")),
    Product(6, "Fresh Spinach", "Produce", "Aisle 1", 2.40, True, "Leafy spinach for salads and stir-fries.", 77, ("Spinach", "Baby Spinach", "Leafy Greens")),
    Product(7, "Chicken Breast Fillet", "Meat", "Aisle 8", 8.90, True, "Boneless chicken breast fillets.", 84, ("Chicken Breast", "Chicken", "Fillet")),
    Product(8, "Salmon Fillet", "Seafood", "Aisle 9", 11.50, False, "Fresh salmon fillet portions.", 79, ("Salmon", "Fish Fillet", "Fresh Salmon")),
    Product(9, "Jasmine Rice 5kg", "Pantry", "Aisle 6", 13.80, True, "Fragrant long-grain jasmine rice.", 90, ("Rice", "Jasmine Rice", "5kg Rice")),
    Product(10, "Spaghetti Pasta", "Pantry", "Aisle 6", 2.25, True, "Durum wheat spaghetti.", 80, ("Pasta", "Spaghetti", "Noodles")),
    Product(11, "Tomato Pasta Sauce", "Pantry", "Aisle 6", 3.40, True, "Classic tomato and herb pasta sauce.", 75, ("Tomato Sauce", "Pasta Sauce", "Marinara")),
    Product(12, "Cheddar Cheese Slices", "Dairy", "Aisle 2", 4.20, True, "Mild cheddar slices for sandwiches.", 86, ("Cheese", "Cheddar", "Cheese Slices")),
    Product(13, "Orange Juice", "Beverages", "Aisle 10", 3.60, True, "No added sugar chilled orange juice.", 82, ("Juice", "Orange", "OJ")),
    Product(14, "Mineral Water 1.5L", "Beverages", "Aisle 10", 1.20, True, "Still mineral water bottle.", 87, ("Water", "Bottle Water", "Mineral Water")),
    Product(15, "Potato Chips Sea Salt", "Snacks", "Aisle 11", 2.80, True, "Crispy sea salt potato chips.", 73, ("Chips", "Crisps", "Potato Chips")),
    Product(16, "Dark Chocolate Bar", "Snacks", "Aisle 11", 3.10, True, "70 percent cocoa dark chocolate.", 78, ("Chocolate", "Dark Chocolate", "Chocolate Bar")),
)


class CatalogSearch:
    def __init__(self, products: tuple[Product, ...] = CATALOG) -> None:
        self.products = products
        self.product_by_id = {product.product_id: product for product in products}
        self.categories = sorted({product.category for product in products})
        self.title_trie = Trie()
        self.title_alias_trie = Trie()

        for product in products:
            self.title_trie.insert(product.name, product.product_id)
            self.title_alias_trie.insert(product.name, product.product_id)
            for alias in product.aliases:
                self.title_alias_trie.insert(alias, product.product_id)

    def search(self, query: str, category: str = "", limit: int = 8, search_mode: str = "title_aliases") -> dict:
        normalized_category = category.strip()
        normalized_search_mode = self._normalize_search_mode(search_mode)
        active_trie = self._get_trie(normalized_search_mode)
        trie_result = active_trie.search(query)

        if trie_result.normalized_query:
            matched_products = [self.product_by_id[product_id] for product_id in trie_result.product_ids]
        else:
            matched_products = list(self.products)

        if normalized_category:
            matched_products = [
                product for product in matched_products if product.category.lower() == normalized_category.lower()
            ]

        sorted_products = sorted(
            matched_products,
            key=lambda product: self._sort_key(product, trie_result.normalized_query, normalized_search_mode),
        )

        limited_products = sorted_products[: max(1, limit)]

        return {
            "query": query,
            "normalized_query": trie_result.normalized_query,
            "category_filter": normalized_category,
            "search_mode": normalized_search_mode,
            "categories": self.categories,
            "results": [self._serialize_product(product) for product in limited_products],
            "result_count": len(limited_products),
            "total_matches": len(sorted_products),
            "metrics": {
                "node_visits": trie_result.node_visits,
                "candidate_count": trie_result.candidate_count if trie_result.normalized_query else len(matched_products),
                "indexed_terms": active_trie.indexed_terms,
                "total_nodes": active_trie.total_nodes,
            },
        }

    def _sort_key(self, product: Product, normalized_query: str, search_mode: str) -> tuple:
        name = normalize_text(product.name)
        aliases = [normalize_text(alias) for alias in product.aliases]

        exact_title_match = normalized_query != "" and name == normalized_query
        exact_alias_match = search_mode == "title_aliases" and normalized_query != "" and any(
            alias == normalized_query for alias in aliases
        )
        title_starts = normalized_query != "" and name.startswith(normalized_query)
        alias_starts = search_mode == "title_aliases" and normalized_query != "" and any(
            alias.startswith(normalized_query) for alias in aliases
        )

        if exact_title_match:
            match_priority = 0
        elif exact_alias_match:
            match_priority = 1
        elif title_starts:
            match_priority = 2
        elif alias_starts:
            match_priority = 3
        else:
            match_priority = 4

        return (match_priority, -product.popularity, product.name)

    @staticmethod
    def _normalize_search_mode(search_mode: str) -> str:
        normalized = search_mode.strip().lower().replace("-", "_").replace(" ", "_")
        return "title" if normalized == "title" else "title_aliases"

    def _get_trie(self, search_mode: str) -> Trie:
        if search_mode == "title":
            return self.title_trie
        return self.title_alias_trie

    @staticmethod
    def _serialize_product(product: Product) -> dict:
        product_data = asdict(product)
        product_data["price"] = f"{product.price:.2f}"
        return product_data
