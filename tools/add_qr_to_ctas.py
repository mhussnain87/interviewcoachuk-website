#!/usr/bin/env python3
"""Add desktop-only QR block to every icuk-cta-banner. Idempotent."""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QR_CSS = """
  .cta-qr { display:flex; align-items:center; gap:12px; margin-top:14px;
            padding-top:12px; border-top:1px solid rgba(255,255,255,.15); }
  .cta-qr img { width:84px; height:84px; background:#fff; border-radius:8px; padding:5px; }
  .cta-qr span { color:#b9c6d8; font-size:.85rem; line-height:1.4; }
  @media (max-width: 820px) { .cta-qr { display:none; } }
"""

QR_HTML = ('\n  <div class="cta-qr"><img src="/assets/qr-get-app.svg" '
           'alt="QR code to download Interview Coach UK" loading="lazy">'
           '<span>On desktop? Point your phone camera here - it takes you '
           'straight to the right store.</span></div>\n')

def process(path):
    html = open(path, encoding="utf-8").read()
    if "cta-qr" in html:
        return "skip (already has QR)"
    if "icuk-cta-banner" not in html:
        return "skip (no CTA banner)"
    html = html.replace("</style>", QR_CSS + "</style>", 1)
    html, n = re.subn(r'(<span class="cta-featureb">.*?</span>)',
                      lambda m: m.group(1) + QR_HTML, html, flags=re.S)
    if n == 0:
        return "skip (no cta-featureb anchor)"
    open(path, "w", encoding="utf-8").write(html)
    return f"OK ({n} banner(s))"

def main():
    targets = sorted(glob.glob(os.path.join(REPO, "blog", "*", "index.html")))
    if not targets:
        sys.exit("ERROR: no blog posts found")
    for t in targets:
        print(f"{os.path.relpath(t, REPO)}: {process(t)}")
    print("Done. Review with: git diff --stat")

if __name__ == "__main__":
    main()
