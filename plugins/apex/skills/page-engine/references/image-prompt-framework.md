# Feature → Emotion Image Prompt Framework

The principle: a product image should make the customer *feel* the benefit, not just show the part. For each image, work through three steps before writing the prompt.

## The 3-step framework

### Step 1 — Identify the FEATURE
What is this section explaining? Be specific: "magnetic base", "120-min battery", "3 spray modes".

### Step 2 — Identify the EMOTION
What feeling does the customer get from this benefit? Examples:
- Magnetic base → **ease & relief** (the tool holds itself, hands free)
- Long battery → **freedom & security** (no power anxiety)
- 3 spray modes → **control & confidence** (right tool for any job)
- Hidden camera in a bulb → **peace of mind & cleverness**
- Quiet fan → **comfort & calm** (kids can nap)
- 360° mirror → **mastery & pride** (look perfect from every angle)
- Cordless scrubber → **liberation** (no cables, go anywhere)
- 0.1° accuracy → **trust & precision** (no second-guessing)

### Step 3 — VISUALIZE that emotion
Write the prompt so the image *conveys* the feeling — through body language, lighting, environment, contrast — not through text.

## Two prompt styles

### Lifestyle/Emotional sections — show real local people (market profile) feeling the benefit

Use cues like:
- Eyes closed, soft smile → bliss, relief
- Wiping forehead, fanning → the pain BEFORE
- Relaxed hands, no clutter → freedom
- Focused craftsman face → confidence, mastery
- Mother gently watching child sleep → peace of mind
- A group laughing in a car → shared comfort

### Technical/Feature sections — explain the feature visually but still convey emotion

Use cues like:
- Cutaway diagrams + clean callouts → trust, engineering quality
- Spec comparison (weak vs strong) → vindication
- 3D grid of options → control, choice
- Dramatic close-up of materials → durability, premium

## Standard prompt structure (every prompt uses this)

```
REFERENCE IMAGE INSTRUCTION:
Use the uploaded reference image as the EXACT product to feature.
[1-2 sentences describing the product specifics]. Match its exact
design — do not change shape or color.

---

PROMPT:
[Setting: where, when, mood, lighting]

[Main subject: who is doing what, with the product clearly visible]

[Their expression / body language conveying THE EMOTION]

[Supporting details: environment that reinforces the emotion]

Minimal or no text. Let [specific visual element] carry the emotion.

Style: premium [cinematic / lifestyle / technical] photography,
[warm / cool / dramatic] lighting, authentic local setting from the market profile,
photorealistic, 4K quality.
Aspect ratio: square (1:1) or landscape (4:3).
```

## Consistency rules across all images for ONE product

- Same reference product appearance throughout
- Same color signature (the badge color reused as accent in airflow / lighting / callouts)
- Authentic local models specified (age, skin tone, clothing from the market profile)
- Local settings from the market profile (example market Kenya: modern compound, Nairobi street, Mombasa coast, tidy workshop, dukas)
- **Minimal text** — anything that comes out messy, the user adds in Canva afterward
- For "problem" and "solution" pairings, use the **same model and setting** to make a clean before/after story

## Compliance for images

Refuse to write prompts for:
- Fake doctor / medical authority figures
- Branded character or copyrighted imagery (Disney, Marvel, sports logos)
- Sexual or suggestive content
- Graphic medical conditions on real-looking children
- Misleading "before/after" weight-loss imagery

For skincare before/afters: it's fine to specify "realistic moderate skin condition transformations" but ad-platform reviewers may still flag — the user should ideally replace AI-generated medical visuals with real customer photos when collected.

## Worked example — car cooling fan

**Section:** "Quiet enough to nap with it running"
**Feature:** Quiet whisper-soft motor
**Emotion:** Peace, comfort, the absence of irritation
**Visualization:**

Example market: Kenya.
```
REFERENCE IMAGE INSTRUCTION: Use the uploaded reference image —
a compact black dual-fan car cooling fan with velcro straps.
Match its exact design.

PROMPT:
A warm, soft-lit photo inside a modern car on a bright sunny day.
A young dark-skinned Kenyan child rests peacefully against a
travel pillow in the back seat, eyes gently closed, deep in a
calm nap. Subtle teal airflow lines from the black dual-fan
cooling fan mounted on the headrest in front of her hint at the
quiet cool air keeping her comfortable. Her face is utterly
peaceful — no stress, no heat, just rest.

The car interior is calm and clean, light grey seats, soft natural
light. Outside the window, a hot sunny day visible — emphasizing
that despite the heat outside, inside is peaceful and quiet.

Minimal or no text. Let the child's peaceful sleep carry the
emotion of "quiet comfort."

Style: premium cinematic lifestyle photography, soft warm light,
authentic Kenyan child, shallow depth of field, photorealistic,
4K quality.
Aspect ratio: square (1:1) or landscape (4:3).
```

## When asked for all image prompts at once

Generate the full set in one response. For each placeholder, include the **3-step framework** explicitly:

```
## IMAGE 1 — [SECTION NAME]
🧠 Feature → Emotion
Feature: [what]
Emotion: [feeling]
Visual cue: [what shows the feeling]

PROMPT:
[full prompt here]
```

End with a quick reference table mapping all images to their feature → emotion combinations.
