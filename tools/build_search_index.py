#!/usr/bin/env python3
"""Builds assets/search-index.json from all blog guides.
Run from repo root: python3 tools/build_search_index.py"""
import glob, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()

items = []
for p in sorted(glob.glob(os.path.join(REPO, "blog", "*", "index.html"))):
    slug = os.path.basename(os.path.dirname(p))
    h = open(p, encoding="utf-8").read()
    title = re.search(r"<h1>(.*?)</h1>", h, re.S)
    quick = re.search(r"Quick answer:</b>\s*(.*?)</div>", h, re.S)
    heads = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", h, re.S)
    items.append({
        "t": clean(title.group(1) if title else slug),
        "u": f"/blog/{slug}/",
        "d": clean(quick.group(1) if quick else "")[:180],
        "h": " | ".join(clean(x) for x in heads)[:1500],
    })

out = os.path.join(REPO, "assets", "search-index.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(items, open(out, "w", encoding="utf-8"), ensure_ascii=True)
print(f"search index: {len(items)} guides -> assets/search-index.json")
