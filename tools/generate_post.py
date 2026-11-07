#!/usr/bin/env python3
"""
Interview Coach UK — blog post generator.

Usage (Mac system Terminal, from website repo root):
  export ANTHROPIC_API_KEY=sk-ant-...   # set once per terminal session, never commit
  python3 tools/generate_post.py \
    --keyword "midwife interview questions" \
    --slug midwife-interview-questions-uk \
    --code midwife            # optional page code for tracking tags

  Dry run (no API call, nothing written; prints the tracking tags):
  python3 tools/generate_post.py --keyword "x" --slug x-interview-questions-uk --dry-run

What it does:
  1. Loads blog/nhs-band-7-interview-questions/index.html as the master template
     (CSS, nav, CTA banners, sidebar, footer all reused verbatim).
  2. Calls the Anthropic API for article content as structured JSON.
  3. Assembles blog/<slug>/index.html, with every App Store ct= and Google Play
     utm tag rewritten to this post's own page code (the template's b7 tags and
     its per-question practice lines are not copied).
  4. Adds the URL to sitemap.xml (lastmod = today).
  5. Inserts a blog-card at the top of blog/index.html.
  6. Prints a review checklist + git commands. NOTHING is committed automatically.
"""
import argparse, json, os, re, sys, datetime, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "blog", "nhs-band-7-interview-questions", "index.html")
SITEMAP = os.path.join(REPO, "sitemap.xml")
BLOG_INDEX = os.path.join(REPO, "blog", "index.html")
MODEL = "claude-sonnet-4-6"
SITE = "https://interviewcoachuk.com"
TEMPLATE_CODE = "b7"  # page code used in the template's ct= / utm_medium tags
SLUG_SUFFIXES = ("-interview-questions-uk", "-interview-questions", "-interview-answers-uk",
                 "-interview-answer-uk", "-interview-answer", "-interview-uk", "-uk")

PROMPT = """You are the content writer for Interview Coach UK (interviewcoachuk.com), a UK interview-prep app. Write a definitive 2026 UK guide targeting the keyword: "{keyword}".

Respond with EXACTLY these seven sections, each starting with its marker line. No other text before, between, or after.

===TITLE===
Page title, max ~65 chars, ends with "(2026 Guide)" where natural, includes the keyword naturally.

===META===
Meta description, 150-160 chars, includes keyword, mentions STAR answers and free 2026 UK guide.

===QUICK===
1-2 sentence direct answer for a highlight box (plain text, no HTML).

===EXCERPT===
25-35 word summary for the blog index card (plain text).

===ARTICLE===
The full article body as HTML. Requirements:
- UK English throughout. Audience: UK job seekers in 2026.
- ~2,500-3,000 words. Use ONLY these tags: h2, h3, p, ul, ol, li, strong, em.
- Structure: (1) h2 "What to expect" section; (2) h2 on what panels assess for this role; (3) h2 "The N most common {keyword}" with 15-18 numbered h3 questions - for EACH give a short paragraph on what the interviewer is testing and how to answer, and for at least 5 of them include a brief worked STAR example (Situation/Task/Action/Result in one flowing paragraph, realistic UK detail); (4) h2 on using the STAR method; (5) h2 "How to prepare in the week before"; (6) h2 "Common mistakes to avoid"; (7) finish with EXACTLY this block: <div class="summary-box"><h3>Key takeaways</h3><ul>...4-6 li items...</ul></div>
- Be specific to the role/sector (bands, frameworks, values, terminology that a real UK panel uses). If salary is mentioned, phrase carefully as typical/approximate for 2026.
- Do NOT include any FAQ section, CTA, links, or images - those are added separately.

===FAQS===
5-6 FAQ pairs, first one answering the most-searched question for this keyword. Format each pair as two lines:
Q: question text
A: concise factual answer, 2-3 sentences, plain text.

===END===
"""

def default_code(slug: str) -> str:
    """Page code for tracking tags, e.g. midwife-interview-questions-uk -> midwife."""
    for suf in SLUG_SUFFIXES:
        if slug.endswith(suf) and len(slug) > len(suf):
            return slug[: -len(suf)]
    return slug

