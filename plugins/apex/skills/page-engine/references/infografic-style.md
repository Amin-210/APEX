---
name: infografic-style
description: >-
  Generate product image prompts in our signature infographic ad style for COD / dropshipping
  Shopify product pages (any market: the store profile sets it; Arabic-language rules included). Use this skill
  WHENEVER the user asks for image prompts, section feature images, hero images, or catalog /
  gallery (carousel) images for a product page, even if they do not say the word "infographic".
  It covers the emotion-first copy approach, the visual-attractiveness-first design bar, the
  adaptable accent-color system, white hook + accent payoff stacked captions, arrows, dashed
  coverage arcs, mode / weather chips, product cutouts, comparison splits, the prompt structure for
  Nano Banana Pro / Gemini, Arabic-language conventions, and the standard catalog slide set.
  Always follow this style exactly for these images unless the user explicitly asks otherwise.
---

# Infografic Style (Product Image Prompts)

This skill defines how we design and generate every product image prompt: both the **section
feature images** inside the product description, and the **catalog / gallery (carousel) images** at
the top of the page. The output is always a text prompt for **Nano Banana Pro / Gemini**, written so
the customer attaches the real product photo as a reference.

## Golden rules (never break these)

1. **Visually attractive above all else.** This is the single most important rule. Every image must
   look premium, clean and scroll-stopping, the kind of image that makes someone stop and buy.
   Strong composition, strong contrast, balanced layout, nothing cluttered or amateur. If a choice
   makes the image more eye-catching and more beautiful, make it.
2. **Lead with emotion and benefit, not specs.** The image must make the customer *feel* the
   outcome (safety, relief, peace of mind, time saved) within about **1 second**. Specs are only
   light supporting proof, never the lead.
3. **One clear message per image.** Headline and visual must agree and read instantly.
4. **Feature to emotion.** For each image: identify the FEATURE, identify the EMOTION the customer
   feels from it, then build a scene that *visualizes that emotion*.
5. **Match the real product.** Every prompt starts with a `REFERENCE IMAGE INSTRUCTION` describing
   the exact product, and the user attaches the product photo on every generation.
6. **Adaptable accent color (see below).** The accent is NOT fixed. It adapts to the product page
   design and the product's own colors, while staying high-contrast and eye-catching.
7. **The market comes from the store profile.** Local settings, local people and the page language
   from the store profile and its market profile. The worked examples in this file use an Arabic
   example market (Lebanon).
8. **No em-dashes or double hyphens** anywhere (project-wide copy rule).

## Accent color (adaptable, not fixed)

Pick an accent color per product that does two jobs at once:

- **Fits** the product page design and the product's own color palette, the same way the Order
  Journey Badge adapts (teal for a teal / mint product, blue for a security product, orange for a
  warm tool, etc.).
- **Pops**: stays high-contrast and instantly eye-catching against the scene, so the payoff line and
  the graphic devices grab attention.

Guidance:
- The **hook line** is usually clean **white**; the **payoff line** and the **graphic devices**
  (arrows, arcs, chips, badges) use the **accent color**.
- Choose the accent for maximum attractiveness and contrast against that specific scene. On a dark /
  night scene, a bright warm accent (for example yellow `#FFD400`) pops strongly and is a great
  default. On a bright or light product, a deeper saturated accent from the product's palette reads
  better. Always sanity-check contrast and legibility.
- Keep the accent **consistent across the whole image set** for one product so the gallery looks
  like a coherent, designed series.
- When writing a prompt, state the chosen accent explicitly (name + hex) so the generation is
  consistent, e.g. "accent color: teal #0d9488" or "accent color: bright yellow #FFD400".

## The two image types

- **Section feature images**: one per description section, each visualizing that section's feature
  and its emotion. Used inside the description.
- **Catalog / gallery slides**: the top carousel, square 1:1, a full set of listing slides. See
  "Catalog set".

## Prompt structure (use this skeleton every time)

```
REFERENCE IMAGE INSTRUCTION: Match the attached product exactly, [product: color, shape, key parts].
Keep [color / shape / key parts] identical. Reproduce every marking exactly as in the attached photo,
printed text included or a plain surface kept plain; never add or remove any.

Base scene (photographic): [a real, emotional scene in a local setting of the market with local people
where relevant, that shows the benefit. Photorealistic, cinematic, premium lighting and composition.]

Infografic overlay elements (clean modern product-ad style, attractive and uncluttered, all graphic
lines in the accent color [name + hex]):
- [arrows pointing from each label to what it describes]
- [dashed coverage arcs / angle fans / signal waves / flow arrows as needed]
- [a small circular product cutout in a bottom corner as an inset badge]
- Keep it tidy, balanced and premium looking.

Text labels (right to left, heavy bold modern Arabic sans-serif, the hook line in bright white with a
thin dark outline, the key payoff line in the accent color [name + hex], larger and bolder, with a
soft shadow so everything pops and stays readable):
- Main headline caption, two stacked lines:
  السطر الأول (أبيض): [hook line, often a question]
  السطر الثاني (باللون المعتمد، أكبر وأعرض): [payoff line, the benefit]
- [arrow labels / chips as needed]
Spell all the Arabic exactly as written. [aspect / composition]. No other added text, no logos, no watermarks.
```

