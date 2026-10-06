# Copywriting Framework (MAIN) — Ayoub Product Page Template

This is the **primary copywriting framework** for every product page, in any market.
The page section order IS this framework. Do not invent extra sections and do
not drop framework sections. The only non-framework element we keep is the **5 framed review cards** (real customers, 5 schema blocks), which serve as the Social Proof section. The **Order Journey Badge** is a separate section placed ABOVE the product image gallery; the **three info accordions** are first in the description body.

REMOVED from the framework (do not add them back): the **Q2 Dream Outcomes** bullet list and the **Q3 Differentiators** cards. COD, free delivery and guarantee are already carried by the Order Journey Badge, the info accordions, and the Final CTA.

**Every line is written from the customer mind map** (`customer-mind-map-brief.md`), never from the supplier text. Each section moves the visitor through a conversion stage:

| Section | Conversion stage |
|---|---|
| Above the Fold — Q1 + image copy | Awareness + Interest |
| Pain Point headline | Desire |
| Social Proof (5 framed reviews) | Believability |
| Benefits Deep Dive | Desire + Trust |
| Us vs Others | Believability |
| Final CTA + Guarantee | Action |
| FAQ | Objection removal |

---

## ABOVE THE FOLD

### Q1 — What does it do? (Value Proposition)
A punchy **headline** plus a one-line **sub-headline** that instantly says what
the product is and the main benefit. This is the Hook. Hero image sits under it.

### Product Images Section Copy
Because visitors look at images before text, supply a short caption for each:
- Hero image
- In-use / lifestyle image
- Feature close-up
- Results or before/after (if applicable)
These captions map to the `{{IMAGE_*}}` placeholders.

---

## BELOW THE FOLD

### 1. Pain Point + Desire Headline
A headline that puts the customer back in the problem, agitates it briefly, then
turns toward the outcome. Goal: reignite desire. Emoji + agitation + image.

### 2. Social Proof Section  ← THE 5 FRAMED REVIEWS (directly after the pain point)
Five real-customer cards, each built on a frame (purpose, mirror, map lines, emotional arc, sentence frame, must contain, must avoid, photo brief, the question that pulls it out) — see `review-frames.md`. Roles: the skeptic · the before/after transformation (shape decided by the map) · the time test (4 stars, one honest gripe) · the fit / my-situation card · the second audience · the emotional one last. Six roles, five cards. Photo-first cards, first name + town, four 5-star and one 4-star. Real customers, in their own words - her neighbourhood, her local words, her moment, her money (market profile). The section is in every template in the standard slider form, OFF by default (`show_reviews`); when it is on with no reviews yet, the 5 frame cards show and the collection kit brings the real ones.

### 3. Benefits Deep Dive
Re-explain the **top 3 benefits** in detail: each a short paragraph + its own
image. (This replaces the old open-ended "5 to 8 feature sections" — cap at 3.)

### 4. Us vs Other Brands — Comparison
A short intro line + a comparison table with **5 to 6 rows** that make our
product the obvious choice (us = green check, others = red X). Goal: believability.

### 5. Final Call to Action + Guarantee
An action-oriented headline, a guarantee statement (the store's real policy, word for word from the store profile), an
optional **honest** urgency/scarcity line (only if real), and the COD closer
reassurance (the store profile's COD closer line).

### 6. FAQ Section
**5 to 6** Q&A written from real customer **objections**: how it works, safety,
results timeline, delivery, returns/COD. Objection removal, not generic filler.

---

## Guardrails that sit ABOVE this framework (never overridden)
- All compliance rules in `compliance-rules.md` still apply.
- Payment exactly as the store profile says; never a method from its `payment never` line. No em-dashes or double-hyphens.
- No invented review counts, ratings, "10,000+ customers", fake urgency, or
  fake authority. Social proof and scarcity must be real.
- FDA-safe verbs for anything ingestible or skincare. Disclaimer footer where needed.

## Optional additions to the prompt (for stronger copy)
- Add the target audience.
- Paste 1 to 2 competitor ad headlines to position against.
- For beauty: prioritise before/after framing and UGC-style proof.
- For high-ticket: add more objection handling in the pain point section and the FAQ.
