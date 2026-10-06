#!/usr/bin/env python3
"""
build-image-manifest.py - Phase 7 delivery step.

Reads the image prompts document (<slug>-image-prompts.md), checks it against the
locked format in references/image-manifest.md, and writes <slug>-images.json next to it.
The .md is for people, the .json is for the image generator. Because the .json is BUILT
from the .md, the two can never disagree.

  python scripts/build-image-manifest.py out/<slug>-image-prompts.md \
      --slug <slug> --store <store> --liquid sections/product-description-<slug>.liquid

Exit code 0 = manifest written. Exit code 1 = the .md breaks the format: fix the .md, run again.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "page-image-manifest/1"
ALLOWED_ASPECTS = {"1:1", "4:5", "5:4", "4:3", "3:4", "3:2", "2:3", "16:9", "9:16"}

TITLE_RE = re.compile(r"^#\s+(.+?)\s+[—-]+\s+image prompts\s*$", re.I | re.M)
ACCENT_RE = re.compile(r"ACCENT:\s*([^#*\n]+?)\s*(#[0-9A-Fa-f]{6})")
HEADING_RE = re.compile(r"^##\s+(.*)$", re.M)
FENCE_RE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)
PLACEHOLDER_RE = re.compile(r"\{\{\s*IMAGE_([A-Z0-9_]+)\s*\}\}")
SLIDE_RE = re.compile(r"\bSlide\s+(\d+)\b", re.I)
TITLE_AFTER_DOT_RE = re.compile(r"·\s*(.+)$")
ASPECT_RE = re.compile(r"\b(Square|Landscape|Portrait)\s+(\d{1,2}:\d{1,2})\b", re.I)
REAL_PHOTO_RE = re.compile(r"REAL PHOTO", re.I)
NO_PRODUCT_RE = re.compile(r"product does NOT appear", re.I)
JOB_RE = re.compile(r"^\*(?!\*)(.+?)\*\s*$", re.M)


def build(md_path: Path, slug: str | None, store: str | None, language: str | None) -> tuple[dict, list, list]:
    text = md_path.read_text(encoding="utf-8")
    errors, warnings = [], []

    title = TITLE_RE.search(text)
    if not title:
        errors.append("Line 1 must be '# <Product name> — image prompts'.")
    accent = ACCENT_RE.search(text)
    if not accent:
        errors.append("Missing the accent line, e.g. '**... · ACCENT: deep wine #7B2D42**'.")
    if not store:
        errors.append("No store key: pass --store <key> (the store profile / .env.<key> name).")

    heads = list(HEADING_RE.finditer(text))
    images, ids = [], set()
    for i, h in enumerate(heads):
        heading = h.group(1).strip()
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        ph, sl = PLACEHOLDER_RE.search(heading), SLIDE_RE.search(heading)
        if not ph and not sl:
            continue  # shared block, casting brief, shot lists, gaps list

        where = f"'## {heading}'"
        fences = FENCE_RE.findall(body)
        if len(fences) != 1:
            errors.append(f"{where}: needs exactly one ``` block, found {len(fences)}.")
            continue
        block = fences[0].strip()
        before = body[: body.index("```")]
        real = bool(REAL_PHOTO_RE.search(before))

        if ph:
            img_id, kind, placeholder, slide = f"image_{ph.group(1).lower()}", "section", f"{{{{IMAGE_{ph.group(1)}}}}}", None
        else:
            slide = int(sl.group(1))
            img_id, kind, placeholder = f"slide_image_{slide:02d}", "slide", None
        if img_id in ids:
            errors.append(f"{where}: duplicate id {img_id}.")
        ids.add(img_id)

        t = TITLE_AFTER_DOT_RE.search(heading)
        job = JOB_RE.search(before)
        item = {
            "id": img_id,
            "kind": kind,
            "placeholder": placeholder,
            "slide": slide,
            "title": t.group(1).strip() if t else heading,
            "job": job.group(1).strip() if job else None,
            "generate": not real,
            "output_file": f"{img_id}.png",
        }

        if real:
            item.update({"real_photo": True, "shot_list": block})
            images.append(item)
            continue

        aspects = ASPECT_RE.findall(block)
        if not aspects:
            errors.append(f"{where}: the prompt must end with the format, e.g. 'Square 1:1.' or 'Landscape 4:3.'")
            continue
        aspect = aspects[-1][1]
        if aspect not in ALLOWED_ASPECTS:
            errors.append(f"{where}: aspect {aspect} is not one of {sorted(ALLOWED_ASPECTS)}.")
        if kind == "slide" and aspect != "1:1":
            warnings.append(f"{where}: catalog slides are square 1:1 by standard, this one is {aspect}.")
        if not block.startswith("REFERENCE IMAGE INSTRUCTION"):
            errors.append(f"{where}: the prompt must start with 'REFERENCE IMAGE INSTRUCTION:'.")
        if accent and accent.group(2).lower() not in block.lower() and "none" not in block.lower():
            warnings.append(f"{where}: the accent hex {accent.group(2)} does not appear inside the prompt.")

        item.update({
            "real_photo": False,
            "aspect": aspect,
            "use_reference": not NO_PRODUCT_RE.search(block),
            "prompt": block,
        })
        images.append(item)

    if not images:
        errors.append("No image blocks found: headings must contain {{IMAGE_X}} or 'Slide N'.")

    slides = sorted(x["slide"] for x in images if x["kind"] == "slide")
    if slides and slides != list(range(1, len(slides) + 1)):
        warnings.append(f"Slide numbers are not 1..{len(slides)} in a row: {slides}.")

    manifest = {
        "schema": SCHEMA,
        "product": title.group(1).strip() if title else None,
        "slug": slug or md_path.stem.replace("-image-prompts", "").lower(),
        "store": store,
        "language": language or "en",
        "accent": {"name": accent.group(1).strip(" ·*"), "hex": accent.group(2).upper()} if accent else None,
        "prompts_file": md_path.name,
        "counts": {
            "generate": sum(1 for x in images if x["generate"]),
            "real_photo": sum(1 for x in images if not x["generate"]),
        },
        "images": images,
    }
    return manifest, errors, warnings


def check_liquid(manifest: dict, liquid: Path, errors: list, warnings: list) -> None:
    text = liquid.read_text(encoding="utf-8")
    # The review band always shows the count and rating lines, editable, with placeholder defaults.
    schema_m = re.search(r"{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}", text, re.S)
    try:
        settings = {x.get("id"): x for x in json.loads(schema_m.group(1)).get("settings", [])} if schema_m else {}
    except ValueError:
        settings = {}
    for sid, default in (("reviews_count_line", "[count]+ Verified Reviews"),
                         ("reviews_rating_line", "Excellent, [avg] out of 5 stars")):
        if not re.search(r"\{\{\s*section\.settings\." + sid + r"\s*\|\s*default:", text):
            errors.append(f"Review band: {sid} is not always shown. Render it as "
                          f"{{{{ section.settings.{sid} | default: '{default}' }}}} (no if around it), "
                          "as in templates/master-template.liquid.")
        elif re.search(r"{%-?\s*(if|unless)\s+section\.settings\." + sid, text):
            errors.append(f"Review band: {sid} is inside an if/unless and can disappear. Always show it.")
        if not str(settings.get(sid, {}).get("default") or "").strip():
            errors.append(f"Review band: the schema needs an editable text setting '{sid}' with the default "
                          f"'{default}'.")
    # Shopify rejects the whole section when a header text is longer than 50 characters.
    for st in (json.loads(schema_m.group(1)).get("settings", []) if settings else []):
        if st.get("type") == "header" and len(str(st.get("content", ""))) > 50:
            errors.append(f"Schema header '{st.get('content')}' is longer than 50 characters; Shopify rejects the section. Shorten it.")
    # The review section: in the template, but OFF by default behind one checkbox; photos optional.
    sr = settings.get("show_reviews", {})
    if sr.get("type") != "checkbox" or sr.get("default") is not False:
        errors.append("Reviews: the schema needs the checkbox 'show_reviews' (label 'Show reviews section') "
                      "with default false, so the section is off until the owner turns it on.")
    if not re.search(r"{%-?\s*if\s+section\.settings\.show_reviews\s*-?%}", text):
        errors.append("Reviews: wrap the whole review section in {%- if section.settings.show_reviews -%} ... "
                      "{%- endif -%} as in templates/master-template.liquid.")
    if re.search(r">\s*Customer photo\s*</p>", text):
        errors.append("Reviews: remove the empty 'Customer photo' placeholder boxes; a card shows a photo only "
                      "when one is uploaded.")
    # Shopify Liquid has no {# #} comments: it prints them as text on the live page.
    for n, line in enumerate(text.splitlines(), 1):
        if "{#" in line:
            errors.append(f"{liquid.name} line {n}: '{{# ... #}}' is not a Shopify comment and shows as text "
                          "on the live page. Write the note as {%- comment -%} ... {%- endcomment -%}.")
    slug = manifest["slug"]
    used_ph = set(PLACEHOLDER_RE.findall(text))                      # old style {{IMAGE_X}}
    by_name = set(re.findall(rf"images\[\s*['\"]{re.escape(slug)}_(image_[a-z0-9_]+)\.png['\"]\s*\]", text))
    pickers = set(re.findall(r"section\.settings\.(image_[a-z0-9_]+)", text))
    wired = by_name | {"image_" + p.lower() for p in used_ph}
    sections = {x["id"] for x in manifest["images"] if x["kind"] == "section" and x["generate"]}
    for i in sorted(sections - wired):
        errors.append(f"No image slot in the Liquid for {i}: add the slot pattern with "
                      f"images['{slug}_{i}.png'] (references/design-system.md).")
    for i in sorted(wired - sections):
        errors.append(f"The Liquid has a slot for {i} but there is no prompt for it.")
    for i in sorted(pickers - by_name):
        errors.append(f"The slot section.settings.{i} has no file-name fallback "
                      f"images['{slug}_{i}.png'], so it would need manual picking.")
    if used_ph:
        warnings.append("The Liquid still uses {{IMAGE_X}} text placeholders (old style). It works, "
                        "but new pages use the self-filling slots.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("md", type=Path)
    ap.add_argument("--slug")
    ap.add_argument("--store", help="store key, e.g. mystore (any name; picks .env.<store> at upload)")
    ap.add_argument("--language", help="caption language, e.g. en, sw, ar")
    ap.add_argument("--liquid", type=Path, help="product-description .liquid, to cross-check placeholders")
    ap.add_argument("--out", type=Path, help="default: <md folder>/<slug>-images.json")
    a = ap.parse_args()

    manifest, errors, warnings = build(a.md, a.slug, a.store, a.language)
    if a.liquid:
        check_liquid(manifest, a.liquid, errors, warnings)

    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        print(f"\n{len(errors)} error(s): fix them (the .md or the .liquid) and run again. No manifest written.")
        sys.exit(1)

    out = a.out or a.md.with_name(f"{manifest['slug']}-images.json")
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = manifest["counts"]
    print(f"OK    {out.name}: {c['generate']} to generate, {c['real_photo']} real photo(s)")
    for x in manifest["images"]:
        print(f"      {x['id']:<20} {x.get('aspect', '-'):<5} "
              f"{'REAL PHOTO' if x['real_photo'] else ('text-only' if not x['use_reference'] else '')}")


if __name__ == "__main__":
    main()
