# APEX: supplier text to a live Shopify product page

APEX is a Claude plugin for Shopify cash-on-delivery stores. You give it a product (supplier text,
a selling price, a compare-at price and a photo); it builds the whole product page and, with the
optional PC side, puts it live with its images.

```
1 PageEngine        customer mind map → angles → copy → persuasion check → voice check
                    → Liquid sections, review frames, image prompts, launch manifest
2 Product setup     creates the Shopify product and its own template
3 Page design       installs the page into the template and pushes it live
4 Image Factory     generates the images and fills the page and the gallery
```

Steps 2 to 4 can run by themselves: the chat saves each build to Google Drive, and a watcher on
your PC picks it up.

## Skills in the plugin

| Skill | What it does |
|---|---|
| `page-engine` | The build engine: one product from supplier text to the full page package |
| `apex-batch` | Several products in one command, each built by its own helper |
| `customer-mind-map` | The psychological map of the buyer that every line of copy comes from |
| `persuasion-check` | Audits the copy as one persuasion arc (12 tests, hard fails block the build) |
| `copy-voice-check` | Rewrites weak lines sentence by sentence, never the structure |
| `infografic-style` | The look and the prompt skeleton for every product image |
| `image-factory` | Product setup, page install, image generation and upload, and the Drive watcher |

## Install

**Claude Code**
```
claude plugin marketplace add <your-github-name>/<this-repo>
claude plugin install apex@apex-marketplace
```

**claude.ai (web / desktop)**: zip each folder in `plugins/apex/skills/` and upload it under
Customize → Skills → + → Create skill → Upload a skill. Code execution and file creation must be on.

## Set up your store (once per store)

APEX never invents store facts. Copy the template in
`plugins/apex/skills/page-engine/references/store-profile.md`, fill it in (brand name, brand
colour, market, language, currency, payment, guarantee, delivery line, order steps) and save it as
`APEX/_stores/<store>.md` in Google Drive, or paste it into the chat with your first build.

Each store also points to a **market profile** (local places, everyday words, moments, image
casting). One example ships with the plugin (`market-example-kenya.md`); write one in the same
shape for each market you sell in.

## Use it

- `PageEngine for row 12`: build from row 12 of a Google Sheet named **APEX Products**
  (columns: NAME, Country, PRICE, COMPARE PRICE, SUPPLIER INFO, BUILD; see `sheet-mode.md`).
- `PageEngine for _inbox/<name>`: build from a Drive folder `APEX/_inbox/<name>/` holding
  `input.txt` (`price:`, `compare price:`, `store:`, then the supplier text) and `photos/`.
- Or paste the supplier text, both prices and the store key straight into the chat.
- `PageEngine batch` / `PageEngine for rows 5, 8, 12`: several products in one go.

Needs the Google Drive connector (and Google Sheets for sheet mode) in the chat.

## The PC side (optional, Windows / PowerShell)

The `image-factory` skill ships everything that runs steps 2 to 4: `factory.py` (the image
engine), `product_setup.py`, `new-product.ps1`, `run-factory.ps1`, `apex-watch.ps1`,
`apex_watch.py`, `build-image-manifest.py`, `journey-badge.liquid` and `.env.example`. Python 3.9+,
no extra packages. Copy them all into one folder, then:

```
setx IMAGE_FACTORY_DIR "<that folder>"
setx THEME_DIR "<your local theme folder>"
.\apex-watch.ps1 -Install     # one time: the watcher starts with Windows
```

You also need Google Drive for Desktop (same Google account as the chat), Shopify CLI logged in
to your store, a `.env.<store>` file with your Shopify app login (Dev Dashboard app with
`write_products`, `read_products`, `write_files`, `read_files`, `write_inventory`, `read_inventory`,
`write_publications`, `read_publications`), and an `.env` with your OpenAI key (copy `.env.example`).

The image engine on its own:
```
py factory.py <slug>-images.json --photos <folder> --no-upload   # set up + generate
py factory.py <slug> --yes                                       # upload + live check
py factory.py <slug> --test                                      # cheap low-quality check
py factory.py <slug> --no-upload --redo image_hero               # make one image again
```
Images are made with the OpenAI Images API (`IMAGE_MODEL`, default `gpt-image-2.5-sunburst`), each
with the product photo attached. Section images go to Content > Files as `<slug>_<image_id>.png`,
where the page finds them by name; catalog slides replace the product gallery in order.

## Rules APEX keeps

- No invented reviews, counts, ratings, urgency or authority. Social proof comes from real customers.
- No disease, weight-loss-number or sexual claims; supplement and skincare copy uses safe verbs.
- Store facts (guarantee, payment, delivery) come from the store profile, word for word.
- Secrets in `.env` files are never printed, read aloud or edited.
