# The design system (locked)
This is the exact look for every page. Copy the CSS below into the `<style>` block, replace `xx-` with the product's 2-letter prefix and set the accent tokens. Do not invent new styling per product: only the accent tokens change.

## One accent, everywhere — the page AND the images

The accent is chosen ONCE per product, in Phase 4, and then used in three places without variation:

1. **The page CSS** — `--xx-accent` and its dark and soft shades (ticks, accordions, chevrons, reviews button, closer bar, every bold keyword).
2. **The Order Journey Badge** — the circles take the same accent.
3. **Every image prompt** — the infografic overlay devices (arrows, arcs, chips, dimension lines, tick and X badges) and the payoff caption line are written with the SAME hex, stated by name and value in every prompt.

How to pick it (`badge-colors.md` has the category guide):
- It must **fit the product** — a teal-and-white product takes a teal accent, a warm wooden tool takes an amber one, a black metal product takes whatever its packaging or brand colour is.
- It must **pop** against the scenes the images will use: on a dark or night scene a bright warm accent, on a bright kitchen or daylight scene a deeper saturated one. Sanity-check contrast before committing.
- It must **survive both jobs**: legible as a 26px tick circle on white AND as a caption line over a photo.
- Green ticks are the one exception the store keeps: checkmark ticks stay green even when the accent is not (`badge-colors.md`).

Write the chosen accent at the top of the build as one line — `accent: terracotta #D2703A` — and paste that exact string into the CSS tokens, the badge settings and every image prompt. A page whose images use a different colour from its buttons looks like two products stitched together, and that is the single fastest way to make a page feel cheap.

Brand colours are separate and do not move: the brand bar, promise row and brand section keep the store profile's `brand colour` on every page whatever the product accent is. The accent lives inside the product zones only.

## What changes per product
Only these four lines at the top of the token block:
```
--xx-accent:      the product's accent colour (see badge-colors.md)
--xx-accent-dark: a darker shade of it, used for bold keywords and the chevron
--xx-accent-soft: a very light tint of it, used for accordion and closer backgrounds
--xx-star:        keep #f59e0b unless the accent clashes
```
Everything else is fixed.

## The full CSS (paste, swap the prefix, set the accent)

