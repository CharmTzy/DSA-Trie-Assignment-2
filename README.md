# Trie Grocery Search Demo

This project is a small Trie-based autocomplete application for `INF1008 Assignment 2`.

## Features

- Prefix search powered by a Trie
- Product aliases that map multiple search terms to the same item
- Category filter and ranked results
- Trie metrics displayed in the UI
- Python standard-library backend with no external dependencies

## Project Files

- `trie.py`: core Trie data structure
- `catalog_search.py`: product catalog and search logic
- `server.py`: HTTP server and JSON API
- `main.py`: entry point
- `static/`: frontend files
- `tests/test_search.py`: basic tests

## Run the Application

```bash
cd "/Users/waiyan/Documents/SIT Y1S2/INF1008 Data Structures & Algorithms/Assignment 2"
python3 main.py
```

Then open `http://127.0.0.1:8000` in your browser.

To use a different port:

```bash
python3 main.py --port 8080
```

## Run the Tests

```bash
cd "/Users/waiyan/Documents/SIT Y1S2/INF1008 Data Structures & Algorithms/Assignment 2"
python3 -m unittest discover -s tests -v
```

## Suggested Demo Flow

1. Search `yog` to show alias-based matching for yogurt.
2. Search `rice` to show fast prefix retrieval.
3. Apply the `Snacks` category filter.
4. Search a missing prefix like `zzz` to show no-match handling.
