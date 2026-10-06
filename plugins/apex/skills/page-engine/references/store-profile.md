# Store profile: the facts PageEngine never invents

APEX works for any store and any market. Everything that is true for one store and not for
another (brand name, brand colour, payment method, guarantee, delivery promise, market, language,
currency) lives in ONE store profile per store. PageEngine reads it in Phase 1 and uses it word for
word. It never guesses a store fact and never carries one store's facts over to another store.

## Where the profile lives
- Google Drive: `APEX/_stores/<store>.md`, where `<store>` is the store key (the same key as the
  `store:` line in `input.txt`, the `store` field in `<slug>-product.json` and the `.env.<store>`
  file the Image Factory logs in with).
- Without Drive: the user pastes the profile into the chat once, with the first build.
- One store only: the key `default` and `APEX/_stores/default.md`.

No profile found → stop before Phase 2 and ask the user to fill in the template below (one
message). Unattended (batch): skip the product with the reason "no store profile for <store>".

## The template (copy, fill in, save as `APEX/_stores/<store>.md`)

```
store: <store key, lowercase, e.g. mystore>
brand name: <the name customers see, e.g. Northwind>
brand colour: <hex for the brand bar, promise row and brand section, e.g. #0E6B5C>
market: <country, e.g. Kenya>
country code: <the code used in the APEX Products sheet's Country column, e.g. KEN>
market profile: <file in page-engine/references, e.g. market-example-kenya.md, or "none">
page language: <e.g. English, with local words from the language bank>
currency: <as written on the page, e.g. KSh>
payment: <how customers pay, e.g. cash on delivery only>
payment never: <methods never to mention, e.g. mobile money, card on the page; or "none">
check before paying: <yes / no: can the customer inspect the parcel before paying?>
guarantee: <the REAL policy in one line, e.g. 7 days to change your mind: we collect it, we pay the return, you get your cash back>
delivery line: <the accordion text, e.g. We deliver nationwide. Capital city: same or next day. Other towns: 1 to 4 business days.>
order steps: <the How To Order steps, e.g. Click order · fill in name, phone, address · choose cash on delivery · we call to confirm before dispatch>
cod closer: <the closer line under the guarantee, e.g. Free delivery and cash on delivery available nationwide>
free delivery: <yes / no>
support channel: <e.g. WhatsApp, phone, email>
regulator notes: <health / supplement / electrical rules for this market, or "see market profile">
```

## How each field is used
| Field | Where it goes |
|---|---|
| brand name | brand bar, brand section, gallery trust slide, image prompts that show the brand. Never the supplier's brand |
| brand colour | brand bar, promise row, brand section. Never changes with the product accent |
| market + market profile | the customer mind map's market, review voice, image casting and settings, local words |
| page language, currency | every line of copy, the price lines, the manifest `language` field |
| payment, payment never, check before paying | the journey badge, How To Order, the FAQ, the closer, every risk-reversal line |
| guarantee | Final CTA, FAQ, accordions, exit read. Written exactly as given, never improved |
| delivery line, order steps, cod closer | the three info accordions and the Final CTA (template tokens `<DELIVERY_INFO>`, `<ORDER_STEPS>`, `<GUARANTEE_LINE>`, `<COD_CLOSER>`) |
| free delivery | the journey badge banner text; "FREE DELIVERY" only when `yes` |
| regulator notes | Phase 2 compliance flags, on top of `compliance-rules.md` |

A field left empty is never filled with a guess: the copy that needs it is left out and listed in
the open items with `[CONFIRM]`.

## Market profiles
A market profile is the local flavour file the mind map, the reviews and the image prompts draw
on: places, everyday words, hooks, money habits, settings and people for the images. One ships as
an example (`market-example-kenya.md`). For a new market, write one in the same shape: places by
tier, everyday words with their meaning, local hooks and moments, money and buying habits, image
casting and settings, words to avoid.
