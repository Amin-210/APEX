# APEX: the whole system, from supplier text to a finished live page

APEX is the name of the complete workflow. The four steps keep their own names:

| Step | Name | Where | What the user does | What it does |
|---|---|---|---|---|
| 1 | **PageEngine** | claude.ai chat | "PageEngine for [product]" + supplier text + selling price + compare price; download the files | customer map, angles, copy, persuasion + voice checks, Liquid, review frames, image prompts, `<slug>-product.json` |
| 2 | **Product setup** | PowerShell: `.\new-product.ps1 <slug>` | run it | product (title, price, compare price, tax / inventory / shipping OFF, URL = slug, published), unique template (copy of the default product template, assigned), Claude Code prompt on the clipboard, VS Code opened |
| 3 | **Claude Code design** | Claude Code in VS Code | paste the prompt (Ctrl+V) | puts the PageEngine Liquid into the template (journey badge first, main product section, description), theme check, pushes live |
| 4 | **Image Factory** | PowerShell: `.\run-factory.ps1 <slug>` | run it | generates the images, uploads section images to Files and slides to the gallery, live check |

Fixed order: 1 → 2 → 3 → 4. Every step shows its output. Commands are PowerShell.

Files per product (Downloads): `<slug>-product.json`, `product-description-<slug>.liquid`,
`journey-badge.liquid`, `<slug>-images.json`, `<slug>-image-prompts.md`, `<slug>-review-frames.md`.
Photos: `Desktop\<slug>-photos` (1-3 supplier photos, including the one that shows all parts).

Folders: image factory = `IMAGE_FACTORY_DIR` (scripts, `.env`, `.env.<store>`, `incoming\<slug>\`,
`products\<slug>\`); theme = `THEME_DIR` (the folder Claude Code works in).

## APEX v2 (default): Google Drive + watcher
The chat saves the build to Google Drive `APEX/<slug>/` (READY.txt last). Google Drive for Desktop
syncs it to the PC; `apex-watch.ps1` (image-factory folder; starts with Windows after the one-time
`.\apex-watch.ps1 -Install`, minimized window "APEX watcher") runs, for every new folder:
A collect (files -> `incoming\<slug>\`, photos from Drive `_inbox\<name>\photos\` -> `Desktop\<slug>-photos`;
old way: `Desktop\apex-inbox`),
B image manifest (`build-image-manifest.py`), C product setup + page install by script
(`product_setup.py --install-page`: journey badge first, the sections above the buy button, the main
product section, the description; everything below the buy button left out; pushed live),
D Image Factory. State per product in `apex-state\<slug>.json`. Finished folders get DONE.txt in Drive.
Every stage's output: the watcher window, `apex-logs\<slug>.log`, and in Drive `APEX/<slug>/STATUS.txt`
+ `apex-log.txt` (the chat reads them). Nothing waits for a key: QuickEdit (a click in the window
pauses it until Enter) is switched off by the watcher.
What starts a run, all without PowerShell: a new folder with READY.txt (new); READY.txt uploaded
again with a new `rev: <n>` line after the chat saved changed files (revision: page text pushed again;
images kept when no image prompt changed, all made again when one changed); `RETRY.txt` in the folder
(retry after a fix; the chat creates it on "APEX retry <slug>"); a run cut off by a restart (resume).
The user's only steps: fill the intake folder, then one chat line with 1-2 photos attached.

## APEX sheet mode (the default input)
A product research sheet named **APEX Products** (Google Sheet, My Drive top level): one row per product.
For a build the user fills PRICE, COMPARE PRICE (in the store's currency) and SUPPLIER INFO, sets BUILD = GO,
saves the full-size photos into `Desktop\apex-inbox\<row>\` on the PC (1.jpg = the clearest) and
writes `PageEngine for row <row>` with 1-2 photos attached (page notes go in that chat message).
READY.txt then carries `photos_row: <row>`; the watcher takes the photos from that folder. After the
hand-off PageEngine sets BUILD = DONE and colours the row's title cell green. No thumbnails. Full
rules: `references/sheet-mode.md`.

## APEX intake (Google Drive, the backup input)
```
APEX/_inbox/<name>/          <name>: lowercase, hyphens, letters and numbers only, new per product
  input.txt                  price: 2990 / compare price: 4490 / store: mystore, then the supplier text
  photos/1.jpg, 2.jpg ...    clean product photos (.jpg .png .webp; no .heic), clearest first
  extra/...                  optional: collages, infographics (PageEngine context only)
```
Chat: `PageEngine for _inbox/<name>` + 1-2 photos attached (PageEngine never downloads photos from
Drive: the connector returns whole files as text, far too large). The build folder `APEX/<slug>/`
gets READY.txt with `inbox: <name>`; the watcher copies the photos from the intake folder (the Drive
folder keeps them) and writes DONE.txt into both folders. Folders starting with `_` are never builds.
APEX v1 (download + new-product.ps1 + Claude Code + run-factory.ps1) stays as the fallback.

## Store profiles
```
APEX/_stores/<store>.md      one per store: brand, colour, market, payment, guarantee, delivery
```
Every build reads the profile of its `store:` key first. Template and rules:
`references/store-profile.md`.
