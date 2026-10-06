---
name: image-factory
description: Runs the Image Factory - the automated workflow that turns the page-engine output (the slug-images.json and the image prompts .md) into finished product images live on the Shopify product page - set up the product folder, preflight (photos, OpenAI key, Shopify login, product handle), generate every image with the OpenAI Images API using the real product photo, then upload straight away with no review stop (section images to Shopify Files so the page fills itself, catalog slides to the product gallery in order) and verify the live page, showing the user the output of every stage. Use WHENEVER the user says "Image Factory", "Image Factory for [product]", "make / generate / create the images for [product]", "upload the images", "put the images on the page", or finishes a page-engine build and wants the images. Works for any product, niche and store. Needs a terminal on the user's machine (Claude Code); in a chat without one, give the user the commands instead.
---

> **APEX, step 4 of 4.** The Image Factory is the last step of APEX: 1 PageEngine → 2 Product setup (`new-product.ps1`, ships with this skill) → 3 Claude Code design → 4 Image Factory. Overview: page-engine `references/apex.md`.


# Image Factory

One workflow from the page-engine output to images live on the product page. The engine is
`factory.py` in the image-factory folder; this skill runs it, shows the output of every stage, and
handles errors. Every step is safe to repeat: finished images are not generated again and
unchanged images are not uploaded again.

## 0. Where things are
- **What ships with this skill** (copy all of it into one folder once, that folder is
  `IMAGE_FACTORY_DIR`): `factory.py` (the engine: set up, preflight, generate, upload, live check),
  `product_setup.py` (it also holds the Shopify login code `factory.py` uses, keep them together),
  `run-factory.ps1`, `new-product.ps1`, `apex-watch.ps1`, `apex_watch.py`, `build-image-manifest.py`,
  `journey-badge.liquid` and `.env.example`. Python 3.9+ with no extra packages.
- **Terminal:** the user works in **PowerShell**. Always give PowerShell syntax: `cd $env:IMAGE_FACTORY_DIR`,
  never CMD's `cd /d %IMAGE_FACTORY_DIR%` (PowerShell rejects it with "A positional parameter cannot be found").
- **Image factory folder:** the `IMAGE_FACTORY_DIR` environment variable. If it is not set, ask the
  user once for the folder that contains `factory.py`, and tell them to run
  `setx IMAGE_FACTORY_DIR "<that folder>"` so it is found next time.
