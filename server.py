from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
from urllib.parse import parse_qs, urlparse

from catalog_search import CatalogSearch


class LocalThreadingHTTPServer(ThreadingHTTPServer):
    def server_bind(self) -> None:
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = str(host)
        self.server_port = port


def create_handler(search_engine: CatalogSearch, static_dir: Path):
    class SearchRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/":
                self._serve_static_file(static_dir / "index.html")
                return

            if parsed.path == "/api/search":
                self._handle_search(parsed.query)
                return

            if parsed.path.startswith("/static/"):
                requested_path = parsed.path.removeprefix("/static/")
                self._serve_static_file(static_dir / requested_path)
                return

            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args) -> None:
            return

        def _handle_search(self, query_string: str) -> None:
            params = parse_qs(query_string)
            query = params.get("q", [""])[0]
            category = params.get("category", [""])[0]
            limit_raw = params.get("limit", ["8"])[0]

            try:
                limit = max(1, min(12, int(limit_raw)))
            except ValueError:
                limit = 8

            payload = search_engine.search(query=query, category=category, limit=limit)
            self._send_json(payload, HTTPStatus.OK)

        def _serve_static_file(self, file_path: Path) -> None:
            try:
                resolved = file_path.resolve(strict=True)
            except FileNotFoundError:
                self._send_json({"error": "File not found"}, HTTPStatus.NOT_FOUND)
                return

            static_root = static_dir.resolve()
            if static_root not in [resolved, *resolved.parents]:
                self._send_json({"error": "Invalid path"}, HTTPStatus.FORBIDDEN)
                return

            content_type, _ = mimetypes.guess_type(str(resolved))
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type or "application/octet-stream")
            self.end_headers()
            self.wfile.write(resolved.read_bytes())

        def _send_json(self, payload: dict, status: HTTPStatus) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return SearchRequestHandler


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    project_dir = Path(__file__).resolve().parent
    static_dir = project_dir / "static"
    search_engine = CatalogSearch()
    handler = create_handler(search_engine, static_dir)
    server = LocalThreadingHTTPServer((host, port), handler)

    print(f"Serving Trie grocery demo at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Trie grocery search demo.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to.")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind to.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(host=args.host, port=args.port)
