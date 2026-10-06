# Image manifest — the machine-readable side of Phase 7

Every build ships TWO image files:

| File | For | Written by |
|---|---|---|
| `<slug>-image-prompts.md` | people: read, copy, review | Claude, in the format below |
| `<slug>-images.json` | the image generator (`factory.py`) and later the Shopify upload | `scripts/build-image-manifest.py`, built FROM the .md |

Never write the .json by hand. Write the .md in the locked format, then run the script. The
script builds the .json and refuses to write it when the .md breaks the format, so a wrong
heading is caught at build time, not when 15 images are being generated.

## The locked .md format

The rules of Phase 7 (casting brief, shared block, self-contained prompts, shot lists, gaps
list) stay exactly as they are. These are the extra rules the script depends on:

1. **Line 1:** `# <Product name> — image prompts`
2. **Header line** containing the store and the accent, in this pattern:
   `**<Store> <Market> · <price> · ACCENT: <colour name> #RRGGBB**`
   e.g. `**Northwind Kenya · KSh 3,700 · ACCENT: deep wine #7B2D42**`. The store key is always
   passed with `--store <key>` (and the page language with `--language`, default `en`).
3. **Section image heading:** `## <n> — {{IMAGE_X}} · <short title>`
   The placeholder is the exact one used in the Liquid (`{{IMAGE_HERO}}`, `{{IMAGE_PROBLEM}}`,
   `{{IMAGE_BENEFIT_1}}` ...).
4. **Catalog slide heading:** `## <n> — Slide <N> · <short title>`, slides numbered 1, 2, 3 ... in a row.
5. **Job line (optional):** one italic line under the heading, outside the block: `*Kills objection 1, strength 5.*`
6. **Exactly one ``` block** per image heading. It holds the complete prompt and nothing else.
7. **The prompt starts with** `REFERENCE IMAGE INSTRUCTION:` and **ends with the format** as its
   last sentence: `Square 1:1.` · `Landscape 4:3.` · `Portrait 4:5.` (then `No other text, no logos, no watermarks.`).
   Allowed ratios: 1:1, 4:5, 5:4, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16.
8. **Product not in the scene:** write the exact sentence `The product does NOT appear in this image.`
   inside the REFERENCE line. The generator then sends no product photo for that image.
9. **Real photo, never generated:** put `**REAL PHOTO — do not generate.**` on its own line between
   the heading and the block. The block then holds the shot list.
10. **Every other `##` heading** (shared block, casting brief, shot lists, gaps list) must NOT contain
    `{{IMAGE_` or the word `Slide` followed by a number, or it is read as an image.

## Naming (fixed, used everywhere after this)

| In the .md | id / output file |
|---|---|
| `{{IMAGE_HERO}}` | `image_hero` → `image_hero.png` |
| `{{IMAGE_BENEFIT_1}}` | `image_benefit_1` → `image_benefit_1.png` |
| `Slide 1` | `slide_image_01` → `slide_image_01.png` |

The section id is the placeholder name in lower case. In the Liquid it is the `image_picker` id of
that slot, and the slot falls back to the file `<slug>_<image_id>.png` in Content > Files (pattern in
`references/design-system.md`). The image factory uploads each section image under exactly that
name, so the page fills itself: no links pasted, no theme editor. Catalog slides go to the product
gallery in slide order. Every new page uses the self-filling slots; a page with old `{{IMAGE_X}}`
text placeholders is rebuilt with PageEngine before its images are uploaded.

## The .json (what the script writes)

```json
{
  "schema": "page-image-manifest/1",
  "product": "Noir Bangle",
  "slug": "noir-bangle",
  "store": "mystore",
  "language": "en",
  "accent": { "name": "deep wine", "hex": "#7B2D42" },
  "prompts_file": "noir-bangle-image-prompts.md",
  "counts": { "generate": 14, "real_photo": 1 },
  "images": [
    {
      "id": "image_hero",
      "kind": "section",
      "placeholder": "{{IMAGE_HERO}}",
      "slide": null,
      "title": "quiet, not flashy",
      "job": "Emotion: quietly put-together. ...",
      "generate": true,
      "output_file": "image_hero.png",
      "real_photo": false,
      "aspect": "4:3",
      "use_reference": true,
      "prompt": "REFERENCE IMAGE INSTRUCTION: ... Landscape 4:3. No other text, no logos, no watermarks."
    },
    {
      "id": "slide_image_09",
      "kind": "slide",
      "placeholder": null,
      "slide": 9,
      "title": "Trust",
      "generate": false,
      "output_file": "slide_image_09.png",
      "real_photo": true,
      "shot_list": "Shot list: ..."
    }
  ]
}
```

Full worked example (one product, the format is the same for every product): `examples/noir-bangle-images.json`.

## The delivery step

```
python scripts/build-image-manifest.py <out>/<slug>-image-prompts.md \
    --slug <slug> --store <store> \
    --liquid sections/product-description-<slug>.liquid
```

- `ERROR` lines: fix the .md and run again. Do not deliver until it prints `OK`.
- `--liquid` cross-checks the page: every section image must have a self-filling slot for
  `images['<slug>_<image_id>.png']`, every slot must have a prompt, and every `image_*` picker must
  have the file-name fallback (all errors). Old `{{IMAGE_X}}` placeholders are still accepted.
- `WARN` lines: read them, fix or state the reason in one line in the summary.
- If the script cannot run in the environment, say so in the open items list and deliver the .md
  only. Never hand-write the .json instead.
