# Interview Coach UK — Handover Addendum
## 18–19 September 2026, part three: performance and the content playbook

Website repo only. The app repo was untouched after 1.4.4 went to both stores.

---

## 1. HOMEPAGE PERFORMANCE

| Metric | Before | After |
|---|---|---|
| Performance (mobile) | 82 (desktop) | **92** |
| Accessibility | 89 | **100** |
| LCP | 3.0 s | 2.6 s |
| CLS | 0.056 | **0.001** |
| Page weight | 2,952 KiB | **533 KiB** |

**The cause was one image.** `/assets/app-icon.png` was **1,503 KiB at 1024x1024,
displayed at 36x36**. Screenshots were 1320x2868 displayed at ~250x543.

Fixed with ImageMagick (`magick`, `cwebp` both installed):
- app-icon -> 144x144 (1,539 KB -> **13 KB**)
- screenshots -> 500x1086 (retina-correct for a 250-368px slot)
- Originals in `.backups/images-sep18/`

**Contrast failures** were all one variable: `--teal:#17A2B8` fails 4.5:1 both as
white-on-teal and teal-text-on-light. Added `--teal-deep:#0B6E7F` for `.nav-cta`,
`.price-cta`, `.section-tag`, `.trial-line`, `.badge`, `.blog-cta a`. Left `--teal`
where it sits on navy or on `--teal-soft`. Added the missing `<main>` landmark.

**Deliberately NOT done:** self-hosting Inter (~1,780 ms of render-block), WebP
(~338 KiB, needs `<picture>` everywhere). Diminishing returns at 533 KiB. **Core Web
Vitals shows 13/13 URLs green on field data** — the 2.6 s figure is emulated Moto G on
throttled 4G.

---

## 2. CONTENT SHIPPED

### Competency guide rewritten (`e3b66a2`)
`/blog/competency-based-interview-questions/` — **23KB -> 41KB**, 6 H2s -> 9, FAQPage
schema added, 12 outbound internal links.
- Title: `Competency Based Interview Questions: 30 Examples With Answers (2026)`
- New sections target orphaned clusters: **scoring** (~125 impressions across
  `competency scores` / `framework scoring` / `competencies scoring`, pos 24-29),
  **frameworks by sector** (hub links), **competency vs other formats** (catches
  `competency based interviews` at 74.9, `competency interview questions` at 66.8)
- Backup in `.backups/competency-rewrite-sep19/`

### NHS leadership — NEW PAGE
`/blog/nhs-leadership-interview-questions/` — cloned Band 7 as scaffold, replaced body
and every identity string (7 URLs, 5 titles).
- Title: `NHS Leadership Interview Questions: 20 Answers for Band 7+ (2026)`
- Targets `nhs leadership interview questions` (107 impr, 23.2) and
  `leadership interview questions nhs` (98, 18.6) — **~205 impressions, no page existed**
- Sections: what leadership interviews test, scoring, 20 questions, **expectations by
  band**, **ward manager / team leader** (catches `band 7 ward manager interview
  questions`, 62 impr), frameworks, presentations, mistakes, FAQ
- Wired in: sitemap (0.9), blog index card, inbound links from Band 6, Band 7, NHS hub
- **Salary content stripped** from the clone — wrong intent, maintenance liability

---

## 3. THE PLAYBOOK — FOUR APPLICATIONS, NONE VALIDATED

**The pattern:** page with real impressions ranking 30-65, ~23KB, six H2s, no FAQPage
schema. **The fix:** triple the content, add a section per orphaned query cluster, add
FAQ schema, add hub links, retitle to number + promise + year.

| Page | Before | Status |
|---|---|---|
| nhs-interview-questions-uk | 23KB, 6 H2, no FAQ, pos 32 | rewritten 18 Sep |
| competency-based-interview-questions | 23KB, 6 H2, no FAQ, pos 64 | rewritten 19 Sep |
| star-method-interview-technique | 39KB, had FAQ, pos 29.9 | light touch — title was 95 chars |

**Where it does NOT apply.** `teaching-assistant-interview-questions-uk` was next on
impressions (2,514, pos 16.5) and was **correctly rejected**: already **63KB with
FAQPage schema and a good title**. It is the page the playbook would have built. If
still stuck in October, the cause is domain authority vs Indeed/Reed/TES, not on-page.
**Do not rewrite it.**

`behavioural-interview-questions-uk` checked for cannibalisation with competency — clean.
113 impressions, 6 queries, all "behaviour*" spellings. Leave it.

---

## 4. BASELINE FOR MID-OCTOBER

| Page | Clicks | Impr | CTR | Pos |
|---|---|---|---|---|
| nhs-interview-questions-uk | 11 | 2,784 | 0.4% | 32.0 |
| competency-based-interview-questions | 0 | ~580 | 0% | 63.9 |
| star-method-interview-technique | 3 | 1,270 | 0.2% | 29.9 |
| star-method-examples-with-answers | 24 | 1,950 | 1.2% | 14.4 |
| questions-to-ask-at-the-end | 0 | 123 | 0% | 15.4 |
| teaching-assistant (control) | 16 | 2,514 | 0.6% | 16.5 |
| nhs-leadership-interview-questions | — | new | — | — |

Site-wide: **1.88K clicks, 52.1K impressions, 3.6% CTR, position 12.2.**

**Attribution warning:** four content changes plus a major performance change in 24
hours. If things move we won't know which lever did it. Teaching assistant is the
closest thing to a control.

---

## 5. REMAINING GAPS (0 clicks, real impressions)

| Query | Impressions | Position |
|---|---|---|
| interview coaching | 308 | 38.4 |
| nhs interview coaching | 215 | 29.0 |
| interview techniques gloucestershire | 136 | 46.8 |
| nhs presentation interview | 95 | 47.6 |
| nhs star interview questions | 86 | 28.2 |
| nhs interview scoring system | 83 | 39.5 |
| interview prep price uk | 74 | 6.4 |
| nhs interview advice | 74 | 42.2 |

The NHS hub rewrite added scoring and presentation sections, so several may resolve
without further work — check before building anything new.

**Parked:** STAR consolidation (deferred twice, revisit mid-Oct with evidence); NHS admin
page (no volume evidence — check Bing Keyword Research first).

---

## 6. STANDING INSIGHTS ADDED

- **Check image dimensions first on a slow page.** One 1.5MB image at 36px was over half
  the payload. `magick identify` on every asset takes seconds.
- **One CSS variable can cause every contrast failure.** Fix once with a second variable.
- **Don't apply the playbook without checking the page.** Teaching assistant was next on
  impressions and needed nothing. Pull size, H2 count, schema and title first.
- **Cloning a page as scaffold works**, but audit for content that doesn't belong — the
  Band 7 clone carried salary figures into a leadership page.
- **Schema can live inside `<article>`.** Band 7's FAQPage block did, so a body splice
  silently removed it. Check where schema sits before writing a replace pattern.
- **A new page needs four things or it's an orphan:** the file, a sitemap entry, a blog
  index card, inbound links from related pages.
- **Anchors differ between near-identical pages.** Band 6:
  `how-to-structure-your-answers-using-star`. Band 7:
  `how-to-structure-every-answer-using-star`. Grep the actual ids.
- Lab PageSpeed and field Core Web Vitals are different things. 13/13 green in GSC
  matters; a 2.6 s emulated-Moto-G LCP mostly doesn't.