## Visual style spec (the "look")

- **Attractiveness first**: premium, clean, high-contrast, balanced. Treat it like a paid-ad creative.
- **Accent color**: adaptable per product (see the Accent color section). Used for the payoff caption
  line and all graphic devices.
- **Caption formula**: a two-line stacked caption. Line 1 is a short **hook in white** (a question
  works great). Line 2 is the **payoff in the bold accent color**, larger and wider.
- **Readability**: put text on a **semi-transparent dark rounded banner**, or always give it a thin
  dark outline plus a soft drop shadow, so it stays legible over any background. Keep captions tidy in
  the upper area so they do not cover the product or the key subject.
- **Typography**: heavy bold modern Arabic sans-serif display font, right to left.
- **Graphic devices** to explain features visually (all in the accent color):
  - **Arrows** from each label to the part it points at.
  - **Dashed coverage arcs / wide ellipse** for light or detection coverage.
  - **Angle fans** (e.g. a 180 degree fan at a sensor) for range.
  - **Distance arrows** with a label for reach.
  - **Signal waves** from a remote to a device for wireless control.
  - **Day to night flow arrow** for solar charge then night light.
  - **Chips / pills**: a neat row of small rounded badges with an icon + short Arabic label.
  - **Product cutout**: a small circular inset of the product in a corner.
  - **Comparison split**: "us vs others" with green checks vs red X marks.
  - **Cert badge**: a bold rounded badge (e.g. an IP65 badge).

## Arabic-language pages (example: spoken Lebanese)

Apply this block only when the page language is Arabic; for another dialect, swap the markers and
hooks for that dialect's.

- Write in **spoken Lebanese colloquial**, the way locals talk, not Modern Standard Arabic.
  Markers: عم، بدّك، هلق، منيح، بيولّع، بيضل، ما في، لحالو، بكم دقيقة.
- **Right to left**, exact spelling (image generators garble Arabic, so spelling must be explicit).
- **Western numerals** (3000, 270, 15) and **metric units** (متر).
- **Local emotional hooks** where the product allows: التقنين، اشتراك الموتور، قطع الكهربا.
- Standard commerce labels stay recognizable: **توصيل مجاني**، **الدفع عند الاستلام**، **اطلب الآن**.
- Verb collocations matter: **حسّ بـ** not "حسّ في". Prefer **منوّر** over "مضوي".

## Catalog / gallery set (square 1:1 carousel)

A complete gallery highlights everything. Standard slides (adapt to the product):

1. **Hero**: clean studio product shot + short benefit headline + 3 quick tick benefits.
2. **Core benefit / brightness / coverage**: the product doing its main job.
3. **Smart / sensor feature**: detection range, angle fan, distance arrow, the catch / deter moment.
4. **Power / reliability**: for solar, a day to night split, plus the no-bill / blackout clincher.
5. **Modes / control**: mode chips + control method.
6. **Durability / weather**: weather chips + any cert badge (e.g. IP65).
7. **Easy install**: mounting in minutes, no wiring, simple 1-2-3, mount height.
8. **What is in the box + dimensions**: neat kit flat-lay + size arrows.
9. **Us vs others**: comparison split, green checks vs red X.
10. **Trust / guarantee**: free delivery, cash on delivery, money-back, warranty badges.

Provide a shared `REFERENCE + FORMAT + STYLE` block once (including the chosen accent color), then
give each slide as a concise scene + labels block the user prepends the shared block to. Keep the
**same accent color across the whole set** so the gallery looks coherent.

## Aspect ratios

- Hero and high-contrast story shots: **landscape ~4:3** (needs width).
- Catalog / gallery slides: **square 1:1**.
- Single dramatic product or weather shots: **4:3 or portrait**.

## Tools and workflow

- Prompts are for **Nano Banana Pro / Gemini**, and are also generated automatically with the OpenAI
  Images API (`gpt-image-2.5-sunburst`) through `<slug>-images.json` (see `references/image-manifest.md`).
- The user **attaches the real product photo** as a reference on every generation.
- **Arabic text caveat (always tell the user)**: image generators frequently garble Arabic,
  especially with several labels. For the cleanest, most attractive result, generate the
  **photographic scene plus the accent-color graphics** in the AI, then **add the Arabic text labels
  in Canva** for perfect script, exact accent color, and precise placement. Always include the exact
  Arabic so they can copy it.

## Lessons from automated generation (tested on gpt-image-2.5-sunburst)

