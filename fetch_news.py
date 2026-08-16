#!/usr/bin/env python3
"""
Haber İzleyici - RSS kaynaklarını çeker, anahtar kelimelere göre işaretler,
data/news.json dosyasına yazar. Bu dosya GitHub Pages üzerinden site.html
tarafından okunur.
"""

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import yaml

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.yaml"
DATA_PATH = ROOT / "data" / "news.json"
MAX_STORED_ITEMS = 500  # dosyanın şişmemesi için tutulan toplam haber sayısı üst sınırı


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_existing_items():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("items", [])
    return []


def make_id(source_name, link, title):
    raw = f"{source_name}|{link}|{title}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def matches_keywords(title, summary, keywords):
    if not keywords:
        return True, []
    haystack = f"{title} {summary}".lower()
    hits = [kw for kw in keywords if kw.strip() and kw.strip().lower() in haystack]
    return (len(hits) > 0), hits


def parse_entry_date(entry):
    for field in ("published_parsed", "updated_parsed"):
        val = getattr(entry, field, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def fetch_source(source, keywords, max_items):
    name = source["name"]
    url = source["url"]
    items = []
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            print(f"[UYARI] '{name}' kaynağı okunamadı: {feed.bozo_exception}")
            return items

        for entry in feed.entries[:max_items]:
            title = strip_html(getattr(entry, "title", ""))
            summary = strip_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            link = getattr(entry, "link", "")
            if not title or not link:
                continue

            matched, hits = matches_keywords(title, summary, keywords)
            items.append({
                "id": make_id(name, link, title),
                "source": name,
                "title": title,
                "summary": summary[:400],
                "link": link,
                "published": parse_entry_date(entry),
                "matched": matched,
                "matched_keywords": hits,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        print(f"[HATA] '{name}' kaynağı çekilirken sorun oluştu: {e}")

    return items


def main():
    config = load_config()
    sources = config.get("sources", [])
    keywords = config.get("keywords", []) or []
    max_items = config.get("max_items_per_source", 30)

    print(f"{len(sources)} kaynak taranıyor, {len(keywords)} anahtar kelime aktif...")

    existing_items = load_existing_items()
    existing_ids = {item["id"] for item in existing_items}

    all_new_items = []
    for source in sources:
        fetched = fetch_source(source, keywords, max_items)
        new_ones = [it for it in fetched if it["id"] not in existing_ids]
        all_new_items.extend(new_ones)
        print(f"  - {source['name']}: {len(fetched)} haber çekildi, {len(new_ones)} yeni")

    combined = all_new_items + existing_items
    combined.sort(key=lambda x: x["published"], reverse=True)
    combined = combined[:MAX_STORED_ITEMS]

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "keyword_filter": keywords,
        "total_items": len(combined),
        "new_items_this_run": len(all_new_items),
        "items": combined,
    }

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandı. Toplam {len(combined)} haber kayıtlı, bu çalıştırmada {len(all_new_items)} yeni haber eklendi.")


if __name__ == "__main__":
    main()
