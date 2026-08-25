#!/usr/bin/env python3
"""Adds anchor IDs to guide H2s + collapsible 'On this page' TOC. Idempotent."""
import glob, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOC_CSS = """
  .icuk-toc { background:#eef4f8; border-radius:12px; padding:6px 18px; margin:1.5rem 0; }
  .icuk-toc summary { cursor:pointer; font-weight:600; padding:10px 0; color:#0f2137; }
  .icuk-toc ol { margin:0 0 12px; padding-left:1.4rem; }
  .icuk-toc li { margin:6px 0; }
  .icuk-toc a { color:#17a2b8; text-decoration:none; }
  .icuk-toc a:hover { text-decoration:underline; }
"""

def slugify(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t[:60] or "section"

def process(path):
    h = open(path, encoding="utf-8").read()
    if '<details class="icuk-toc"' in h:
        return "skip (has TOC)"
    art = re.search(r"<article>(.*?)</article>", h, re.S)
    if not art:
        return "skip (no article)"
    body = art.group(1)
    seen, entries = set(), []
    def add_id(m):
        attrs, text = m.group(1), m.group(2)
        if "id=" in attrs:
            mid = re.search(r'id="([^"]+)"', attrs)
            entries.append((mid.group(1), re.sub(r"<[^>]+>", "", text).strip()))
            return m.group(0)
        sid = slugify(text)
        while sid in seen:
            sid += "-2"
        seen.add(sid)
        entries.append((sid, re.sub(r"<[^>]+>", "", text).strip()))
        return f'<h2{attrs} id="{sid}">{text}</h2>'
    new_body = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, body, flags=re.S)
    if len(entries) < 3:
        return "skip (<3 sections)"
    toc_items = "\n".join(f'      <li><a href="#{sid}">{t}</a></li>' for sid, t in entries)
    toc = ('\n<details class="icuk-toc"><summary>On this page</summary>\n'
           f'    <ol>\n{toc_items}\n    </ol>\n  </details>\n')
    qa = re.search(r'<div class="quick-answer">.*?</div>', new_body, re.S)
    if qa:
        new_body = new_body[:qa.end()] + toc + new_body[qa.end():]
    else:
        new_body = toc + new_body
    h = h.replace(art.group(0), "<article>" + new_body + "</article>", 1)
    if ".icuk-toc" not in h:
        h = h.replace("</style>", TOC_CSS + "</style>", 1)
    open(path, "w", encoding="utf-8").write(h)
    return f"OK ({len(entries)} sections)"

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(REPO, "blog", "*", "index.html"))):
        print(f"{os.path.relpath(p, REPO)}: {process(p)}")