```css
/* ============ TOKENS ============ */
.xx-page {
  --xx-accent: #22c55e;
  --xx-accent-dark: #16a34a;
  --xx-accent-soft: #e8f9ee;
  --xx-ink: #1a1a1a;
  --xx-text: #3a3a3a;
  --xx-muted: #6b7280;
  --xx-border: #e5e7eb;
  --xx-red: #c0392b;
  --xx-star: #f59e0b;

  max-width: 760px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  text-align: center;
  color: var(--xx-text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}

/* ============ TYPOGRAPHY ============ */
.xx-page h2 { font-size: 24px; font-weight: 800; margin: 0 0 18px; color: var(--xx-ink); line-height: 1.3; letter-spacing: -0.3px; }
.xx-page h3 { font-size: 20px; font-weight: 800; margin: 0 0 14px; color: var(--xx-ink); line-height: 1.3; letter-spacing: -0.2px; }
.xx-page p  { font-size: 16px; margin: 0 0 14px; color: var(--xx-text); }
.xx-page strong, .xx-page b { color: var(--xx-accent-dark); font-weight: 700; }

/* ============ SECTION LAYOUT ============ */
.xx-section { margin: 0 0 44px; }
.xx-section:last-child { margin-bottom: 0; }
.xx-section img { width: 100%; max-width: 100%; height: auto; border-radius: 14px; display: block; margin: 18px auto 0; }

/* ============ IMAGE PLACEHOLDER ============ */
.xx-img-placeholder { width: 100%; background: #e5e7eb; border-radius: 14px; min-height: 220px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #9ca3af; gap: 8px; margin: 18px auto 0; }
.xx-img-placeholder .xx-ph-icon { font-size: 3rem; line-height: 1; }
.xx-img-placeholder .xx-ph-text { font-size: 0.85rem; margin: 0; font-weight: 500; }

/* ============ RESULTS BULLETS (proof list, green ticks) ============ */
.xx-results { list-style: none; text-align: left; display: inline-block; margin: 8px auto 0; padding: 0; font-size: 16px; color: var(--xx-ink); max-width: 480px; }
.xx-results li { display: flex; align-items: flex-start; gap: 12px; margin: 14px 0; font-weight: 600; }
.xx-results li::before { content: "✓"; background: var(--xx-accent); color: #fff; width: 26px; height: 26px; min-width: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; margin-top: 1px; }

/* ============ USE LIST (emoji bullets) ============ */
.xx-uses { list-style: none; text-align: left; display: inline-block; margin: 8px auto 0; padding: 0; font-size: 16px; color: var(--xx-text); }
.xx-uses li { margin: 10px 0; padding: 0; }

/* ============ ACCORDIONS ============ */
.xx-accordions { margin: 0 0 36px; text-align: left; }
.xx-accordion { background: var(--xx-accent-soft); border-radius: 10px; margin-bottom: 10px; overflow: hidden; }
.xx-accordion summary { list-style: none; cursor: pointer; padding: 16px 20px; font-size: 16px; font-weight: 700; color: var(--xx-ink); display: flex; justify-content: space-between; align-items: center; gap: 12px; user-select: none; }
.xx-accordion summary::-webkit-details-marker { display: none; }
.xx-accordion summary::after { content: "▼"; font-size: 12px; color: var(--xx-accent-dark); transition: transform .25s ease; flex-shrink: 0; }
.xx-accordion[open] summary::after { transform: rotate(180deg); }
.xx-accordion-body { padding: 0 20px 18px; font-size: 15px; color: var(--xx-text); line-height: 1.65; }
.xx-accordion-body p { margin: 0 0 10px; font-size: 15px; }
.xx-accordion-body ul { margin: 0; padding-left: 22px; }
.xx-accordion-body li { margin: 6px 0; }

/* ============ FAQ TITLE ============ */
.xx-faq-title { font-size: 22px; font-weight: 800; color: var(--xx-ink); margin: 40px 0 18px; text-align: center; }

/* ============ REVIEWS: 5-card slider (always on) ============ */
.xx-reviews{margin:0 0 44px;}
.xx-reviews-title{font-size:22px;font-weight:800;color:var(--xx-ink);margin:0 0 14px;}
.xx-reviews-cta{display:inline-block;background:var(--xx-accent-dark);color:#fff;padding:12px 26px;border-radius:10px;font-weight:700;font-size:15px;text-decoration:none;margin:0 0 18px;}
.xx-rv-band{background:var(--xx-accent-soft);border:1px solid color-mix(in srgb, var(--xx-accent) 22%, #fff);border-radius:14px;padding:16px 14px;margin:0 0 18px;}
.xx-rv-avatars{display:flex;justify-content:center;margin:0 0 8px;}
.xx-rv-avatar{width:44px;height:44px;min-width:44px;border-radius:50%;border:2px solid #fff;background:#e5e7eb;margin-left:-10px;overflow:hidden;display:flex;align-items:center;justify-content:center;font-size:20px;color:#9ca3af;}
.xx-rv-avatar:first-child{margin-left:0;}
.xx-rv-avatar img{width:100%;height:100%;object-fit:cover;margin:0;border-radius:0;}
.xx-rv-count{font-size:17px;font-weight:800;color:var(--xx-ink);margin:0 0 4px;}
.xx-rv-rating{font-size:15px;color:var(--xx-muted);font-weight:600;margin:0;}
.xx-rv-rating .xx-rv-st{color:var(--xx-star);letter-spacing:2px;margin-right:6px;}
.xx-rv-track{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:2px 2px 6px;}
.xx-rv-track::-webkit-scrollbar{display:none;}
.xx-review{flex:0 0 85%;max-width:340px;scroll-snap-align:start;background:#fff;border:1px solid var(--xx-border);border-radius:14px;padding:18px 20px;text-align:left;}
.xx-review img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:10px;margin:0 0 14px;display:block;}
.xx-review .xx-img-placeholder{margin:0 0 14px;aspect-ratio:4/5;min-height:0;border-radius:10px;}
.xx-review-name{font-size:16px;font-weight:700;color:var(--xx-ink);margin:0 0 10px;}
.xx-review-stars{color:var(--xx-ink);font-size:17px;letter-spacing:3px;margin:0 0 12px;}
.xx-review-text{font-size:16px;color:var(--xx-text);margin:0;line-height:1.6;}
.xx-rv-nav{display:flex;justify-content:center;gap:18px;margin-top:18px;}
.xx-rv-btn{width:52px;height:52px;border-radius:50%;border:0;background:#1a1a1a;color:#fff;font-size:22px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;}
.xx-rv-btn.xx-rv-prev{background:#c4c4c4;}


/* ============ TRUST TRIO ============ */
.xx-trust { display: flex; justify-content: center; align-items: flex-start; gap: 20px; flex-wrap: wrap; margin: 36px 0 22px; }
.xx-trust-badge { text-align: center; flex: 0 1 180px; }
.xx-trust-badge .icon { font-size: 44px; line-height: 1; margin-bottom: 6px; display: block; }
.xx-trust-badge .label { font-size: 13px; font-weight: 800; color: var(--xx-ink); letter-spacing: .4px; text-transform: uppercase; }

/* ============ GUARANTEE ============ */
.xx-guarantee-title { font-size: 17px; font-weight: 800; color: var(--xx-red); margin: 24px 0 12px; letter-spacing: .5px; }
.xx-guarantee-text { font-size: 15px; color: var(--xx-muted); margin: 0 auto 24px; max-width: 560px; }

/* ============ CLOSER ============ */
.xx-closer { font-size: 16px; font-weight: 800; color: var(--xx-ink); margin: 24px 0 0; padding: 16px; background: var(--xx-accent-soft); border-radius: 10px; }

/* ============ MOBILE ============ */
@media (max-width: 600px) {
  .xx-page { padding: 16px 12px 36px; }
  .xx-page h2 { font-size: 19px; }
  .xx-page h3 { font-size: 17px; }
  .xx-page p { font-size: 15px; }
  .xx-trust { gap: 14px; }
  .xx-trust-badge { flex: 0 1 130px; }
  .xx-trust-badge .icon { font-size: 38px; }
  .xx-results { font-size: 15px; }
}
```

