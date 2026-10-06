---
name: "page-engine"
description: The build engine for COD product pages - turns an approved customer mind map into Shopify Liquid for a cash-on-delivery store in any market (store facts from a store profile), on the Ayoub framework, with 5 psychologically framed review cards after the pain point and infografic-style image prompts, plus the launch manifest (slug-product.json) and the APEX Google Drive hand-off. Use whenever the user writes "PageEngine for row N", "PageEngine for" plus a product name (a row of the APEX Products sheet) or "PageEngine for _inbox/...", and whenever the user pastes supplier product info, uploads product images and asks to build or design a page, says "build a Shopify page", "create a product description", "set up a new product", or asks to turn a product into a store page. Also for image prompts driven by the map, compliance for weight-loss, medical or supplement copy, badge and accent colours and bundle pricing. Triggers even without the words "skill" or "Shopify" - supplier copy or product images with intent to sell is the signal.
---

> **APEX, step 1 of 4.** PageEngine is the first step of APEX, the whole system from supplier text to a finished live page: 1 PageEngine → 2 Product setup (`new-product.ps1`) → 3 Claude Code design → 4 Image Factory (`run-factory.ps1`). Overview: `references/apex.md`.


# Page Engine

Turns raw supplier product info into a fully-built Shopify Liquid product description section optimized for the store's own market (its store profile and market profile), written on the **Ayoub conversion copywriting framework**.

## What this skill produces

TWO `.liquid` section files:
- `journey-badge-template.liquid` — the Order Journey Badge, a SEPARATE section placed at the VERY TOP of the product page, ABOVE the product image gallery. Reusable across all products (colors are section settings).
- the product description section, which:
- Drops into the theme as `sections/product-description-<slug>.liquid`
- Includes scoped CSS, all body sections in the copywriting-framework order, the 5-card review slider (off by default), an objection-based FAQ, and COD copy taken from the store profile
- Uses image placeholders the user replaces with Shopify CDN URLs

Plus, on request: Nano Banana / Gemini image prompts using the Feature -> Emotion framework.

## THE COPYWRITING FRAMEWORK IS THE STRUCTURE

The page section order **is** the Ayoub framework in `references/copywriting-framework.md`. Read that file first — it is the main spec. Do not add sections outside the framework and do not drop framework sections. The only non-framework element kept is **the reviews form** (the 5-card review slider), which serves as the Social Proof section.