def existing_codes(repo=REPO):
    """Page codes already used by guides (from their ct=<code>-top tags)."""
    codes = {}
    blog = os.path.join(repo, "blog")
    for d in sorted(os.listdir(blog)):
        f = os.path.join(blog, d, "index.html")
        if os.path.isfile(f):
            with open(f, encoding="utf-8") as fh:
                m = re.search(r"ct=([a-z0-9-]+)-top&", fh.read())
            if m:
                codes[m.group(1)] = d
    return codes

def tracking_tags(page: str):
    """All (kind, value) tracking tags in a page, in document order."""
    pat = r"[?&](ct)=([a-z0-9_-]+)|(utm_medium|utm_campaign)(?:=|%3D)([a-z0-9_-]+)"
    return [(m.group(1) or m.group(3), m.group(2) or m.group(4)) for m in re.finditer(pat, page)]

def retag(page: str, code: str, old: str = TEMPLATE_CODE) -> str:
    """Rewrite the template's tracking tags to this page's code and drop the
    template's per-question practice lines. Exits if any template tag survives."""
    page = re.sub(r'[ \t]*<p class="icuk-q-cta">.*?</p>\n?', "", page, flags=re.S)
    o = re.escape(old)
    page = re.sub(rf"([?&]ct=){o}-", rf"\g<1>{code}-", page)
    page = re.sub(rf"(utm_medium=){o}(?=&|\")", rf"\g<1>{code}", page)
    page = re.sub(rf"(utm_medium%3D){o}(?=%26|&|\")", rf"\g<1>{code}", page)
    problems = [f"{k}={v}" for k, v in tracking_tags(page)
                if (k == "ct" and not v.startswith(code + "-"))
                or (k == "utm_medium" and v != code)
                or (k == "ct" and re.fullmatch(rf"{re.escape(code)}-q\d+", v))]
    if "icuk-q-cta" in page.split("</style>")[-1] or problems:
        sys.exit(f"ERROR: tags not rewritten to page code '{code}': {problems or 'icuk-q-cta line left'}")
    return page

def api_call(keyword: str) -> dict:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=...")
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": PROMPT.format(keyword=keyword)}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    )
    print(f"Calling {MODEL} for: {keyword} ...")
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    text = "".join(b.get("text", "") for b in resp.get("content", []))
    def section(name, nxt):
        m = re.search(rf"===({name})===\s*(.*?)\s*==={nxt}===", text, re.S)
        if not m:
            sys.exit(f"ERROR: model response missing section {name}")
        return m.group(2).strip()
    data = {
        "title": section("TITLE", "META"),
        "meta_description": section("META", "QUICK"),
        "quick_answer": section("QUICK", "EXCERPT"),
        "excerpt": section("EXCERPT", "ARTICLE"),
        "article_html": section("ARTICLE", "FAQS"),
    }
    faq_block = section("FAQS", "END")
    faqs = []
    for m in re.finditer(r"Q:\s*(.+?)\s*\nA:\s*(.+?)(?=\nQ:|\Z)", faq_block, re.S):
        faqs.append({"q": m.group(1).strip(), "a": " ".join(m.group(2).split())})
    if len(faqs) < 3:
        sys.exit("ERROR: fewer than 3 FAQs parsed from model response")
    data["faqs"] = faqs
    for k, v in data.items():
        if not v:
            sys.exit(f"ERROR: empty section {k}")
    usage = resp.get("usage", {})
    print(f"OK. tokens in/out: {usage.get('input_tokens')}/{usage.get('output_tokens')}")
    return data

def build_faq_html(faqs):
    parts = ["<h2>Frequently asked questions</h2>"]
    for f in faqs:
        parts.append(f"<h3>{f['q']}</h3>\n<p>{f['a']}</p>")
    return "\n".join(parts)

def build_faq_jsonld(faqs):
    obj = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ],
    }
    # ensure_ascii=True guarantees em-dashes become \u2014 escapes (GitHub Pages rule)
    return json.dumps(obj, indent=2, ensure_ascii=True)

