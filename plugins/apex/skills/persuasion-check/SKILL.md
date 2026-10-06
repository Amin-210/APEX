---
name: "persuasion-check"
description: Audits finished product-page copy as ONE persuasion arc before anything is designed or built - the decision journey section by section, then 12 tests scored against the customer mind map (recognition, desire peaks, emotion/logic alternation, proof placement, objection coverage and order, price justification, CTA after every peak, identity close, first-use shock, honest limits, exit read), then a ranked fix list and any missing section written in full. Use WHENEVER product page copy is finished and before the design, accent or build steps - in page-engine as Phase 3c - and whenever the user asks why a page is not converting, whether the copy is persuasive, or what is weak about a page. Works for any store and market. Never invents new design - additions are written with the existing classes in the design system.
---

# Persuasion Check

A page can be good section by section and still fail as a whole. Every section here was written from the map, so nothing "fails" on its own - the gaps only appear when the page is read the way she reads it, top to bottom, once.

This skill reads the finished copy and scores it against the customer mind map. It runs BEFORE the accent decision, the design and the build.

## Inputs
The finished copy (all sections in page order), the customer mind map (layers, portrait, sub-personas, objection ranking with strengths, first-use shock), the price and the offer.
Missing the map → stop and ask for it. Without the ranking this is just an opinion about copy.

## Output, in this order

1. **The decision journey** - a table: section · what she sees · what she thinks after · which map line it serves · drop-off risk. Walk it as her, in order, once.
2. **The scorecard** - the 12 tests below, each PASS / WEAK / FAIL with the map line behind the verdict.
3. **The fix list** - ranked by impact, each fix naming the section it touches.
4. **Any missing section written in full** - copy AND markup, using only existing classes from `design-system.md`. Never invent a component, a colour or a layout.

## The 12 tests

| # | Test | Reads from the map | FAIL when |
|---|---|---|---|
| 1 | **Recognition first** | Layer 2 her words, layer 3 hidden habits | The page argues before she sees her own habit or her own phrase |
| 2 | **Two desire peaks** | Layer 6 deep desire | Layer 6 appears once (usually the hook) and never returns before the FAQ |
| 3 | **Emotion / logic alternation** | - | Three or more logic sections run back to back |
| 4 | **Proof before argument** | Sub-personas, Part E | Reviews sit after the benefit sections instead of before them |
| 5 | **Objection coverage** | Part E top 5 | Any top-5 objection is not answered anywhere on the page |
| 6 | **Objection order** | Part E strengths | A strength-5 objection is answered after a strength-3 one |
| 7 | **Price justification** | Layer 9 what the failed solution cost her | The page argues "better" but never answers "why this much" - no anchor, no per-use or per-month maths, no cost of the thing she keeps replacing |
| 8 | **CTA after every peak** | - | A peak (hook, reviews, emotional close) is followed by more than two sections with no way back to the form |
| 9 | **Identity close** | Layer 7 | The last emotional beat is a feature, a spec or logistics instead of who she becomes |
| 10 | **First-use shock** | Part E shock line | The thing that goes wrong or feels wrong on day one is not pre-answered anywhere |
| 11 | **Honest limits** | Layer 9, compliance | Nothing on the page says what the product does NOT do - everything reads perfect |
| 12 | **Exit read** | Part E fear 2-3 | The last three things she reads do not include the risk reversal (check before you pay, 7-day return) |

**Hard fails - the page does not proceed to design:** 5 objection coverage, 7 price justification, 8 CTA placement.
**Advisory - fix unless there is a reason not to:** the other nine. State the reason in one line when overriding.

## Scoring notes

- Quote the map line in every verdict: "objection 1, strength 5, answered in section 6" or "layer 6 appears once, in the hook". A verdict without a map line is an opinion, not a score.
- A section can serve two tests. A test is never passed by a section that only half serves it - mark WEAK and say what is missing.
- Count peaks by content, not by heading size: a peak is a moment she can picture herself in, not a benefit statement.
- If the map is mostly [HYPOTHESIS], say so at the top of the scorecard: the audit is only as true as the map, and 20-30 confirmation calls turn it real.

## Writing the fixes

Additions are written in the page's existing design language, from `design-system.md`. The three that come up most often:

**Price justification** - one `.xx-section`: an h3, one short paragraph doing the maths in her terms (what the failed solution costs her over a year, or cost per use), and an `.xx-results` tick list of 3-4 lines. No new component.

**Mid-page CTA** - one `.xx-closer` bar wrapping an anchor link back to the buy form, right after the peak it follows. Same style as the bottom closer, one line of text.

**Emotional close** - one `.xx-section` before the FAQ: an h3 naming the moment, three short lines from layers 4, 6 and 7, and one image placeholder. Ends on her, not on the product.

Rules for any addition: existing classes only, the page's accent only, no new fonts or colours, and it must be traceable to a map line. If a fix needs a component the design system does not have, say so and stop - do not invent one.

## What this skill does not do

It does not judge whether the map is right. If the map says her top fear is rust and it is really price, this audit will pass a page that argues rust beautifully. That is what the map's validation plan is for.
It does not rewrite sections that pass. It does not touch design, colour or build.
It does not judge HOW lines are written - that is **copy-voice-check**, which runs straight after it on the same copy.
