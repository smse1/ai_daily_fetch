from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .utils import ensure_dir, keyword_summary


class DigestWriter:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.data_dir = repo_root / "data"
        self.report_dir = repo_root / "reports"
        ensure_dir(self.data_dir)
        ensure_dir(self.report_dir)

    def write_report(self, date_str: str, new_items: list[dict], all_items: list[dict]) -> Path:
        report_path = self.report_dir / f"{date_str}.md"
        grouped = defaultdict(list)
        for item in new_items:
            grouped[item["source"]].append(item)

        keywords = keyword_summary([item["title"] for item in new_items], top_n=12)
        total_sources = len(grouped)

        lines: list[str] = []
        lines.append(f"# AI 每日动态日报 - {date_str}")
        lines.append("")
        lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- 今日新增：{len(new_items)} 条")
        lines.append(f"- 涉及来源：{total_sources} 个")
        lines.append(f"- 历史累计：{len(all_items)} 条")
        lines.append("")

        if keywords:
            lines.append("## 今日高频关键词")
            lines.append("")
            lines.append(", ".join(f"`{word}`×{count}" for word, count in keywords))
            lines.append("")

        if not new_items:
            lines.append("## 今日无新增内容")
            lines.append("")
            lines.append("可能原因：来源未更新、页面结构变化、网络抓取失败。")
            report_path.write_text("\n".join(lines), encoding="utf-8")
            return report_path

        lines.append("## 今日新增内容")
        lines.append("")
        for source, items in grouped.items():
            lines.append(f"### {source}（{len(items)} 条）")
            lines.append("")
            for idx, item in enumerate(items, start=1):
                published = item.get("published") or "未提供"
                lines.append(f"{idx}. [{item['title']}]({item['url']})")
                lines.append(f"   - 发布时间：{published}")
                if item.get("summary"):
                    summary = item["summary"].replace("\n", " ").strip()
                    if len(summary) > 220:
                        summary = summary[:220] + "..."
                    lines.append(f"   - 摘要：{summary}")
            lines.append("")

        lines.append("## 说明")
        lines.append("")
        lines.append("- 本报告按当天抓取去重后的新增链接生成。")
        lines.append("- 若部分站点没有公开发布时间，报告中会显示“未提供”。")
        lines.append("- 你可以继续接入邮件、飞书、企业微信、Telegram 推送。")
        lines.append("")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path
