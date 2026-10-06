# Order Journey Badge — Color Palette Guide

The Order Journey Badge color adapts to each product's dominant palette. The **keypoint checkmarks always stay green** regardless of badge color.

## Quick mapping

| Product type | Banner background | Hex | Circle bg | Notes |
|---|---|---|---|---|
| Default / generic | Green | `#22c55e` | Same green | Safe fallback |
| Tech / security / cameras | Deep blue | `#1d4ed8` | Same blue | Conveys trust |
| Tools / hardware (orange product) | Orange | `#ea580c` | Same orange | Matches industrial tools |
| Tools / hardware (black + gold) | Slate | `#1e293b` | Slate + gold border | Premium tool look |
| Ocean / wellness / hydration | Teal | `#0d9488` | Same teal | Soft & natural |
| Supplements (beetroot / berry) | Burgundy | `#7c2d12` or `#9f1239` | Same burgundy | Wellness, earthy |
| Health / skincare | Soft teal | `#0d9488` | Same teal | Calming |
| Car accessories (black + teal) | Teal | `#0d9488` | Same teal | Modern car aesthetic |
| Cleaning products | Green | `#22c55e` | Same green | Fresh & clean |
| Pest control / botanical | Green | `#16a34a` | Same green | Natural |
| Mirror / beauty / luxury | Rose gold or dark | `#a78bfa` or `#1f2937` | Same | Elegant |

## How to choose for a new product

1. Look at the product's **primary color** in the images
2. Look at the **emotional category** (security → blue, wellness → teal/green, tools → orange/slate, luxury → dark)
3. Pick the closest match from the table above
4. If multiple fit, lean toward what reinforces the **selling angle**

## CSS variables to update

In the master template, only these three CSS variables change per product (assuming the prefix is `xx-`):

```css
--xx-accent: <HEX>;   /* The main badge color */
```

And the CSS rules that use it: `.xx-journey-banner`, `.xx-journey-circle` backgrounds.

The chevron arrows (`›`) stay grey (`#9ca3af`) by default but can shift to a darker shade of the accent for premium products (e.g. gold on slate).

## Examples by product type

- **Product with teal accents in the supplier photos** → teal `#0d9488` (match the product)
- **Security / smart-home gadget** → deep blue `#1d4ed8` (security/tech feel)
- **Black-and-gold tool** → slate `#1e293b` with gold accents (match the product)
- **Measuring or workshop tool** → orange `#ea580c` (typical industrial-tool orange)
- **Ocean / natural skincare** → teal `#0d9488`
- **Generic / unclear** → green `#22c55e` (safe default)
