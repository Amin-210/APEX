# APEX step 2, Product setup: the product and its unique template (after the build)

**The order of the whole flow (fixed):**
1. **PageEngine** builds the page and delivers the files (this skill).
2. **Product setup** (`.\new-product.ps1 <slug>`) creates the product and its unique template and
   assigns it. It does NOT design the page.
3. **Claude Code in VS Code** designs the page: it puts the PageEngine Liquid into that template
   (prompt written by the setup, already on the clipboard, VS Code opened on the theme folder).
4. **Image Factory** (`.\run-factory.ps1 <slug>`) makes the images and uploads them.

There is no setup before the build. What used to be done by hand in step 2 (create the product, title
and price, untick tax and inventory, URL = slug, create a unique template based on product, assign
it) is done by `new-product.ps1` + `product_setup.py` in the image-factory folder (both ship with
the image-factory skill).

## The launch manifest: `<slug>-product.json` (Claude writes it in every Phase 6 delivery)

```json
{
  "store": "mystore",
  "title": "Swift Cordless Chopper",
  "slug": "swift-chopper",
  "template_suffix": "swift-chopper",
  "currency": "KSh",
  "language": "en",
  "price": "2990.00",
  "compare_at_price": "4490.00",
  "status": "ACTIVE",
  "prefix": "sc",
  "description_section": "product-description-swift-chopper",
  "journey_badge": { "banner_text": "FREE DELIVERY", "circle_color": "#E8590C", "banner_color": "#C2410C" }
}
```
- `store` = the store key: the `.env.<store>` file to log in with and the store profile `APEX/_stores/<store>.md`.
- `currency`, `language` = the store profile's currency and page language code (`en`, `sw`, `ar`, `fr` ...).
- `title` = the product's OWN name (never the supplier's), `price` = the confirmed selling price.
- `compare_at_price` = the compare price the user gave with the selling price (required, higher than `price`). Never invent or calculate it; if the user did not give one, ask.
- `prefix` = the page's 2-letter class prefix (the live check looks for `<prefix>-page`).
- `journey_badge` colours = the page accent and its dark shade (same hexes as the CSS).

## What the user runs (PowerShell, image-factory folder)

```
.\new-product.ps1 <slug>            # product + unique template, Claude Code prompt on the clipboard
.\new-product.ps1 <slug> -DryRun    # check only, change nothing
.\new-product.ps1 <slug> -ProductOnly  # only update price, compare-at, tax, inventory, shipping
```
It takes the newest `<slug>-product.json`, `product-description-<slug>.liquid` and
`journey-badge.liquid` from Downloads / Desktop / Documents and prints every stage:

1. **READ** the manifest (and notes which Liquid files are there for Claude Code).
2. **PREFLIGHT** Shopify login from `.env.<store>`, app permissions, Shopify CLI, theme folder.
3. **PRODUCT** create it (title, URL handle = slug, active), price, compare-at price,
   **charge tax OFF, track inventory OFF, physical product / shipping OFF**. An existing product with that handle is reused, never
   duplicated.
4. **SALES CHANNEL** publish it to the Online Store.
5. **TEMPLATE** pull the live theme's `templates/product.json` and create
   `templates/product.<slug>.json` as a copy of it (= "Create template, based on product"). An
   existing template is never overwritten. Lists the sections in it.
6. **PUSH + ASSIGN** push the template to the live theme with Shopify CLI, then assign it to the
   product.
7. **HAND-OFF** check the live page answers, write `incoming\<slug>\claude-code-prompt.md`, copy it to
   the clipboard and open VS Code on the theme folder.

The Claude Code prompt tells Claude Code to: copy the description section (and the journey badge
only if missing) into `sections/`; keep only the main product section in the template; add the
journey badge first with the page's colours and the description right after the main section; run
theme check without changing the copy; push only those files live; show the template before and after.

Theme files go through Shopify CLI because the Admin API only writes theme files with a special
Shopify exemption.

## One-time setup (per PC / per store)
1. Put `new-product.ps1` and `product_setup.py` in the image-factory folder; `Unblock-File .\\new-product.ps1`.
2. App permissions (Dev Dashboard -> app -> Versions -> new version -> release -> approve on the
   store): `write_products`, `read_products`, `write_inventory`, `read_inventory`,
   `write_publications`, `read_publications` (plus the image factory's `write_files`, `read_files`).
3. Shopify CLI installed (`npm install -g @shopify/cli`) and logged in once
   (`shopify theme list --store <shop>.myshopify.com`).
4. `THEME_DIR` = the local theme folder Claude Code works in: `setx THEME_DIR "C:\path\to\theme"`, then a new PowerShell
   window. No local copy yet: `shopify theme pull --live --store <shop>.myshopify.com --path <folder>`.

## When it stops
| Message | Fix |
|---|---|
| missing `<slug>-product.json` / description `.liquid` | download it from the chat into Downloads |
| no compare_at_price / must be higher than the price | the manifest needs the compare price the user gave; ask the user, rebuild the manifest |
| the app is missing permission(s) | add the scopes above in a new app version, release, approve on the store |
| Shopify CLI not found | `npm install -g @shopify/cli` |
| THEME_DIR is not set / not a theme folder | set it (step 4 above) or pull the theme once |
| Shopify CLI pull/push failed | log in once: `shopify theme list --store <shop>.myshopify.com`, run again |
| token request failed / 401 | `.env.<store>` login; stray `SHOPIFY_` lines in `.env` (see image-factory) |
| live page not reachable yet | Shopify cache, open the live link after a minute |
| VS Code did not open | the `code` command is missing: VS Code -> Ctrl+Shift+P -> "Shell Command: Install 'code' command in PATH"; the prompt is on the clipboard anyway |
