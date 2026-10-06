# Sheet mode: the product row in APEX Products (the default input)

The user keeps the product research in the Google Sheet **APEX Products** (My Drive, top level).
One row = one product. PageEngine reads the row instead of an `_inbox` folder. `_inbox` stays as
the backup way in (Phase 1 in SKILL.md).

## The command
- `PageEngine for row <n>`: the product in sheet row `<n>` (the row number at the left of the sheet).
- `PageEngine for <name>`: find the row whose title (the NAME cell, or PRODUCT BRAND when NAME is empty) contains `<name>` (case-insensitive). One match →
  use it. Several → list them (row, NAME) and ask which. None → say so in one line.

## Tools
The **Google Sheets connector** (`get_spreadsheet`, `get_values`, `update_values`,
`update_formulas`) reads and writes single cells with their full text. Never read the sheet with
Drive `read_file_content`: on a large sheet it returns a sample of the rows and cuts cells after
about 80 characters. Without the Sheets connector: say that it must be turned on in this chat, or
offer the `_inbox` way.

## Step 1: find and read the row
1. Drive `search_files`: `title = 'APEX Products' and mimeType = 'application/vnd.google-apps.spreadsheet'`.
   Not found → say so and stop.
2. `get_spreadsheet` with `fields: ["sheets.properties"]` → the first tab's title and its `sheetId`.
3. `get_values '<tab>'!1:1` → the headers. Find every column BY HEADER NAME (trim spaces, ignore
   case), never by letter: the user may move columns.

   | Header | Required | Use |
   |---|---|---|
   | NAME | yes | the research name, only to find the row; never the page name. The row's title cell = NAME, or PRODUCT BRAND when NAME is empty (the user often types the title there) |
   | PRODUCT BRAND | no | the supplier's or competitor's brand: NEVER on the page, in any file or image |
   | IMAGE | no | the user's own picture: never read, never written |
   | productLINK (or ALIBABA-LINK) | no | context only; may be tried with WebFetch, never relied on |
   | Country | yes | a store profile's `country code` (e.g. `KEN`) |
   | STORE | no | the store key; needed only when two store profiles share one country code |
   | PRICE | yes | selling price in the store's currency |
   | COMPARE PRICE | yes | compare-at price in the store's currency |
   | SUPPLIER INFO | yes | the supplier text (what input.txt held) |
   | BUILD | yes | `GO` = build it; `DONE` = built |

   A required header missing → stop and name it. All other columns are the user's research:
   ignore them. There is no PAGE NOTES column: page notes come in the chat message
   with the command (e.g. "PageEngine for row 33, don't mention the plug") and are binding facts.
4. `get_values '<tab>'!A<n>:<last column><n>` → the row, every cell complete.

## Step 2: checks (stop on the first failure, say what to fix, never guess)
- **Country** must match exactly one store profile's `country code` (`APEX/_stores/*.md`, or the STORE
  column when two profiles share a code). No match → "Row <n>: no store profile for country <code>." Empty → ask.
- **BUILD** must be `GO`. `DONE` → "Row <n> is already built (BUILD = DONE). Set it back to GO to
  build it again." Empty → "Set BUILD to GO in row <n> first."
- **PRICE** and **COMPARE PRICE**: both present; strip the currency sign or code, commas and spaces; both must
  be numbers; COMPARE PRICE higher than PRICE. Never invent, round or calculate either.
- **SUPPLIER INFO** not empty. Show in the chat, before building, one line:
  `SUPPLIER INFO: <characters> characters, <lines> lines, last line: "<last line>"`
  If it ends with `...` or `…`, stop: the text looks cut; ask the user to paste the full text into
  the cell.
- **Photos in the chat:** the 1-2 photos the user attached, as always. None → build from the text
  and say so in one line.

Then build as always (Phase 2 onwards), with that store's key, profile and currency.

## Step 3: hand-off (APEX v2, SKILL.md) with two changes
- READY.txt has NO `inbox:` line. It gets these two lines instead:
  ```
  photos_row: <n>
  sheet_row: <n>
  ```
  The watcher then takes the full-size photos from `Desktop\apex-inbox\<n>\` on the PC.
- In "APEX: next steps" remind the user, only if they have not said it is done: the full-size photos
  go into `Desktop\apex-inbox\<n>\` (1.jpg = the clearest photo, 1-3 photos, .jpg/.png/.webp), one
  folder per row.

## Step 4: after READY.txt is uploaded, update the row
1. Re-read the row's title cell (NAME, or PRODUCT BRAND when NAME is empty) and compare it with
   step 1 (rows move when the user sorts or inserts). Different → search for it; not found → skip
   this step and say in one line that the row moved.
2. **BUILD → DONE:** `update_values '<tab>'!<BUILD column><n>` with `[["DONE"]]`.
3. **Title green:** colour the title cell's background green (#00B050) with `update_spreadsheet`:
   `{"repeatCell": {"range": {"sheetId": <sheetId>, "startRowIndex": <n-1>, "endRowIndex": <n>,
   "startColumnIndex": <title col, 0-based>, "endColumnIndex": <title col + 1>}, "cell":
   {"userEnteredFormat": {"backgroundColor": {"red": 0, "green": 0.6902, "blue": 0.3137}}},
   "fields": "userEnteredFormat.backgroundColor"}}`. Only the background, never the text.
4. No thumbnail: the IMAGE cell is the user's; never upload a picture or write a formula there.
5. One line in the delivery: `Sheet: row <n> → BUILD = DONE, title green`.

## Rules
- Only two things of the product's own row are ever written: the BUILD cell (DONE) and the title
  cell's background (green). Never another cell, row, column, header, format or dropdown.
- Prices only from this row. PRODUCT BRAND and NAME never appear on the page (our own name only).
- Changes after the hand-off (`rev:`) and "APEX retry" work exactly as in SKILL.md; the sheet is not
  touched again.
