---
name: "apex-batch"
description: APEX batch version - builds SEVERAL product pages in one command, one after another, each with the full PageEngine skill in its own fresh helper, handed off to Google Drive for the APEX watcher as soon as it is done. Use WHENEVER the user writes "PageEngine batch", "PageEngine for rows 5, 8, 12" (rows of the APEX Products sheet), names more than one intake folder in one command ("PageEngine for _inbox/a, _inbox/b"), writes "PageEngine for all new in _inbox", "APEX batch" or "batch build". For ONE product use the page-engine skill instead (APEX v2).
---

# APEX batch version

A separate layer on top of APEX v2. It does not change PageEngine or the Image Factory: it runs
PageEngine once per product (in a fresh helper each time) and adds a check table before and a
summary after. One product = the normal PageEngine (APEX v2), not this skill.

**On the PC it uses the same watcher as single builds** (`apex_watch.py`, shipped with the
image-factory skill): several waiting products run in hand-off order, oldest READY.txt first, and
the photos in `Desktop\apex-inbox\<row>\` are copied, not moved, so every row folder keeps its
photos after DONE.


The user gives several intake folders at once. The chat is the **manager**: it checks every folder
first, then builds the products **one after another, each in its own fresh helper** (a subagent with
a clean context), and hands each one off to Google Drive as soon as it is done. The watcher on the
PC starts that product (product, page, images) while the next one is being built (overlapping).

## The command
**Sheet mode (the default):** the products are rows of the Google Sheet **APEX Products**, read with
the Google Sheets connector exactly as in page-engine `references/sheet-mode.md`.
- `PageEngine batch`: every row with BUILD = `GO` whose Country matches a store profile, top to bottom.
  `PageEngine batch <code>` limits it to one country code (e.g. `PageEngine batch KEN`).
- `PageEngine for rows 5, 8, 12`: those rows, in that order.
- Attach **one photo per product, in the same order** (the manager lists the order back in the check
  table). The full-size photos for the Image Factory are on the PC, one folder per row:
  `Desktop\apex-inbox\<row>\` (1.jpg = the clearest).
- Page notes (there is no PAGE NOTES column) come in the command, per row, e.g. "PageEngine for
  rows 5, 8 (row 8: don't mention the plug)"; the manager passes each row's notes to its helper.

**Intake folders (the backup):**
- `PageEngine for _inbox/a, _inbox/b, _inbox/c` (any separator: commas, "and", new lines), with
  **one photo attached per product, in the same order as the list**. Build order = list order.
- `PageEngine for all new in _inbox`: every intake folder in `APEX/_inbox/` whose name does not start
  with `_` and that has neither `BUILT.txt` nor `DONE.txt`, in the order of their names. Photos are
  attached in that same order (the manager lists the order back in the check table, so a wrong
  count or order is visible at once).
- One folder only = the normal PageEngine skill (APEX v2), not this skill.

## Step 1 — Check every product before building anything (the manager, itself)
**Sheet mode:** for each row, in order, run the checks of page-engine `references/sheet-mode.md`
step 2 (Country matches a store profile, BUILD GO, PRICE and COMPARE PRICE numbers with compare higher, SUPPLIER INFO
not empty and not cut, required headers present), plus checks 5 and 6 below (the attached photo
matches the text; no photo = build from the text). The manager cannot see the PC, so it never
checks `Desktop\apex-inbox\<row>\`: a missing folder stops only that product on the PC, with a clear
message in its STATUS.txt. The check table gets a Row column.

**Intake folders:** for each folder, in order, with the Google Drive connector (never download photos):
1. The folder exists in `APEX/_inbox/`.
2. `input.txt` read: `price:`, `compare price:` (must be higher than the price) and `store:` present,
   supplier text below; the store profile `APEX/_stores/<store>.md` exists.
3. `photos/` holds at least one .jpg / .jpeg / .png / .webp (a .heic alone does not count).
4. Not built already: no `BUILT.txt` / `DONE.txt` in the intake folder.
5. The attached photo for this position shows the product the text describes. Look at it: the
   type of product, its colour, its parts. Also cross-check the photo against the supplier text for
   contradictions (different model, features in the text that the photo does not show, a spec on
   the photo that the text contradicts). A small spec difference (IP55 vs IP65) is not a
   contradiction: note it, build with the safe wording. A different product, or core features in
   the text that the product clearly does not have, IS: skip.
6. No photo attached for this position (fewer photos than folders): build from the text, note
   "no photo seen" (the watcher still uses the Drive photos for the images).

Any failed check → that product is **skipped** with a one-line reason; the others are built. Never
stop the batch, never ask. Then send the user ONE check table (SendUserMessage) and start at once:

| # | Folder | Price / compare | Photo | Result |
|---|---|---|---|---|
| 1 | cordless-chopper | 2990 / 4490 | matches | build |
| 2 | led-torch | 1990 / 2990 | photo shows a different torch than the text | skipped |

Put one task per product in the task list.

## Step 2 — Build each product in its own helper (one at a time, in order)
Start one helper (Agent tool, general-purpose) per product, wait for it to finish, then start the
next. Never two at once (keeps the hand-off order, and the Drive writes never collide). The helper
brief, filled in per product:

```
You are building ONE product page with the PageEngine skill, start to finish, unattended.
Load the skill "page-engine" with the Skill tool (apex:page-engine) and follow it
exactly, all phases, all checks, the full delivery and the APEX v2 Google Drive hand-off.
Input (sheet mode): row <n> of the Google Sheet APEX Products: follow the skill's
references/sheet-mode.md (read the row with the Google Sheets connector, READY.txt with
photos_row: <n>, then BUILD -> DONE and the title cell green).
Input (intake folders): the Drive intake folder APEX/_inbox/<name>/ (read input.txt with the Google
Drive connector; never download photos). Store: <store>. Price: <price>. Compare price: <compare>.
Product photo: <path to the attached photo> (look at it with the Read tool).
[If no path exists: "Product photo, described by the manager: <careful description: product type,
colour, shape, parts, printed text, what is in the box>".]
Checks done by the manager: <notes, e.g. "IP55 in the text, IP65 on the photo: use rain resistant">.
Unattended rules: never ask the user anything; take the most reasonable reading and note it in the
build notes. The product name is the store's own, never the supplier's. Store facts come only from
the store profile; a missing profile = stop and report it.
Slug: before creating APEX/<slug>/, check it does not exist already for a different product
(a READY.txt there whose inbox: line names another folder); if it does, choose another slug.
Already used in this batch: <slugs so far>.
After READY.txt is uploaded: sheet mode = update the row (sheet-mode.md step 4); intake folders =
create BUILT.txt in APEX/_inbox/<name>/ with the text "built as <slug>".
Reply ONLY with this block:
SLUG: ... | NAME: ... | PRICE: ... / ... | ACCENT: name #hex | ANGLE: one line |
CHECKS: persuasion ..., voice ..., manifest OK (n images) | CONFIRM: items or none |
DRIVE: all sizes matched + READY.txt uploaded, or the problem | SHEET: DONE + title green, or what was skipped (sheet mode)
```

When a helper ends without `READY.txt uploaded`, mark that product failed with its reason and go on
with the next. The manager keeps only the reply blocks (never the page files) in its own context.

## Step 3 — The end
1. Wait about a minute, then read `APEX/<slug>/STATUS.txt` for every built product (the watcher
   writes it). A missing STATUS.txt = the watcher has not reached it yet (it works in hand-off order).
2. Send one summary table: # · name · slug · price / compare · angle · watcher status · [CONFIRM]
   items. Then the skipped products with their reason and what to fix.
3. Say that the rest runs by itself on the PC (Windows notifications as each product goes live) and
   that "APEX status" shows the live state of all of them later.

## Rules
- Quality does not drop in batch mode: every product gets every phase of the PageEngine skill, its own customer
  map, its own angles, its own accent. No copying of hooks, scenes or wording between products.
- Prices only from each product's own row (or input.txt); never taken from another product.
- In sheet mode only each product's own BUILD cell and title colour are written (by its helper), never
  anything else in the sheet.
- A skipped product is not half-built: nothing of it goes to `APEX/<slug>/`.
- "APEX status" (no slug): read STATUS.txt of every `APEX/<slug>/` changed in the last 2 days and
  show one line each.
