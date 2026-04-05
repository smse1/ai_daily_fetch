from __future__ import annotations

from pathlib import Path

from src.digest import DigestWriter
from src.fetch import SourceFetcher
from src.utils import ensure_dir, load_json, save_json, slugify_date


REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
CONFIG_PATH = REPO_ROOT / "config" / "sources.json"
ARTICLES_PATH = DATA_DIR / "articles.json"
LAST_RUN_PATH = DATA_DIR / "last_run.json"



def deduplicate(old_items: list[dict], fetched_items: list[dict]) -> tuple[list[dict], list[dict]]:
    known_ids = {item["id"] for item in old_items}
    known_urls = {item["url"] for item in old_items}

    new_items: list[dict] = []
    for item in fetched_items:
        if item["id"] in known_ids or item["url"] in known_urls:
            continue
        new_items.append(item)
        known_ids.add(item["id"])
        known_urls.add(item["url"])

    merged = old_items + new_items
    return merged, new_items



def sort_items(items: list[dict]) -> list[dict]:
    return sorted(
        items,
        key=lambda x: (
            x.get("published", ""),
            x.get("fetched_at", ""),
            x.get("source", ""),
        ),
        reverse=True,
    )



def run() -> None:
    ensure_dir(DATA_DIR)

    existing_items = load_json(ARTICLES_PATH, default=[])
    fetcher = SourceFetcher(CONFIG_PATH)
    fetched_items = fetcher.fetch_all()

    merged_items, new_items = deduplicate(existing_items, fetched_items)
    merged_items = sort_items(merged_items)
    new_items = sort_items(new_items)

    save_json(ARTICLES_PATH, merged_items)
    save_json(
        LAST_RUN_PATH,
        {
            "date": slugify_date(),
            "fetched_count": len(fetched_items),
            "new_count": len(new_items),
            "total_count": len(merged_items),
        },
    )

    writer = DigestWriter(REPO_ROOT)
    report_path = writer.write_report(slugify_date(), new_items, merged_items)

    print(f"本次抓取: {len(fetched_items)} 条")
    print(f"新增内容: {len(new_items)} 条")
    print(f"累计内容: {len(merged_items)} 条")
    print(f"日报位置: {report_path}")


if __name__ == "__main__":
    run()
