#!/usr/bin/env python3
"""
Interview Coach UK — weekly social kit generator.

Usage (from website repo root, ANTHROPIC_API_KEY exported):
  python3 tools/social_pack.py                 # uses the newest guide
  python3 tools/social_pack.py --slug nhs-band-6-interview-questions

Writes social-packs/PACK_<slug>_<date>.txt — ready-to-paste posts.
Nothing is posted anywhere automatically.
"""
import argparse, datetime, glob, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "claude-sonnet-4-6"
SITE = "https://interviewcoachuk.com"
APP_IOS = "https://apps.apple.com/app/id6754808754"
APP_AND = "https://play.google.com/store/apps/details?id=com.interviewcoachuk"

PROMPT = """You write social content for Interview Coach UK, a solo-built UK interview-prep app (315 expert STAR answers across 9 UK sectors, AI answer coaching, mock interviews, and a feature that turns any pasted job advert into 12 tailored questions; 3-day free Premium trial; iOS + Android).

Source guide just published:
TITLE: {title}
URL: {url}
QUICK ANSWER: {quick}
SAMPLE QUESTIONS FROM THE GUIDE:
{questions}

Voice: practical, warm, first-person solo-founder, UK English, zero hype-words (no "game-changer", "unlock", emojis fine but sparing). Never invent statistics.

Respond with EXACTLY these sections, each starting with its marker line, no other text:

===LINKEDIN_1===
Feature-angle post (120-180 words) using this guide's topic as the hook. End with "Full guide + the app link in the comments." Do NOT include URLs in the body.

===LINKEDIN_2===
Pure-value post (100-160 words): one genuinely useful interview tip drawn from the guide's questions, written to be useful even if the reader never clicks anything. Soft mention of the guide at the end.

===X_1===
Tweet under 260 chars: strongest single question from the guide + one-line advice on answering it.

===X_2===
Tweet under 260 chars: different angle (mistake to avoid, or STAR tip).

===X_3===
Tweet under 260 chars: light/relatable observation about interview prep for this role.

===REDDIT_1===
Reply template (80-140 words) for someone who posts "I have a {role} interview next week, any tips?" — genuinely helpful first (2-3 concrete tips referencing what panels ask), app mentioned only in a final low-key line as "I built a small app that might help". No links (subreddit rules vary).

===REDDIT_2===
Reply template (80-140 words) for someone anxious about competency/STAR questions in this field — reassuring, practical structure advice, same low-key single-line mention at the end.

===FACEBOOK===
Version for UK job-seeker Facebook groups (80-130 words): friendlier, question-led opening, guide link on its own final line: {url}

===END===
"""

def newest_slug():
    posts = glob.glob(os.path.join(REPO, "blog", "*", "index.html"))
    posts = [p for p in posts if os.path.basename(os.path.dirname(p)) != "blog"]
    if not posts:
        sys.exit("ERROR: no blog posts found")
    latest = max(posts, key=os.path.getmtime)
    return os.path.basename(os.path.dirname(latest))

def extract(slug):
    p = os.path.join(REPO, "blog", slug, "index.html")
    if not os.path.exists(p):
        sys.exit(f"ERROR: blog/{slug}/index.html not found")
    h = open(p, encoding="utf-8").read()
    title = re.search(r"<h1>(.*?)</h1>", h, re.S)
    quick = re.search(r'Quick answer:</b>\s*(.*?)</div>', h, re.S)
    qs = re.findall(r"<h3[^>]*>\s*\d+\.\s*(.*?)</h3>", h, re.S)[:6]
    clean = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()
    return {
        "title": clean(title.group(1) if title else slug),
        "quick": clean(quick.group(1) if quick else ""),
        "questions": "\n".join(f"- {clean(q)}" for q in qs) or "- (none extracted)",
        "url": f"{SITE}/blog/{slug}/",
        "role": re.sub(r"\s*(Interview Questions|Interview|Questions).*$", "", clean(title.group(1) if title else slug), flags=re.I).strip() or "this role",
    }

def api_call(prompt):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=...")
    body = json.dumps({"model": MODEL, "max_tokens": 3000,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    text = "".join(b.get("text", "") for b in resp.get("content", []))
    usage = resp.get("usage", {})
    print(f"OK. tokens in/out: {usage.get('input_tokens')}/{usage.get('output_tokens')}")
    return text

def section(text, name, nxt):
    m = re.search(rf"==={name}===\s*(.*?)\s*==={nxt}===", text, re.S)
    if not m:
        sys.exit(f"ERROR: model response missing section {name}")
    return m.group(1).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    a = ap.parse_args()
    slug = a.slug or newest_slug()
    meta = extract(slug)
    print(f"Generating social pack for: {meta['title']}")
    text = api_call(PROMPT.format(**meta))

    names = ["LINKEDIN_1", "LINKEDIN_2", "X_1", "X_2", "X_3",
             "REDDIT_1", "REDDIT_2", "FACEBOOK", "END"]
    parts = {n: section(text, n, names[i+1]) for i, n in enumerate(names[:-1])}

    today = datetime.date.today().isoformat()
    out_dir = os.path.join(REPO, "social-packs")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"PACK_{slug}_{today}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"""SOCIAL PACK — {meta['title']}
Generated {today} · guide: {meta['url']}
Links for LinkedIn FIRST COMMENT (never the post body):
  App Store: {APP_IOS}
  Google Play: {APP_AND}
  Guide: {meta['url']}

════ LINKEDIN POST 1 (schedule Mon/Tue 8:30am) ════
{parts['LINKEDIN_1']}

════ LINKEDIN POST 2 (schedule Thu 8:30am) ════
{parts['LINKEDIN_2']}

════ X / TWITTER (spread across the week) ════
1. {parts['X_1']}

2. {parts['X_2']}

3. {parts['X_3']}

════ REDDIT REPLY TEMPLATE A — "interview next week, tips?" ════
(adapt to the thread — never paste verbatim into multiple threads)
{parts['REDDIT_1']}

════ REDDIT REPLY TEMPLATE B — anxious about STAR/competency ════
{parts['REDDIT_2']}

════ FACEBOOK GROUPS ════
{parts['FACEBOOK']}
""")
    print(f"WROTE social-packs/PACK_{slug}_{today}.txt")
    print("Review, then: open the file, paste into schedulers. Nothing auto-posts.")

if __name__ == "__main__":
    main()