The prompts are also generated automatically (OpenAI Images API, one call per prompt, the product
photo attached). These rules came out of real test runs and hold for EVERY product, niche and market:
a watch, a supplement bottle, a skincare jar, a tool or a gadget. Apply them in every prompt.

1. **Markings follow the photo.** The model copies printed text on the product (a brand name, a
   label, a logo on the packaging) in some images and drops it in others. The REFERENCE line always
   ends: "Reproduce every marking exactly as in the attached photo, printed text included or a plain
   surface kept plain; never add or remove any." The closing line says "No other ADDED text", so it
   is never read as "remove the product's own label".
2. **Captions over busy, split or multi-photo images go on banners.** Over a grid, a split, a
   patterned background, or clothing / props near the accent colour, accent-coloured text disappears.
   Put each caption line on its own solid rounded banner: line 1 white on a dark charcoal banner,
   line 2 white bold capitals on a solid accent banner. Keep things behind the caption out of the
   accent colour.
3. **Chips describe what the image shows.** A chip naming another moment than the scene (a time of
   day, a use, a place) is a copy error. Write each scene and its chip together.
4. **When the product must NOT appear, nothing may look like it.** Give the other objects in the
   scene a clearly different colour, shape or design from the product, or the buyer reads the scene
   as the product.
5. **Actions are written as a visible pose, with a negative.** "Hovers, not choosing" was drawn as
   picking something up. Write the body position ("hand hovers above, fingers open and NOT touching").
6. **A defect that carries the story is named physically.** "Old", "dead" or "worn out" came out
   looking normal. Write what the eye sees: cracked glass, a peeling label, a rusted edge, a stain.
7. **Every person is written out in full in every prompt.** "Her hand" or "a woman's hands" with no
   description came out as a generic light-skinned hand model. Name the casting-brief persona each
   time: market, age, skin tone, clothing (e.g. "a Kenyan woman around 30, dark brown skin",
   "a Lebanese man in his 40s"). Never "her", "the same person as above" or "the grid from the
   benefit image": the generator sees one prompt at a time.
8. **A rival in a comparison must look clearly different from the product.** "An old version" next
   to the product was drawn as the product itself, damaged, which tells the buyer OUR product fails.
   Describe the rival as another design (other shape, colour, label, no signature detail).
9. **Exact label text goes in double quotes, without a full stop.** A chip written as a sentence
   was drawn with its full stop. Write: chip with exactly this text: "Free delivery".
10. **Slow model, cheap test first.** Test new prompts at quality low (layout, product, scene), then
   generate the set at high. English spelling is already reliable at low. **Arabic is not tested
   yet:** on Arabic-language pages run the first product both ways (captions rendered, and `--text none` with
   the captions added in Canva) and keep whichever reads correctly.

Photos per image: **every image is made from the standard product photos in `reference/` only. A
prompt must never need an extra photo per image**, and the open items never ask the user for one.
When an image shows the product in a setup that is not photographed on its own (an attachment
mounted, the product open, a bundle), the prompt names the parts that ARE visible in the product
photos and describes in words how they are put together ("the head fitted on the open cup with the
round white disc inside"). If that is not enough to draw it right, choose a scene that shows the
product as it is photographed instead. So the supplier photo that shows all parts belongs in the
photos folder.

## Worked example (section image, solar security light, dark night scene -> yellow accent)

```
REFERENCE IMAGE INSTRUCTION: Match the attached product exactly, a black outdoor solar security
light with three adjustable LED heads, a solar panel on top, and a round motion sensor dome below
the center head. Keep color and shape identical.

Base scene (photographic): A Lebanese residential street at night during a power cut. Every other
house is completely dark, while ONE home is brightly lit at its entrance by the light on the wall.
A calm Middle Eastern family stands safe in the pool of light. Strong one-second contrast. Premium,
cinematic composition.

Infografic overlay elements (clean, attractive, uncluttered, all graphic lines in accent color
bright yellow #FFD400, chosen to pop on this dark scene):
- Thin arrows from each label to the part it describes.
- A small circular product cutout in a bottom corner.

Text labels (right to left, heavy bold modern Arabic sans-serif, hook line bright white with a thin
dark outline, payoff line in bright yellow #FFD400, larger and bolder, soft shadow):
- Main headline caption, two stacked lines:
  السطر الأول (أبيض): ما في كهربا؟
  السطر الثاني (أصفر، أكبر وأعرض): بيتك بيضل منوّر
- Arrow to the solar panel: بيشحن عالشمس لحالو
- Arrow to the unit: بلا أسلاك وبلا فاتورة
- Small label near the family: أمان وراحة لعيلتك
Spell all the Arabic exactly as written. Wide landscape composition. No other text, no logos, no watermarks.
```

(For a mint product the accent might be teal, for a different page palette another color, always
chosen to fit the design and pop. The structure stays identical.)
