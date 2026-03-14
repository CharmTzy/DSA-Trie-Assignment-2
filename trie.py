from __future__ import annotations

from dataclasses import dataclass, field


def normalize_text(text: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return " ".join(cleaned.split())


@dataclass(slots=True)
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    product_ids: set[int] = field(default_factory=set)
    terminal: bool = False


@dataclass(slots=True)
class TrieSearchResult:
    normalized_query: str
    product_ids: set[int]
    node_visits: int
    candidate_count: int


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()
        self.total_nodes = 1
        self.indexed_terms = 0

    def insert(self, term: str, product_id: int) -> None:
        normalized = normalize_text(term)
        if not normalized:
            return

        self.indexed_terms += 1
        node = self.root
        node.product_ids.add(product_id)

        for char in normalized:
            if char not in node.children:
                node.children[char] = TrieNode()
                self.total_nodes += 1
            node = node.children[char]
            node.product_ids.add(product_id)

        node.terminal = True

    def search(self, prefix: str) -> TrieSearchResult:
        normalized = normalize_text(prefix)
        if not normalized:
            return TrieSearchResult(
                normalized_query="",
                product_ids=set(self.root.product_ids),
                node_visits=0,
                candidate_count=len(self.root.product_ids),
            )

        node = self.root
        node_visits = 0

        for char in normalized:
            child = node.children.get(char)
            node_visits += 1
            if child is None:
                return TrieSearchResult(
                    normalized_query=normalized,
                    product_ids=set(),
                    node_visits=node_visits,
                    candidate_count=0,
                )
            node = child

        return TrieSearchResult(
            normalized_query=normalized,
            product_ids=set(node.product_ids),
            node_visits=node_visits,
            candidate_count=len(node.product_ids),
        )
