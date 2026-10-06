# Phase 3b — The 5 reviews: frames, copy and design
The Social Proof section sits directly after the Pain Point section. It is 5 framed cards, not 12 pre-filled ones.

The section is in every template in the standard slider form, but OFF by default: the checkbox "Show reviews section" (`show_reviews`, default false) wraps it, and the owner ticks it when ready. When on with no reviews yet → the 5 frame cards show as fallback, and the collection kit at the bottom of this file brings the real words and photos that replace them. Review text itself comes from real customers only.

## Making real reviews sound local (not generic)
Real words often arrive flat over WhatsApp — "it is nice, thank you". The job is to bring them back to how she actually speaks, without inventing anything. Take the places, words, moments and money from the market profile; the examples below come from the example market (Kenya):

- **Her place:** the estate, the town, the matatu, the shop she passed on the way. "Kasarani", "Ngong Road", not "Kenya".
- **Her words:** imeziba, sina space, inanuka, poa, iko fiti, harusi, fundi, bob. Keep the Swahili or Sheng she used; never translate it into neat English.
- **Her moment:** Sunday after lunch, month end, before visitors, after supper, during the rains.
- **Her money:** shillings and the real number she paid or saved.
- **Her people:** her mum-in-law, her landlord, the neighbour, her kids — the person whose reaction mattered.
- **Light editing only:** fix spelling, cut repetition, order her own sentences into the card's frame, then send the final version back for her OK. If a line is not hers, it does not go in.

## Each card ships with a 9-row frame

| Row | What goes in it |
|---|---|
| **Purpose** | The one objection this card kills, in her words, with its rank |
| **Mirror** | Who she is: age band, situation, town, which persona or sub-persona |
| **Map lines** | The layers it draws on, e.g. "2 her phrase · 8 fear 1 · 10 who noticed" |
| **Emotional arc** | The path the reader travels, e.g. doubt → recognition → relief → pride |
| **Sentence frame** | 4-6 numbered parts to fill with her real words |
| **Must contain** | The concrete detail that makes it believable: a number, a time span, a place, what someone said |
| **Must avoid** | Claims the page does not make, and anything the product cannot keep |
| **Photo brief** | Written for THIS card: what is in frame · setting · angle and distance · light · what must be visible because the text claims it · what must NOT be in frame · why it matches her words |
| **Ask for it with** | The one WhatsApp question that pulls this exact story out of a real customer |

## The fixed roles
1. **The skeptic** (first) — kills the biggest "will it be what the page says" fear
2. **The before / after transformation** — the change in her life, not in the product (see below)
3. **The time test** (4 stars, one honest gripe) — kills the durability or results-over-time fear
4. **The fit / my-situation card** — kills the compatibility fear, from a sub-persona
5. **The second audience** — gift buyer, landlord, business, whoever else buys it
6. **The emotional one** (last) — answers "is it worth it" with feeling, ends on her, not on the product

With six roles and a five-card slider, the map drops whichever card answers the weakest objection for that product.

## The before / after card — the map decides its shape
This is the strongest card for decision-making, because it lets her run her own future in her head. The customer map decides HOW it is built, product by product:

| What the map says | The shape the card takes |
|---|---|
| **PROBLEM product, visible result** (drain, cleaning, repair) | Hard before/after: the state of the thing before → what she did → the state after, with a time ("30 minutes", "the same evening"). Photo: the same spot, same angle, before and after |
| **PROBLEM product, invisible or slow result** (health, comfort, sleep) | Time-based: week 1 → week 3 → now, in her words. No claim she did not make. Photo: the thing she can show (the bottle on the shelf, her routine), never a body result |
| **DESIRE product** (watch, decor, gadget) | Situation before → situation after: the bare wrist and the borrowed one → the wedding photo. The "after" is a moment, not a measurement |
| **MIX / chore product** (rack, organiser, tool) | Routine before → routine after: what her evening looked like → what it looks like now. Photo: the counter, the room, the corner — same view, both states |
| **Sophistication stage 4-5** (she has tried everything) | Lead with the failed solution: what she used before this, what it cost her, what changed |

Whatever the shape, the card must carry: the BEFORE in her own words (the habit or the moment, not an adjective), one concrete marker of time, the AFTER as something she can see or do, and a closing line about her rather than the product. The map's layer 3 (hidden habits) supplies the before; layer 6 (deep desire) supplies the after.

## The sentence shape inside a card (NorthPower method)
1. Skeptic opener in her doubt words → 2. the private problem or hidden habit → 3. a concrete detail (time, place, number) → 4. the result plus one surprise → 5. someone noticed and what they said → 6. an identity close about her, not the product.
Minimum parts: 1, 2, 4, 6. A short real review beats a padded one.

## Design of the section (store standard slider, always on)
- Title "What our customers say" + an order button in the accent-dark colour ("I want to order this ↑", back to the order form).
- Band in the accent-soft colour: up to 4 overlapping round avatars (only uploaded real customer photos show; no avatar row when none is uploaded), the count line (e.g. "110+ Verified Reviews") and ★★★★★ + the rating line (e.g. "Excellent, 4.7 out of 5 stars"). Count and rating lines are ALWAYS shown (never inside an `if`): editable text settings with the placeholder defaults "[count]+ Verified Reviews" and "Excellent, [avg] out of 5 stars", rendered with `| default:` as in the master template; the owner replaces [count] and [avg] with the store's real numbers in the theme editor.
- Swipeable cards, about 85% wide so the next card peeks in: her own phone photo on top (4:5) only when one is uploaded, never an empty placeholder box, 💬 first name + town, stars, the review text.
- Round arrow buttons centred under the cards: previous in grey, next in black.
- Off by default (checkbox "Show reviews section"). When on: with no review blocks, the 5 frame cards show; each real review block replaces them.
- Four 5-star, one 4-star.

## Coverage check (always close with this)
A table of the top objections against the card that covers each, then one line: personas covered, moments covered, star spread.

## Collection kit (day 7 after delivery, WhatsApp)
What was the occasion or problem · what you tried before · how long until it worked · what almost stopped you ordering · a photo as described in that card's photo brief (no face needed) · may we use your first name and town?
