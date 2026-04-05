from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse, urlunparse

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with", "from",
    "by", "at", "is", "are", "be", "as", "it", "its", "into", "new", "how", "what",
    "why", "this", "that", "their", "your", "our", "will", "can", "more", "using",
    "latest", "about", "than", "after", "over", "under", "through", "via", "ai",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()



def slugify_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")



def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)



def normalize_url(url: str, base_url: str | None = None) -> str:
    if base_url:
        url = urljoin(base_url, url)
    parsed = urlparse(url)
    clean = parsed._replace(query="", fragment="")
    normalized = urlunparse(clean)
    return normalized.rstrip("/")



def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()



def article_id(url: str, title: str) -> str:
    raw = f"{url}::{title}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]



def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))



def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")



def keyword_summary(titles: Iterable[str], top_n: int = 10) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for title in titles:
        words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", title.lower())
        for w in words:
            if w not in STOPWORDS:
                counter[w] += 1
    return counter.most_common(top_n)