COD store standards kept: the **Order Journey Badge** is a SEPARATE section placed ABOVE the product image gallery (see journey-badge-template.liquid), and the **three info accordions** (What's in the Box, Delivery Information, How To Order) are FIRST inside the description body, directly under the buy button, before the Q1 hook. Sections that ARE removed (not in the framework): the "Who It's For" persona list, the standalone spec table, and the trust trio. Also removed from the framework: the **Q2 Dream Outcomes** bullet list and the **Q3 Differentiators** card grid (their COD value is already carried by the Order Journey Badge, the info accordions, and the Final CTA).

## The 9-phase workflow

Follow in order. Do not skip phases.

### Phase 0 — No Shopify setup before the build
Do not ask the user to create the product first. Fixed order: (1) PageEngine builds the page; (2) `.\new-product.ps1 <slug>` creates the product and its unique template from the launch manifest this build delivers; (3) Claude Code in VS Code designs the page in that template (the setup writes its prompt); (4) the Image Factory. See `references/pre-build-setup.md`.

### Phase 1 — Input gathering
**Sheet mode (the default input).** When the user writes `PageEngine for row <n>` or `PageEngine for <product name>`, the input is that product's row in the Google Sheet **APEX Products**: follow `references/sheet-mode.md` exactly (read the row with the Google Sheets connector, the checks, `photos_row:` in READY.txt, then BUILD → DONE and the title cell coloured green).

**Drive intake (the backup input).** When the user writes `PageEngine for _inbox/<name>` (or names a folder in `APEX/_inbox/`), read the input from Google Drive with the Google Drive connector:
1. Find `APEX` in My Drive, then `_inbox` inside it, then the folder `<name>` inside that (`search_files` with `title = '...'` and `parentId = '<id>'` and the folder mimeType). Missing → say so in one line and ask for the exact name.
2. List the folder (`search_files`: `parentId = '<folder id>'`), then list `photos/` and `extra/` the same way.
3. Read `input.txt` with `read_file_content` (a Google Doc named `input` works the same way). Its first lines carry `price:`, `compare price:` and `store:` (the store key); everything below is the supplier text. A missing price or compare price → ask once before building, as always.
4. **Never download the photos from Drive** (`download_file_content` returns the whole file as text: one normal photo costs hundreds of thousands of characters). List their names only. The photos you look at are the 1-2 the user attaches in the chat. None attached → build from the text, say in one line that you did not see the product, and write the REFERENCE line of the image prompts from the supplier text.
5. `photos/` = clean product photos: the Image Factory uses these on the PC (the watcher copies them). `extra/` = collages, infographics, before/after: context for you only, never for image generation.
6. Remember `<name>`: READY.txt gets the line `inbox: <name>` (hand-off, step 4).
Without an intake folder (supplier text pasted in the chat) the old way still works: the user drops the photos into `Desktop\apex-inbox` on the PC.

**Store profile (always, every input).** Read the store's profile, `APEX/_stores/<store>.md` (or the one pasted in the chat), and follow `references/store-profile.md`: brand name, brand colour, market, language, currency, payment, guarantee, delivery line, order steps and closer come from it, word for word. No profile → ask for it once (template in that file) before Phase 2. Then open the market profile it names.

Read the supplier text and the images. Cross-check them. If they contradict (e.g. supplier says "no battery" but images show a charging port), flag it before proceeding.

### Phase 2 — THE CUSTOMER MIND MAP — the source of all copy
Do NOT write personas or angles here from the supplier text. Run **customer-mind-map** and use its output as the single source for every line on the page.

Produce, in this order:
1. **Step 0** — problem / desire / MIX product, and the sophistication stage.
2. **The 10 layers** — who · the problem in her words · hidden habits · painful moments · surface desire · deep desire · identity · fears and objections (ranked) · failed solutions · who she wants to impress. Every line tagged [VOC] (a real customer said it), [RESEARCH] (found in reviews/forums) or [HYPOTHESIS].
3. **Portrait** — one named person, her day with the problem, her inner monologue in her own words, plus 2-3 sub-personas.
4. **Language bank** — her exact words for the problem, the desire, the fear, the moments, plus the words to AVOID.
5. **Objection ranking** — top 5 with strength 1-5, and the first-use shock to pre-answer.
6. **Angles** — ALL viable angles with what each is built on.
7. **Compliance flags** — claims to refuse or rewrite, before anything is built.

Then map the output onto the framework slots:
- Q1 headline + sub-headline ← deep desire (6) + the moment (4)
- Pain point + desire turn ← problem in her words (2) + hidden habit (3) + painful moment (4)
- The 5 reviews ← objection ranking + sub-personas (see Phase 3b)
- Benefits deep dive (TOP 3) ← surface desire (5) answered against failed solutions (9)
- Us vs Others rows ← failed solutions (9), category names only, never a brand
- Final CTA ← identity (7) + the real guarantee
- FAQ (5-6) ← objections 1-6 in her words

Rule: **a line that cannot be traced to a map line does not go on the page.** If the map is missing something the framework needs, ask the user or mark it [HYPOTHESIS] and flag it for validation.

### Phase 3 — Angle selection (the MAP decides, no confirmation needed)
The customer mind map from Phase 2 chooses the angles. Do not stop to ask. Pick the page angle and each section angle from the map, then state the choice and the map line behind it in one short table, and keep building.

How the map decides:
- **Page angle** — the objection or desire ranked strongest in Part E / layer 6. Whatever blocks the most buyers, or pulls hardest, wins.
- **Q1 hook** — deep desire (6) + the moment (4).
- **Pain point** — the top-ranked objection or the hidden habit (3) that stings most.
- **Benefits 1-3** — the three surface desires (5) that answer the next three objections in rank order.
- **Us vs Others** — the failed solution (9) she has actually paid for, never a named brand and never a solution she has never tried.
- **Final CTA** — identity (7) plus the real guarantee.

Angle menu to draw from: villain / root-cause, feeling (shame, fear, relief, pride), symptom stack, day-in-the-life, benefit ladder, value, social proof, safety.

Still get from the user the two prices, because they are not in the map: **the selling price and the compare-at price**. The user always gives both, together with the supplier text; if one is missing, ask for it (one question) before building, and never invent or calculate a compare-at price. The product name is always our own (never the supplier's). Everything else proceeds.

### Phase 3b — The 5 reviews (frames, after the Pain Point section)
The Social Proof section is now **5 psychologically framed review cards**, not 12 pre-filled ones. Before building, produce the review frames document: one table per card with **Purpose · Mirror · Map lines · Emotional arc · Sentence frame · Must contain · Must avoid · Photo brief · Ask for it with**, then a coverage check table.

Fixed roles: 1 the skeptic · 2 the before/after transformation (the map decides its shape - hard before/after, time-based, situation-based or routine-based, depending on product type and sophistication) · 3 the time test (4 stars, one honest gripe) · 4 the fit / my-situation card from a sub-persona · 5 the second audience (gift buyer, landlord, business) · 6 the emotional one, last, ending on her and not on the product. Six roles, five cards - the map drops the one answering the weakest objection.

**The review section is in EVERY template, in the store's standard 5-card slider form, but OFF by default** (see Phase 5 and `templates/master-template.liquid`): the whole review section is wrapped in `{%- if section.settings.show_reviews -%} ... {%- endif -%}` (checkbox "Show reviews section", default false); the owner ticks it in the theme editor when the store is ready to show reviews. When it is on and no real reviews exist yet, the 5 frame cards show; the collection kit brings the real words and photos that replace them in the theme editor. Reviews themselves come from real customers only. Then bring their words back to how they actually speak - her neighbourhood, her local words, her moment, her money, her people (from the market profile) - with light editing only (see `review-frames.md`). Photos are optional: a card shows the customer's photo only when one is uploaded, never an empty box. When there is a photo, it must prove the sentence: a card about the clasp after a month needs the clasp in focus, not a smiling face.

### Phase 3c — Persuasion check (before any design decision)
Run **persuasion-check** on the finished copy, as one arc, before the accent and the build. It returns the decision journey, a 12-test scorecard against the map, a ranked fix list, and any missing section written in full.

Hard fails block the build: **objection coverage**, **price justification**, **CTA after every peak**. The other nine are advisory - fix them or state the reason in one line.

Sections added by the audit are written with the existing classes in `references/design-system.md` (usually a `.xx-section` price-justification block, a `.xx-closer` mid-page CTA, or a `.xx-section` emotional close before the FAQ). No new components, no new colours.

### Phase 3d — Copy voice check (still before any design decision)
Run **copy-voice-check** on the copy that came out of 3c. persuasion-check asks whether the beats exist; this asks whether the words land: second person, her exact words, a scene instead of a list in the pain point, headings that carry a person or a consequence, sensory detail, the hook as a moment, one idea per sentence, specificity, rhythm, the reframe leading its block, repetition, and the last line of every section.

It returns the weak lines quoted with rewrites and the rewritten sections in full. Same sections, same order, same design classes - words only. Claims never get stronger in a rewrite, and customer reviews are never rewritten for voice.

### Phase 4 — Accent colour decision (one colour for the page AND the images)
Pick ONE accent per product, from the product's own palette, using `references/badge-colors.md`. It must fit the product, pop against the scenes the images will use, and stay legible both as a small tick circle on white and as a caption line over a photo.

State it once as a single line — `accent: terracotta #D2703A` — and use that exact hex in all three places:
- the page CSS tokens (`--xx-accent`, plus a darker and a soft tint of it),
- the Order Journey Badge circles,
- every image prompt: the infografic overlay devices and the payoff caption line (`references/infografic-style.md` and `design-system.md`).

Checkmark ticks stay green even when the accent is not. The store's brand colour (store profile) in the brand bar, promise row and brand section never changes with the product.

### Phase 5 — Building the .liquid file
The **Order Journey Badge is a SEPARATE section** built from `templates/journey-badge-template.liquid` and placed ABOVE the product image gallery (not inside the description). The description section is built from `templates/master-template.liquid`. Replace the tokens. **Locked description section order** (top to bottom):
1. `{% comment %}` metadata block
2. Scoped `<style>` with a unique 2-letter class prefix and the accent variables
3. Wrapper `<div class="xx-page">`
4. **Three info accordions** — What's in the Box, Delivery Information, How To Order — FIRST in the description, directly under the buy button, before the hook
5. **ABOVE THE FOLD**
   - Q1 Value Proposition — headline (H2) + sub-headline + hero image
6. **BELOW THE FOLD**
   - 1. Pain Point + Desire — agitation (emoji) + desire turn + image
   - 2. Social Proof — **the 5-card review slider, in every template but OFF by default** (the whole review section is wrapped in `{%- if section.settings.show_reviews -%} ... {%- endif -%}` (checkbox "Show reviews section", default false)): title "What our customers say" + order button (accent-dark) → band in the accent-soft colour with 4 overlapping round avatars, the count line and the ★★★★★ + rating line → swipeable cards (85% wide, next card peeking), each with the customer's photo on top ONLY when one is uploaded (no placeholder box otherwise), 💬 first name + town, stars, the text → round prev (grey) / next (black) arrow buttons underneath. Cards come from the review blocks; with no blocks, the 5 frame cards render as fallback. Band (when the section is on): the count line and the ★★★★★ rating line are ALWAYS shown (never inside their own `if`), each a text setting with a placeholder default: `reviews_count_line` = "[count]+ Verified Reviews", `reviews_rating_line` = "Excellent, [avg] out of 5 stars", rendered with `| default:` exactly as in `templates/master-template.liquid`; the owner edits them in the theme editor and puts the store's real numbers in place of [count] and [avg]. Avatars are image settings: only uploaded avatars show, no grey icons, and no avatar row at all when none is uploaded. One 4-star card
   - 3. Benefits Deep Dive — TOP 3 benefits, each H3 + paragraph + image
   - 4. Us vs Others — intro line + comparison table (5 to 6 rows)
   - 5. Final CTA + Guarantee — action headline + the store's REAL guarantee (store profile, word for word) + honest urgency (if real) + COD closer line
   - 6. FAQ — 5 to 6 objection-based accordions
7. `{% schema %}` with **5 review blocks as presets, each holding its frame** (purpose + sentence frame), the same frames as the fallback cards, never invented review text

**Locked design rules:** use `references/design-system.md` exactly. Note the components marked OFF by default there (the green-tick `.xx-results` summary list) - do not put them on a page without a reason from the map - it holds the full CSS to paste, the token block, the type scale, the 44px section rhythm (heading → text → image), the inline-block left-aligned lists, the green-tick proof list, the emoji use list, the pill accordions with the rotating chevron and the two `name=` groups, the review stack, the trust trio, the guarantee lines, the closer bar, the grey image placeholders and the 600px type step-down. Per product, only the accent tokens change (`--xx-accent`, `--xx-accent-dark`, `--xx-accent-soft`) plus the 2-letter class prefix. No new fonts, no extra colours, no inline styles, no second layout.

**Liquid notes: only Shopify's own comment tag.** Every note in the Liquid (section markers, instructions) is written `{%- comment -%} ... {%- endcomment -%}`. Never `{# ... #}`: that is Jinja/Twig syntax, Shopify does not know it and prints it as visible text on the live page. `build-image-manifest.py --liquid` fails the build when it finds `{#`.

**Locked copy rules:** payment exactly as the store profile says (never a method listed under `payment never`); no em-dashes or double-hyphens; FDA-safe verbs for supplements/skincare; bold keywords green; review authors use first name + town (or initials) from the REAL customer, with permission; the set is four 5-star and one 4-star, the 4-star carrying one honest gripe; local flavor from the market profile (currency, places, everyday words, scenes). **No invented review counts, ratings, "10,000+ customers", or fake urgency — all social proof and scarcity must be real.**

**Class prefix system:** every product gets a 2-letter prefix (e.g. `cf-` car fan). For new products, pick the first letters of 2 distinct words in the slug.

NOTE ON EXAMPLES: `examples/` holds one finished image-prompts pair in the locked format (a fictional store in the example market). The SECTION ORDER always follows `references/copywriting-framework.md` and `templates/master-template.liquid`.

### Phase 6 — Delivery (all four parts, always, without being asked)
A build is not delivered until all four are on the table. Never stop after the Liquid and offer the rest - the page cannot go live without them, and asking the user to request them wastes a round trip.

1. **The two `.liquid` files and the launch manifest** — the journey badge section, `sections/product-description-<slug>.liquid` (JSON validity check on both schemas) and `<slug>-product.json` (title = own product name, slug, template suffix = slug, the price and the compare-at price exactly as the user gave them, prefix, description section name, badge colours; format in `references/pre-build-setup.md`). The product setup creates the product and template; Claude Code puts the Liquid into the template with the prompt the setup writes.
2. **The review frames document** — the 5 cards from Phase 3b, written out in full: one nine-row table per card (Purpose · Mirror · Map lines · Emotional arc · Sentence frame · Must contain · Must avoid · Photo brief · Ask for it with), then the coverage check table, then the day-7 WhatsApp collection message. This ships with EVERY build, whether or not the store has reviews yet: the schema presets only carry a one-line summary of each frame, and the page is worthless as social proof until someone fills them with real words.
3. **The image prompts document** (Phase 7) — the casting brief, one complete self-contained prompt per section image and per gallery slide in the infografic style with the page's accent hex, the real-photo shot lists, and the gaps list. Delivered with every build, not on request. It ships as TWO files: `<slug>-image-prompts.md` for people and `<slug>-images.json` for the image generator, built from the .md by `scripts/build-image-manifest.py` (see Phase 7).
4. **A short summary** — accent colour, the angles chosen with the map line behind each, the persuasion-check and copy-voice-check verdicts, any honest disclaimers added.
5. **The open items list** — what still has to come from the real world before publishing: the images, the first real reviews, and any [CONFIRM] left in the copy.

Tell the user that the review slider is in the template but OFF (theme editor, Product Description section, tick "Show reviews section" to show it), which band settings to fill with the store's real count and average before turning it on, and that each frame card is replaced by a real review block (her words, her photo if she sent one) as the day-7 answers come back.

### Phase 7 — Image prompts (infografic-style, driven by the customer map)
**Always produced and delivered as part of Phase 6, never held back for a request.**
All section feature images and all catalog / gallery slides are generated with **`references/infografic-style.md`**. That file owns the LOOK and the prompt skeleton: attractiveness first, emotion within one second, one message per image, the REFERENCE IMAGE INSTRUCTION, the adaptable accent colour, the white hook + accent payoff stacked caption, arrows, coverage arcs, chips, product cutouts, comparison splits, and the standard catalog set.

The **customer mind map (Phase 2) decides the content**, exactly as it decides the copy:
- **Who is in the image** — the persona and sub-personas from the map, not a model ideal.
- **The scene** — a painful moment (layer 4), a hidden habit (layer 3) or the identity moment (layer 7), in her real setting.
- **The emotion to hit in one second** — from layer 6, the deep desire.
- **Which feature each image carries** — the feature that answers the next objection in the ranking (Part E), in that order.
- **The caption words** — her exact words from the language bank, never supplier phrasing, never a word from the "avoid" list.
- **The accent colour** — NOT chosen here: it is the Phase 4 accent, the same hex as the page CSS and the journey badge. State it as name + hex in every prompt and keep it identical across the whole set, so the images and the page read as one designed product.

**Market adaptation (from the store profile and its market profile).** Local settings and local people, the page language with the local words from the language bank, the store's currency and units, the local hooks from the market profile, and the standard commerce labels kept recognisable: **pay on delivery**, **free delivery** (only when the store profile says so), **order now**. The Arabic conventions and the Canva Arabic caveat in infografic-style apply only on Arabic-language pages.

**Every prompt is self-contained.** Write the shared REFERENCE + SETTING + PEOPLE + LOOK + accent block once at the top for reference, then repeat it in full inside every single prompt, so each one can be copied in one grab. Never "use the block above" or "same as slide 1". Put the image's job and the map layer it serves on one line OUTSIDE the copy block.

Deliver in this order: the casting brief from the map · the shared block · one complete prompt per section image (`{{IMAGE_HERO}}`, `{{IMAGE_PROBLEM}}`, `{{IMAGE_BENEFIT_1..3}}`) · one complete prompt per catalog slide · real-photo shot lists for anything that must not be generated (review photos, storefront, team, the rider handover) · the gaps list, where each gap says what it must show, who is in it, which fear it works on, the first-second emotion, and how to get it.

Never: AI people presented as customers (no names, quotes, stars or Verified on generated people), before/after body or health results, or a product that looks better than the one in the box.

**Machine-readable manifest (always, last step of Phase 7).** The prompts are generated automatically, so the .md follows the locked format in **`references/image-manifest.md`**: `# <Product> — image prompts` on line 1, the `ACCENT: <name> #HEX` header line, headings `## <n> — {{IMAGE_X}} · <title>` for section images and `## <n> — Slide <N> · <title>` for catalog slides, exactly one ``` block per image, every prompt starting with `REFERENCE IMAGE INSTRUCTION:` and ending with its format (`Square 1:1.` / `Landscape 4:3.` / `Portrait 4:5.`), `The product does NOT appear in this image.` where the product is absent, and `**REAL PHOTO — do not generate.**` above any block that must be shot for real. Then run:

`python scripts/build-image-manifest.py <slug>-image-prompts.md --slug <slug> --store <store> --liquid sections/product-description-<slug>.liquid`

It writes `<slug>-images.json` (ids `image_hero`, `image_benefit_1`, `slide_image_01` ...) and cross-checks every `{{IMAGE_X}}` in the Liquid. Any `ERROR` means the .md is fixed and the script run again; the build is not delivered until it prints `OK`. Never write the .json by hand.

**Image slots fill themselves (automation contract, every product).** Every section image in the Liquid uses the slot pattern in `references/design-system.md` / `templates/master-template.liquid`: an `image_picker` whose id is the image's id in `<slug>-images.json` (`image_hero`, `image_problem`, `image_benefit_1` ... `image_close`), with the fallback `images['<slug>_<image_id>.png']`. The image factory uploads each generated section image to Content > Files under exactly that name, so after the upload the page shows its images with no theme editing and no manual picking; a picker filled by hand still wins. Never use `{{IMAGE_X}}` text placeholders or a slot without the `images[...]` fallback in new pages. `build-image-manifest.py --liquid` checks the wiring and fails the build when a slot or an image is missing.

**Hand-off: APEX v2 (Google Drive, the default).** After the files are built and checked, save the build to the user's Google Drive with the Google Drive connector, so the watcher on the PC runs steps 2 to 4 by itself:
1. Find the folder `APEX` in My Drive (`search_files`: `title = 'APEX' and mimeType = 'application/vnd.google-apps.folder' and parentId = 'root'`); create it only if it is missing.
2. Create the folder `<slug>` inside `APEX` (reuse it if it exists).
3. Upload each file with `create_file`: `title` = the exact file name, `textContent` = the file content, `contentMimeType` = `text/plain` (`application/json` for .json), **`disableConversionToGoogleType: true`** (otherwise Drive turns it into a Google Doc and the PC gets no real file), `parentId` = the `<slug>` folder. Files: `<slug>-product.json`, `product-description-<slug>.liquid`, `<slug>-image-prompts.md`, `<slug>-review-frames.md`, `<slug>-build-notes.md`. (The images .json is built on the PC; the journey badge is already in the factory folder.)
4. LAST, upload `READY.txt` listing those file names, one per line, plus the line `inbox: <name>` when the input came from `APEX/_inbox/<name>/` (the watcher takes the photos from its `photos/` folder), or, in sheet mode, the lines `photos_row: <n>` and `sheet_row: <n>` (the watcher takes the photos from `Desktop\apex-inbox\<n>\`; then update the row: `references/sheet-mode.md` step 4). The watcher starts only when READY.txt exists and every listed file has synced.
5. **Changes to a build already handed off** (the user corrects a claim, a price, a caption, an image): fix the files, then in `APEX/<slug>/` trash each changed file (`trash_file`) and upload the new version with the same name (Drive cannot overwrite; two files with one name confuse the sync), then LAST trash READY.txt and upload it again with the same lines plus `rev: <n>` (2 for the first change, then 3, ...). A changed READY.txt is the watcher's signal: it reruns by itself, pushes the new page text, keeps the images when no image prompt changed, and makes every image again when a prompt changed. Check each upload's `fileSize` against the local file. Nothing for the user to type.
6. **Status and retry from the chat.** `APEX/<slug>/STATUS.txt` (status, stage, detail) and `apex-log.txt` (the full output of every stage) are written by the watcher; read them with `read_file_content` when the user asks how a product is doing or says it stopped, and report the stage output. After the user fixed the cause (e.g. added photos), "APEX retry <slug>" = create `RETRY.txt` (any text) in `APEX/<slug>/`; the watcher reruns within 30 seconds.
Also present the files for download as usual (APEX v1 fallback). End the delivery with "APEX: next steps": in sheet mode the full-size photos go into `Desktop\apex-inbox\<n>\` (one folder per sheet row, 1.jpg = the clearest); with a Drive intake folder there is nothing to copy (the watcher takes the photos from `_inbox/<name>/photos/`); without one, drop the same photos into `Desktop\apex-inbox` on the PC. The watcher starts with Windows once `.\apex-watch.ps1 -Install` was run (one time); product setup, page install and Image Factory run by themselves, print every stage in the minimized "APEX watcher" window and write STATUS.txt + apex-log.txt into `APEX/<slug>/`; the PC must be on and signed in. If the Drive connector is not available, fall back to v1: download the files, then `.\new-product.ps1 <slug>`, Claude Code, `.\run-factory.ps1 <slug>`. Never give CMD syntax: the user works in PowerShell.

### Phase 8 — Refinement
Wrong specs, tone, weak hook (offer 3 alternatives), ad warnings (soften + disclaimers), bundle pricing (`references/bundle-pricing.md`).

## Compliance — refuse or rewrite
REFUSE: kg/days weight-loss claims, sexual/ED angles, disease "cure" language, fake doctor/celebrity imagery, branded IP. REWRITE medical claims into FDA-safe verbs. Add a disclaimer footer for supplements and skincare. Full detail in `references/compliance-rules.md`.

## Quality checklist
- [ ] Every image prompt is self-contained: the shared block repeated inside it, copy-paste ready
- [ ] Persuasion check run and passed (no hard fails); every advisory fail has a stated reason
- [ ] Copy voice check run: headings carry a person or a consequence, the pain point is a scene, second person throughout, every section ends on a consequence
- [ ] The review frames document delivered with the files (5 nine-row tables + coverage check + day-7 collection message)
- [ ] The image prompts document delivered with the files (shared block repeated in every prompt, page accent hex, real-photo shot lists, gaps list)
- [ ] `<slug>-images.json` built by `scripts/build-image-manifest.py` with `--liquid`, printed `OK`, delivered next to the .md
- [ ] All four delivery parts handed over in one message without the user asking
- [ ] Two desire peaks, a CTA after each, price justified, page closes on identity then risk reversal
- [ ] Angles chosen from the map and stated with the map line behind each
- [ ] Section order matches the copywriting framework exactly
- [ ] Q1 headline + sub-headline present and benefit-driven
- [ ] Pain point section agitates with emoji then turns to desire
- [ ] Copy traces to the customer map, line by line; nothing invented from the supplier text
- [ ] `<slug>-product.json` delivered: own product name, price and compare-at price exactly as the user gave them, badge colours = page accent
- [ ] No `{# ... #}` anywhere in the Liquid: every note is `{%- comment -%} ... {%- endcomment -%}` (Shopify prints `{# #}` as text)
- [ ] Schema header texts are max 50 characters. Schema names (section, blocks, presets) are max 25 characters; Shopify rejects the whole section otherwise (block name "Customer Review", never a longer label)
- [ ] Every image prompt works from the standard product photos alone; no prompt or open item asks for an extra per-image reference photo
- [ ] Social Proof = the 5-card review SLIDER after the pain point, in the template but OFF by default (`show_reviews` checkbox, default false, wrapping the whole section), frame cards as fallback, band with up to 4 uploaded avatars (none shown when none uploaded) + count + rating settings, card photos only when uploaded (no empty image boxes), four 5-star and one 4-star, arrow buttons, real customer words only in the blocks
- [ ] Review band shows BOTH lines always: `{{ section.settings.reviews_count_line | default: '[count]+ Verified Reviews' }}` and the ★★★★★ + `reviews_rating_line | default: 'Excellent, [avg] out of 5 stars'`, both editable schema text settings with those defaults, no `if` around them
- [ ] Trust line only if true; no invented counts or ratings
- [ ] Benefits deep dive capped at TOP 3, each text then image
- [ ] Us vs Others comparison table (5 to 6 rows)
- [ ] Final CTA + the REAL guarantee (store profile, word for word) + COD closer; urgency only if real
- [ ] FAQ is 5 to 6, objection-based
- [ ] Order Journey Badge delivered as a SEPARATE section, placed ABOVE the product image gallery, colors set
- [ ] Three info accordions (Box / Delivery / Order) FIRST in the description, before the hook
- [ ] NO who-it's-for, NO spec table, NO trust trio
- [ ] Bold keywords green; checkmarks green; accent applied consistently
- [ ] Schema valid JSON; mobile query; CSS scoped to unique prefix
- [ ] No payment method from the store profile's `payment never`; no em-dashes or double-hyphens; no banned claims
- [ ] Disclaimer footer if supplement/skincare

## Files in this skill
- `references/copywriting-framework.md` — THE MAIN framework (Ayoub). Read first.
- `templates/journey-badge-template.liquid` — standalone Order Journey Badge section (goes ABOVE the gallery)
- `templates/master-template.liquid` — description section, locked framework order
- `references/apex.md` — APEX, the whole system in one table (the four steps, files, folders)
- `references/sheet-mode.md` — the default input: a product row of the APEX Products sheet (read, checks, BUILD → DONE, title green)
- `references/pre-build-setup.md` — launch: `<slug>-product.json` + `new-product.ps1` (product + unique template, Claude Code prompt)
- `references/badge-colors.md` — accent color palette guide
- `references/design-system.md` — the exact CSS and design rules for every page
- `references/customer-mind-map-brief.md` — Phase 2: the map that is the source of every line
- `references/review-frames.md` — Phase 3b: the 5 review frames and their design
- `references/infografic-style.md` — THE look and prompt skeleton for all image prompts (Phase 7), with content decided by the customer map
- `references/image-prompt-framework.md` — Feature -> Emotion mapping helper
- `references/image-manifest.md` — the locked prompts-file format and the `<slug>-images.json` contract for automated image generation
- `scripts/build-image-manifest.py` — builds and validates `<slug>-images.json` from the prompts .md (Phase 7 last step)
- `examples/noir-bangle-image-prompts.md` + `examples/noir-bangle-images.json` — a finished pair in the locked format
- `references/store-profile.md` — the store facts (brand, colour, payment, guarantee, delivery, market) and the profile template
- `references/market-example-kenya.md` — an example market profile: place names, everyday words, scenarios
- `references/compliance-rules.md` — refuse / rewrite rules
- `references/bundle-pricing.md` — optional pricing upgrade