def build_article_jsonld(title, desc, url, today_iso):
    obj = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc, "url": url,
        "image": f"{SITE}/og-image.png", "inLanguage": "en-GB",
        "datePublished": today_iso, "dateModified": today_iso,
        "publisher": {"@type": "Organization", "name": "Interview Coach UK",
                      "url": f"{SITE}/",
                      "logo": {"@type": "ImageObject", "url": f"{SITE}/og-image.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    return json.dumps(obj, indent=2, ensure_ascii=True)

SAMPLE_DATA = {
    "title": "Sample Role Interview Questions UK (2026 Guide)",
    "meta_description": "Sample meta description for a dry run.",
    "quick_answer": "Sample quick answer.",
    "excerpt": "Sample excerpt.",
    "article_html": "<h2>What to expect</h2>\n<p>Sample body.</p>",
    "faqs": [{"q": "Sample question %d?" % i, "a": "Sample answer."} for i in range(1, 4)],
}

def build_page(tpl, keyword, slug, code, data, today):
    """Assemble the new guide's HTML from the template and the model's content."""
    today_h = today.strftime("%-d %B %Y")
    url = f"{SITE}/blog/{slug}/"
    title, desc = data["title"], data["meta_description"]
    # --- head: swap metadata ---
    page = tpl
    def sub1(pattern, repl_fn, s, flags=0):
        return re.sub(pattern, repl_fn, s, count=1, flags=flags)
    page = sub1(r"<title>.*?</title>", lambda m: f"<title>{title} — Interview Coach UK</title>", page, re.S)
    page = sub1(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1) + desc + m.group(2), page)
    page = sub1(r'(<meta name="keywords" content=").*?(">)', lambda m: m.group(1) + keyword + m.group(2), page)
    for prop in ("og:title", "twitter:title"):
        page = sub1(rf'(property="{prop}" content="|name="{prop}" content=").*?(")', lambda m: m.group(1) + title + m.group(2), page)
    for prop in ("og:description", "twitter:description"):
        page = sub1(rf'(property="{prop}" content="|name="{prop}" content=").*?(")', lambda m: m.group(1) + desc + m.group(2), page)
    for pat in (r'(property="og:url" content=").*?(")', r'(name="twitter:url" content=").*?(")',
                r'(<link rel="canonical" href=").*?(")'):
        page = sub1(pat, lambda m: m.group(1) + url + m.group(2), page)
    # replace first (Article) JSON-LD block
    article_ld = ('<script type="application/ld+json">\n'
                  + build_article_jsonld(title, desc, url, today.isoformat()) + "\n</script>")
    page = sub1(r'<script type="application/ld\+json">.*?</script>', lambda m: article_ld, page, re.S)

    # --- hero bar ---
    hero = re.search(r'<div class="hero-bar">.*?</div>\s*(?=<div|<main|<section)', page, re.S)
    if hero:
        new_hero = re.sub(r"<h1>.*?</h1>", lambda m: f"<h1>{title}</h1>", hero.group(0), count=1, flags=re.S)
        new_hero = re.sub(r'(<div class="meta">).*?(</div>)', lambda m: m.group(1) + f"Updated {today_h}" + m.group(2), new_hero, count=1, flags=re.S)
        page = page.replace(hero.group(0), new_hero, 1)

    # --- article body ---
    art = re.search(r"<article>(.*?)</article>", page, re.S)
    if not art:
        sys.exit("ERROR: <article> block not found in template")
    def extract_balanced_div(s, start_pat, last=False):
        ms = list(re.finditer(start_pat, s))
        if not ms:
            return ""
        m = ms[-1] if last else ms[0]
        i, depth = m.start(), 0
        for t in re.finditer(r"<div\b|</div>", s[m.start():]):
            depth += 1 if t.group(0).startswith("<div") else -1
            if depth == 0:
                return s[m.start(): m.start() + t.end()]
        return ""
    def personalise(banner):
        # personalise the banner line to this guide's keyword
        return re.sub(r"<p>.*?</p>",
                      lambda m: f"<p>Practise {keyword} in the Interview Coach UK app — free to download.</p>",
                      banner, count=1, flags=re.S)
    cta_top = personalise(extract_balanced_div(art.group(1), r'<div class="icuk-cta-banner">'))
    cta_end = personalise(extract_balanced_div(art.group(1), r'<div class="icuk-cta-banner">', last=True))
    if cta_top == cta_end:
        sys.exit("ERROR: template needs separate top and end CTA banners")
    new_article = "\n".join([
        f'<div class="quick-answer"><b>Quick answer:</b> {data["quick_answer"]}</div>',
        cta_top,
        data["article_html"],
        build_faq_html(data["faqs"]),
        '<script type="application/ld+json">\n' + build_faq_jsonld(data["faqs"]) + "\n</script>",
        cta_end,
    ])
    page = page.replace(art.group(0), "<article>\n" + new_article + "\n  </article>", 1)
    return retag(page, code)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--tag", default="Interview Tips")
    ap.add_argument("--code", help="page code for ct/utm tags (default: from slug)")
    ap.add_argument("--dry-run", action="store_true",
                    help="no API call and nothing written; print the tracking tags")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", a.slug):
        sys.exit("ERROR: slug must be lowercase letters, digits, hyphens only")
    code = a.code or default_code(a.slug)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", code) or len(code) > 30:
        sys.exit("ERROR: code must be lowercase letters, digits and single hyphens, max 30 chars")
    taken = existing_codes()
    if code in taken and taken[code] != a.slug:
        sys.exit(f"ERROR: page code '{code}' is already used by blog/{taken[code]}/ - pass --code")
    out_dir = os.path.join(REPO, "blog", a.slug)
    if os.path.exists(out_dir) and not a.dry_run:
        sys.exit(f"ERROR: {out_dir} already exists")

    tpl = open(TEMPLATE, encoding="utf-8").read()
    today = datetime.date.today()
    today_h = today.strftime("%-d %B %Y")
    url = f"{SITE}/blog/{a.slug}/"

    data = SAMPLE_DATA if a.dry_run else api_call(a.keyword)
    title = data["title"]
    page = build_page(tpl, a.keyword, a.slug, code, data, today)

    if a.dry_run:
        print(f"DRY RUN blog/{a.slug}/  page code: {code}  (nothing written)")
        for href in re.findall(r'href="([^"]*(?:[?&]ct=|utm_)[^"]*)"', page):
            print("  " + href.replace("&amp;", "&"))
        return

    os.makedirs(out_dir)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"WROTE blog/{a.slug}/index.html")

    # --- sitemap ---
    sm = open(SITEMAP, encoding="utf-8").read()
    if url not in sm:
        entry = (f"  <url>\n    <loc>{url}</loc>\n"
                 f"    <lastmod>{today.isoformat()}</lastmod>\n"
                 f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n")
        sm = sm.replace("</urlset>", entry + "</urlset>")
        open(SITEMAP, "w", encoding="utf-8").write(sm)
        print("UPDATED sitemap.xml")

    # --- blog index card (inserted at top of grid) ---
    bi = open(BLOG_INDEX, encoding="utf-8").read()
    card = (f'\n    <a href="/blog/{a.slug}/" class="blog-card">\n'
            f'      <div class="blog-tag">{a.tag}</div>\n'
            f'      <div class="blog-title">{title}</div>\n'
            f'      <div class="blog-date">{today_h}</div>\n'
            f'      <div class="blog-excerpt">{data["excerpt"]}</div>\n    </a>')
    m = re.search(r'<div class="blog-grid">', bi)
    if m and f"/blog/{a.slug}/" not in bi:
        bi = bi[:m.end()] + card + bi[m.end():]
        open(BLOG_INDEX, "w", encoding="utf-8").write(bi)
        print("UPDATED blog/index.html")

        # refresh search index so the new guide is searchable
    try:
        import subprocess
        subprocess.run(["python3", os.path.join(REPO, "tools", "build_search_index.py")], check=False)
        subprocess.run(["python3", os.path.join(REPO, "tools", "add_toc.py")], check=False)
        subprocess.run(["python3", os.path.join(REPO, "tools", "group_guides_page.py")], check=False)
    except Exception:
        pass

    print(f"""
REVIEW CHECKLIST
  1. open blog/{a.slug}/index.html   (visual check in browser)
  2. Skim content for factual errors (salaries, frameworks, band numbers)
  3. Then commit:
     cd {REPO} && git add -A && git commit -m "content: {a.slug} guide" && git push
  4. GSC: URL Inspection -> {url} -> Request Indexing
""")

if __name__ == "__main__":
    main()
