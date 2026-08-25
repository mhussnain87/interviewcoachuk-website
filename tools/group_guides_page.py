#!/usr/bin/env python3
"""Regroups /blog/ cards into sector sections. Re-runnable."""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(REPO, "blog", "index.html")

SECTIONS = [
    ("NHS, Healthcare & Social Care", ("nhs", "midwife", "healthcare-assistant", "paramedic", "social-worker")),
    ("Civil Service & Public Sector", ("civil-service",)),
    ("Emergency Services & Uniformed Roles", ("police",)),
    ("Education", ("teaching",)),
    ("Business, Retail & Graduate", ("retail", "amazon", "graduate")),
    ("Interview Skills & Techniques", ("star", "competency", "behavioural",
        "tell-me", "strengths", "why-do-you", "interview-tips", "uk-job")),
]
FALLBACK = "More Guides"

s = open(p, encoding="utf-8").read()
cards = re.findall(r'<a href="/blog/[^"]+" class="blog-card">.*?</a>', s, re.S)
assert cards, "no blog cards found"

def bucket(card):
    href = re.search(r'href="/blog/([^"]+)/"', card).group(1)
    for name, keys in SECTIONS:
        if any(k in href for k in keys):
            return name
    return FALLBACK

groups = {}
for c in cards:
    groups.setdefault(bucket(c), []).append(c)

parts = []
order = [n for n, _ in SECTIONS] + [FALLBACK]
for name in order:
    if name not in groups:
        continue
    sid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    parts.append(f'<section class="guide-section" id="{sid}">')
    parts.append(f'  <h2 class="guide-section-title">{name}</h2>')
    parts.append('  <div class="blog-grid">')
    parts.extend("    " + c for c in groups[name])
    parts.append("  </div>")
    parts.append("</section>")
new_grid_area = "\n".join(parts)

CSS = """
  .guide-section-title { font-size:1.3rem; color:#0f2137; margin:2.2rem 0 1rem;
    padding-bottom:.4rem; border-bottom:2px solid #17a2b8; display:inline-block; }
"""

JS = """
<script>
(function(){
  var input = document.getElementById('guide-search');
  if (!input) return;
  input.addEventListener('input', function(){
    setTimeout(function(){
      document.querySelectorAll('.guide-section').forEach(function(sec){
        var any = Array.prototype.some.call(
          sec.querySelectorAll('.blog-card'),
          function(c){ return c.style.display !== 'none'; });
        sec.style.display = any ? '' : 'none';
      });
    }, 0);
  });
})();
</script>
"""

if 'class="guide-section"' in s:
    start = s.index('<section class="guide-section"')
    end = s.rindex("</section>") + len("</section>")
    s = s[:start] + new_grid_area + s[end:]
else:
    m = re.search(r'<div class="blog-grid">.*</div>', s, re.S)
    assert m, "grid not found"
    s = s[:m.start()] + new_grid_area + s[m.end():]
    s = s.replace("</style>", CSS + "</style>", 1)
    s = s.replace("</body>", JS + "</body>", 1)

open(p, "w", encoding="utf-8").write(s)
total = sum(len(v) for v in groups.values())
print(f"grouped {total} guides into {len(groups)} sections")