## The rules this CSS encodes

- **Centered page, left-aligned reading.** The page is `text-align:center`, but every list is `display:inline-block` with `text-align:left` and a 480px cap, so lines never centre-wrap. Accordions and review cards are left-aligned too.
- **Section rhythm:** heading → text → image, 44px between sections, the image always last with 18px above it and a 14px radius.
- **One accent does all the colour work:** ticks, accordion background and chevron, reviews button, closer bar, and every `<strong>` in the copy.
- **Bold = green, automatically.** Wrapping a phrase in `<strong>` is the only way copy gets colour. No inline styles.
- **Emoji carry the small icons:** accordion titles (📦 🚚 🛒), use-list bullets, the review name (💬), the trust trio (🛡️ 📞 🚚) at 44px with uppercase 13px labels.
- **Two list types:** `.xx-uses` for use cases and lists (emoji bullets) is the default. `.xx-results` (green tick circles) is **OFF by default** — see below.
- **Accordion groups:** `name="xx-info"` for the info set and `name="xx-faq"` for the FAQ, so only one opens per group.
- **Image placeholders stay visible** while images are missing: grey block, 📷, and the exact instruction of what to upload in the theme editor.
- **Mobile is a type step-down, not a re-layout:** 19/17/15 and smaller trust badges at 600px.
- **Never:** new fonts, extra colours outside the tokens, shadows on text, inline styles, or a second layout for one product.

## Approved additions (written by the persuasion check)

When the audit asks for a section, it is written with these patterns. Existing classes only, the page's accent only, no new components.

**Price justification** — one `.xx-section`: h3, one short paragraph doing the maths in her terms (what the failed solution costs her over a year, or the cost per use), then an `.xx-results` tick list of 3-4 lines, then one bold closing line.

**Mid-page CTA** — one `.xx-closer` bar wrapping an anchor back to the buy form, placed right after the peak it follows:
```html
<div class="xx-closer"><a href="#MainContent" style="color:inherit;text-decoration:none">Order now — pay cash when you check it ↑</a></div>
```

**Emotional close** — one `.xx-section` before the FAQ: h3 naming the moment, three short lines drawn from layers 4, 6 and 7, then one image (or the standard `.xx-img-placeholder`). It ends on her, not on the product.

If a fix needs something the system does not have, the audit says so and stops rather than inventing a component.

## Components kept but OFF by default

These are built and styled, and stay out of a page unless the customer map gives a reason to use them.

**`.xx-results` — the green-tick "Here's What You Get" list.** A standalone summary block of 4-6 tick bullets, usually placed right after the hook. It is OFF by default for two reasons: it repeats what the benefit sections say further down, and it pulls the reader into a feature list before any proof has landed. Turn it on only when a product genuinely has several unrelated jobs a buyer cannot guess (a multi-tool, a bundle, a subscription), and then it replaces one of the benefit sections rather than adding to them. The CSS stays in `design-system.md` so it is one class away when a page needs it.

## Section markup patterns

```html
<div class="xx-section">
  <h3>Heading</h3>
  <p>One or two short lines. <strong>The phrase that matters</strong> in bold.</p>
  <ul class="xx-results"><li>Proof point</li></ul>
  {%- liquid
    assign pe_img = section.settings.image_x
    if pe_img == blank
      assign pe_img = images['<slug>_image_x.png']
    endif
  -%}
  {% if pe_img != blank %}
    <img src="{{ pe_img | image_url: width: 800 }}" alt="..." loading="lazy" width="{{ pe_img.width }}" height="{{ pe_img.height }}">
  {% else %}
    <div class="xx-img-placeholder"><span class="xx-ph-icon">📷</span><p class="xx-ph-text">Upload "..." image in theme editor</p></div>
  {% endif %}
</div>
```

**Every section image slot uses exactly this pattern (automation contract).** `image_x` is the image's
id from `<slug>-images.json` (`image_hero`, `image_problem`, `image_benefit_1`, `image_close` ...), used
three times: as the `image_picker` id in the schema, in `section.settings.image_x`, and in the file name
`images['<slug>_image_x.png']`. The image generator uploads every section image to Content > Files under
that exact name, so the page fills itself with no theme editing; an image picked by hand in the theme
editor still wins; the grey placeholder shows until either exists. Never write a slot without the
`images[...]` fallback or without the `width`/`height` attributes (theme check ImgWidthAndHeight), and never invent an id that is not in the images.json.

Trust trio, guarantee and closer at the bottom carry the store's real promises from the store profile (e.g. check before you pay · the real return policy · pay cash on delivery), never generic "100% money back / 24-7 support / 30-day guarantee".