- **Python:** `py` on Windows (fall back to `python` if `py` is missing).
- **The helper `run-factory.ps1`** (ships with this skill, lives in the image factory folder) does the
  file hunting: it takes the newest `<slug>-images*.json` and `<slug>-image-prompts*.md` from Downloads,
  Desktop or Documents (repeat downloads named `... (1).json` included), copies them with clean names
  into `incoming\<slug>\`, finds the photos in `Desktop\<slug>-photos` or `Desktop\<first word>-photos`,
  switches off stray `SHOPIFY_` lines in `.env` (backup `.env.bak`, see the table), then generates and
  uploads. If the product folder already exists, it just continues.
- **Product photos:** 1-3 sharp photos, product clearly visible, daylight, including the supplier photo
  that shows all the parts. Prompts never need an extra photo per image.
- Never print, read aloud or edit `.env` / `.env.<store>` values; they hold secrets. Diagnose with
  commands that print setting NAMES only (see the table).

## Before the images: product setup and page design (new product)
Fixed order for a NEW product: PageEngine -> `.\new-product.ps1 <slug>` -> Claude Code in VS Code
designs the page -> `.\run-factory.ps1 <slug>`. Only start the images once the page is designed and
live, so the live check finds the image slots.

`new-product.ps1` (ships with this skill, lives in the image factory folder next to
`product_setup.py`) reads `<slug>-product.json` from page-engine and creates the product (URL handle =
slug, active, price and compare-at price from the user, charge tax OFF, track inventory OFF, physical
product / shipping OFF, published to the
Online Store; an existing product with that handle is reused, never duplicated), creates
`templates/product.<slug>.json` as a copy of the live default product template, pushes it with
Shopify CLI and assigns it. It does not design the page: it writes the Claude Code prompt, copies it
to the clipboard and opens VS Code on the theme folder. Stages are printed 1/7 to 7/7; `-DryRun`
checks only. Full reference and its error table: page-engine `references/pre-build-setup.md`.

## APEX v2: the watcher (default for new products)
`apex-watch.ps1` + `apex_watch.py` (ship with this skill, with `build-image-manifest.py` and
`journey-badge.liquid`) watch the Google Drive folder `APEX\` synced by Google Drive for Desktop
(found automatically under "My Drive" / "Meine Ablage"; or `setx APEX_DRIVE_DIR "<path>"`). For each
new `<slug>` folder with READY.txt they run: A collect (sheet mode: READY.txt's `photos_row: <n>` line →
the photos are moved from `Desktop\apex-inbox\<n>\`; intake mode: photos from Drive `_inbox\<name>\photos\` named on
READY.txt's `inbox:` line, copied not moved; `extra\` ignored; old way: loose photos in `Desktop\apex-inbox`),
B image manifest, C `product_setup.py --install-page` (product + template + page installed by script,
no Claude Code), D `run-factory.ps1`. Every stage prints in the window, goes to `apex-logs\<slug>.log`
and to Drive `APEX\<slug>\STATUS.txt` + `apex-log.txt`; state in `apex-state\<slug>.json`.
Runs start by themselves: new folder with READY.txt; READY.txt changed (new `rev: <n>` line from the
chat after changed files: page pushed again, images kept unless an image prompt changed, then the old
`products\<slug>` is renamed `<slug>-old-<time>` and every image is made again); `RETRY.txt` in the
folder; a run cut off by a restart resumes (at most twice). Only one watcher runs per PC; QuickEdit is
switched off so a click in the window never pauses a run; a Windows notification shows start, done
and stop.
```
.\apex-watch.ps1 -Install        # ONE TIME: start with Windows (minimized "APEX watcher"), starts now too
.\apex-watch.ps1 -Uninstall      # stop starting with Windows
.\apex-watch.ps1                 # watch in this window
.\apex-watch.ps1 -Once           # check once
.\apex-watch.ps1 -Retry <slug>   # run again (hands it to the running watcher; same as RETRY.txt)
```
| Message | Fix |
|---|---|
| Google Drive folder 'APEX' not found | install Google Drive for Desktop, sign in with the same Google account as the claude.ai Drive connector, let it sync; or `setx APEX_DRIVE_DIR "G:\My Drive\APEX"` |
| still syncing, missing: ... | wait, Google Drive is still copying; the watcher tries again by itself |
| no product photos | sheet mode: put 1-3 photos (.jpg/.png/.webp) into `Desktop\apex-inbox\<row>\` (the product's row number in APEX Products); intake mode: put them in `_inbox\<name>\photos\` in Drive (or `Desktop\apex-inbox` without an intake folder), then RETRY.txt in `APEX\<slug>\` (or `-Retry <slug>`) |
| skipped (not .jpg/.png/.webp) | iPhone .heic photos: export them as JPG into the same folder, then RETRY.txt if no photo was left |
| still syncing, missing: the intake folder | Google Drive is still copying `_inbox\<name>`; the watcher tries again by itself |
| run cut off (window closed, PC restarted) | resumes by itself when the watcher starts again (at most twice, then RETRY.txt) |
| "fixed N {# #} note(s)" (yellow) | the page had `{# ... #}` notes, which Shopify prints as visible text; the watcher (and product_setup.py) turned them into `{% comment %}` tags before the push. Nothing to do |
| paused after `shopify theme push` until Enter | old product_setup.py: the CLI asked "not a theme directory, proceed?" invisibly; the current one runs the CLI with SHOPIFY_FLAG_FORCE=1 and no keyboard, so it never waits |
| window paused, title starts with "Select" | an old watcher without the QuickEdit fix: press Esc; update apex_watch.py |

## One-time setup per PC
1. Put `run-factory.ps1` in the image factory folder (exactly this name, not `run-factory (1).ps1`).
2. In PowerShell, in that folder: `Unblock-File .\run-factory.ps1` and
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (answer Y).
3. For `new-product.ps1`: `Unblock-File .\new-product.ps1`; Shopify CLI installed and logged in once
   (`shopify theme list --store <shop>.myshopify.com`); `setx THEME_DIR "<local theme folder>"`; the
   store app also has `write_inventory`, `read_inventory`, `write_publications`, `read_publications`.
4. `.env` holds only the OpenAI key and the image settings. Each store's Shopify login lives ONLY in
   `.env.<store>` (e.g. `.env.mystore`, one per store key). Copying `.env.example` to `.env` brings Shopify lines
   along; they must stay commented out (`# SHOPIFY_...`).

## 1. Generate, then upload directly (no review stop)
Runs after the page is designed and live (see above).
The user wants the images live without a review step, and wants to SEE the output of every stage.
Run the two documented commands back to back from the image factory folder:
```
py factory.py <path>/<slug>-images.json --photos <photos folder> --no-upload
py factory.py <slug> --yes
```
(For a product already set up, the first line is `py factory.py <slug> --no-upload`.)
The second command runs only when the first one finished without an error. With the helper script
`run-factory.ps1` in the image factory folder, both run with one command: `.\run-factory.ps1 <slug>`
(`-NoUpload` stops after generating).

The first command sets up `products/<slug>/`, runs the preflight and generates. The second uploads the
section images to Content > Files as `<slug>_<image_id>.png` (the page finds them by that name,
nothing to change in the theme), replaces the product gallery with the slides in order (the old
gallery media stay in Content > Files) and checks the live page.

If the preflight stops, fix what it names (see the table below) and run the same command again. If
images fail, run the same command again once; if the same image fails twice, report its error.
Every step is safe to repeat.

If the user asked for a cheap prompt check, use `--test` instead (all at low quality into
`products/<slug>/test/`, no upload, the real images untouched). `--only id,id` limits any run to those
images; `--text none` asks for images without rendered text (Arabic or other scripts the model
garbles: add the captions in Canva); real-photo slides put in `products/<slug>/real/<image id>.jpg`
are uploaded into the gallery in their slide position.

## 2. Show the output of every stage (no approval gate)
Do not stop to review or to ask before uploading. Show the user, stage by stage, what the terminal
printed: set up, preflight, the image list with each image's status, the upload lines, and the live
check line ("N/M section images showing"). Then list the real photos still to add by hand (e.g. the
storefront or doorstep slide, the customer photos in the review cards).

If the user later points at an image they do not like, regenerate and re-upload just that one
(it costs money, so only on their request):
```
py factory.py <slug> --no-upload --redo image_x,slide_image_y
py factory.py <slug> --yes
```
When a bad image comes from the prompt itself (wrong caption, product drawn wrong, rival looks like
the product), propose the prompt change in the page-engine files and the lesson for
`references/infografic-style.md`.

## When the preflight or the upload stops
| Message | Fix |
|---|---|
| no product photo in reference/ | ask for photos, run again with `--photos <folder>` |
| OPENAI_API_KEY missing | the user adds it to `.env` in the image factory folder (never do it for them) |
| SHOPIFY_SHOP is not set / token request failed | the user creates `.env.<store>` with SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET of the Dev Dashboard app installed on that store (scopes write_files, read_files, write_products, read_products) |
| the app is missing permission(s) | Dev Dashboard → the app → Versions: add the named scopes, release, approve the update on the store |
| N image(s) failed | run the same command again (only the failed ones are made); the same image failing twice: show its error line and fix that prompt |
| shop_not_permitted | the app and the store are not in the same Dev Dashboard organization |
| no product with URL handle '<slug>' | the product must exist with URL handle = slug (or run with `--handle <its handle>`) |
| live check shows fewer images than uploaded | wait a minute (Shopify is still processing) and run the upload again; if it stays, the page section has no self-filling slot for those images: rebuild the section with PageEngine (a `rev:` change) and run the upload again |
| `FileNotFoundError ... <slug>-images.json` | the file was never downloaded or got another name; the helper finds renamed copies, otherwise the user downloads both files from the chat into Downloads |
| `A positional parameter cannot be found ... %IMAGE_FACTORY_DIR%` | CMD syntax in PowerShell: use `cd $env:IMAGE_FACTORY_DIR` |
| `run-factory.ps1 cannot be loaded ... running scripts is disabled` | run the one-time setup: `Unblock-File .\run-factory.ps1` and `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Shopify `GraphQL HTTP 401 ... Invalid API key or access token`, although `.env.<store>` is correct | `.env` contains active `SHOPIFY_` lines (usually after copying `.env.example`) that override `.env.<store>`. The helper comments them out automatically (backup `.env.bak`); by hand: `(Get-Content .env) -replace '^SHOPIFY_', '# SHOPIFY_' \| Set-Content .env`. To check without showing secrets, list only the setting names: `foreach ($f in '.env','.env.mystore') { "--- $f"; Get-Content $f \| ForEach-Object { ($_ -split '=',2)[0] } }` |
| insufficient_quota / 401 from OpenAI | the user adds credit / fixes the key on platform.openai.com |

## Settings (in `.env`, read automatically)
`IMAGE_MODEL` (default gpt-image-2.5-sunburst; gpt-image-2.5-flare costs the same and is faster),
`IMAGE_QUALITY` (the user's default, e.g. medium). The key images `image_hero` and `slide_image_01`
are made at high (`--key-quality` to change).

## In a chat without a terminal
Give the user the PowerShell steps: `cd $env:IMAGE_FACTORY_DIR`, then `.\run-factory.ps1 <slug>` (the
one-time setup first, if the helper is new on that PC). They paste screenshots of the output; explain
each stage and fix any stop with the table above.
