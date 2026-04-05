from __future__ import annotations

import json
import re
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from .utils import article_id, normalize_space, normalize_url, utc_now_iso

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


class FetchError(RuntimeError):
    pass


class SourceFetcher:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.sources: list[dict[str, Any]] = json.loads(config_path.read_text(encoding="utf-8"))

    def fetch_all(self) -> list[dict[str, Any]]:
        articles: list[dict[str, Any]] = []
        for source in self.sources:
            try:
                source_type = source["type"]
                if source_type == "rss":
                    items = self._fetch_rss(source)
                elif source_type == "html":
                    items = self._fetch_html(source)
                else:
                    raise FetchError(f"不支持的来源类型: {source_type}")
                articles.extend(items)
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] 抓取失败: {source['name']} -> {exc}")
        return articles

    def _fetch_rss(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        feed = feedparser.parse(source["url"])
        if getattr(feed, "bozo", 0):
            print(f"[WARN] RSS 解析可能异常: {source['name']}")

        items: list[dict[str, Any]] = []
        for entry in feed.entries[: source.get("limit", 10)]:
            title = normalize_space(getattr(entry, "title", ""))
            link = normalize_url(getattr(entry, "link", ""))
            summary = normalize_space(getattr(entry, "summary", ""))
            published = self._parse_published(entry)
            if not title or not link:
                continue
            items.append(
                {
                    "id": article_id(link, title),
                    "source": source["name"],
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "published": published,
                    "fetched_at": utc_now_iso(),
                }
            )
        return items

    def _fetch_html(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        response = requests.get(source["url"], headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        include_patterns = source.get("include_patterns", [])
        exclude_patterns = source.get("exclude_patterns", [])
        base_url = source.get("base_url")

        seen_links: set[str] = set()
        items: list[dict[str, Any]] = []

        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            title = normalize_space(a.get_text(" ", strip=True))

            if not href or not title or len(title) < 8:
                continue

            link = normalize_url(href, base_url=base_url)
            path = re.sub(r"https?://[^/]+", "", link)

            if include_patterns and not any(p in path for p in include_patterns):
                continue
            if self._is_excluded(path, exclude_patterns):
                continue
            if link in seen_links:
                continue

            seen_links.add(link)
            items.append(
                {
                    "id": article_id(link, title),
                    "source": source["name"],
                    "title": title,
                    "url": link,
                    "summary": "",
                    "published": "",
                    "fetched_at": utc_now_iso(),
                }
            )
            if len(items) >= source.get("limit", 10):
                break

        return items

    @staticmethod
    def _is_excluded(path: str, exclude_patterns: list[str]) -> bool:
        stripped = path.rstrip("/")
        for pattern in exclude_patterns:
            if stripped == pattern.rstrip("/"):
                return True
        return False

    @staticmethod
    def _parse_published(entry: Any) -> str:
        candidates = [
            getattr(entry, "published", ""),
            getattr(entry, "updated", ""),
            getattr(entry, "created", ""),
        ]
        for value in candidates:
            if not value:
                continue
            try:
                return parsedate_to_datetime(value).isoformat()
            except Exception:  # noqa: BLE001
                continue
        return ""
