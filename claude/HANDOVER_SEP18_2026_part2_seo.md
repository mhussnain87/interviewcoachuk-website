# Interview Coach UK — Handover Addendum
## 18 September 2026, part two: SEO and visibility

Follows the 1.4.4 release handover. This half of the session moved to the
**website repo** — `~/dev/interviewcoachuk-website`.

---

## 1. WHAT SHIPPED

| Commit | What |
|---|---|
| `936cdb4` | NHS interview questions hub — full rewrite |
| (final) | STAR guide retitle + two new sections; duplicate h1 removed on examples page |

### NHS hub — /blog/nhs-interview-questions-uk/  (23KB -> 49KB)

- Title: `25 NHS Interview Questions With Model STAR Answers (2026)`
- Meta line: `Published 13 April 2026 · Updated 18 September 2026`
- 10 H2s / 35 H3s (was 6 / 12)
- Added `FAQPage` schema, 7 Q&A pairs — page had none, band pages did
- 13 outbound internal links: now a hub, not a competitor to the band pages
- Sitemap lastmod -> 2026-09-18, priority 0.8 -> 0.9
- Indexing requested; Rich Results Test passed
- Backup at `.backups/nhs-hub-rewrite-sep18/`

Sections chosen to absorb orphaned query clusters the page already ranked badly for:
scoring system (was pos 57), presentations (39-47), STAR (28), plus by-band and
by-role hub sections.

### STAR guide — /blog/star-method-interview-technique/  (39KB -> 41KB)

- Title cut 95 -> 55 chars: `STAR Method: How to Answer Interview Questions (UK 2026)`.
  The old one was truncated in results; likely cause of 0.2% CTR.
- New meta description, updated date line
- New H2s: STAR vs CAR/SOAR/STARL, and when STAR does not fit the question
- Removed a duplicate `<h1>` on /blog/star-method-examples-with-answers-uk/

### Bing

Already verified (97 clicks / 3.7K impressions). Sitemap submitted, 31 URLs pushed.
**Gotcha:** two properties exist, www and non-www. Canonicals, sitemap and GSC are all
non-www. Submitting non-www URLs to the www property is rejected. Remove the www one.

---

## 2. WHAT THE GSC DATA SAYS

Site-wide, 3 months: **1.86K clicks, 51.5K impressions, 3.6% CTR, position 12.4.**

**The site is an NHS site.** Bands 6, 7 and 5 are **1,628 of 1,860 clicks — 88% from
three pages**. Band 6 ranks **3.7** for "band 6 interview questions".

**Depth wins here, not links.** The failing hub had **30 inbound links** at 23KB and
ranked 32. Band 6 had **8** at 65KB and ranked 6.4. Most useful thing learned today.

Baseline to measure in 4 weeks:

| Page | Clicks | Impr | CTR | Pos |
|---|---|---|---|---|
| nhs-interview-questions-uk | 11 | 2,784 | 0.4% | 32.0 |
| star-method-examples-with-answers | 24 | 1,950 | 1.2% | 14.4 |
| star-method-interview-technique | 3 | 1,270 | 0.2% | 29.9 |
| questions-to-ask-at-the-end | 0 | 123 | 0% | 15.4 |

Untouched page-2 opportunities: `teaching-assistant` (2,494 impr, 16.6, 0.7%),
`healthcare-assistant` (978, 12.9, 1.3%), homepage (3,142, 17.8, 2.1%).

---

## 3. DEFERRED — STAR CANNIBALISATION

Two pages compete for one intent and both lose. Combined 3,220 impressions, 27 clicks.
Deferred twice, deliberately, to ~mid-October: three changes shipped today with no
results yet, and consolidating now would make attribution impossible.

Open questions when revisiting:
- **Direction?** Technique page is stronger (size, schema, 30 links) but examples page
  ranks better and earns 8x the clicks. Consolidating onto technique fights Google's
  apparent preference.
- **GitHub Pages cannot serve a true 301.** Canonical + meta refresh only. A botched
  job risks both pages.

---

## 4. STRATEGIC POSITION

**Broad head terms are not reachable yet.** "job interview help" / "coaching" are held
by Indeed, Reed, Prospects, National Careers Service, Totaljobs. Whole domain gets
51.5K impressions a quarter. A page targeting them lands ~position 40 and stays.

**Route to broad terms is through narrow ones.** Own NHS, then the next cluster. Each
adds authority; head terms become reachable by earning standing, not by targeting.

**Clinical focus confirmed over balanced.** Hub kept clinical because diffuseness was
the diagnosed problem. NHS admin (medical secretaries, ward clerks, booking, band 2-4,
business support) gets its own page later. No volume evidence gathered — check Bing
Keyword Research first.

---

## 5. NEXT SESSION

**Wait ~4 weeks before judging.** Then check the four pages above and decide:
1. Did depth-fixing work? If so repeat on `teaching-assistant` and other page-2 guides
2. Consolidate the STAR pages, and in which direction

Not dependent on waiting:
- **ASO keywords** — subtitle/keyword field should contain *questions to ask
  interviewer*. Needs a version submission; bundle with 1.4.5.
- **Author field in Article schema** — flagged non-critical, site-wide, small E-E-A-T
  gain. Scripted sweep across 29 guides.
- **"(2026)" in ~29 titles** — needs an annual sweep. Worth scripting now.
- Remove the duplicate www Bing property.
- **Urfan email — nearly two weeks overdue.** u.faqir@bradford.ac.uk from info@.
- `direct` campaign token; TikTok bio link; TikTok video #5; Offer Codes and Play promo
  codes; AppsFlyer vs Apple download comparison.

---

## 6. STANDING INSIGHTS ADDED

- **Depth beats internal links on this domain.** 30 links at 23KB lost to 8 links at
  65KB by 26 positions. Check size against a working sibling before theorising.
- **Check the whole listing before declaring something missing.** Claimed six pages were
  absent from the sitemap based on `head -40`; a full loop showed all present.
- **A page can be too young to judge.** Questions-to-ask looked broken at 0 clicks, but
  only began getting impressions in late August. Check the trend line first.
- **Titles over ~60 chars get truncated** and depress CTR. STAR was 95 chars at 0.2%.
  Worth auditing the other guides.
- **Google restricted FAQ rich results in 2023** to government and health authority
  sites. `FAQPage` schema still aids comprehension but will not render here. Don't chase.
- **GitHub Pages cannot serve 301s.** Any URL retirement needs canonical + meta refresh.
- **Bing rejects URLs not matching the exact verified property**, www included.
