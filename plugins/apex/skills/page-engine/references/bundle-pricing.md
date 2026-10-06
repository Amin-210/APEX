# Bundle Pricing (Optional Upgrade)

This is an optional pricing pattern observed on a competitor's COD product page. Use only when the product is **consumable** (supplement, refill, cream) or **gift-worthy** (small accessory people buy multiples of).

## The pattern

Instead of one price, offer **3 quantity tiers** with increasing discounts. Pre-select the middle option as "Best Seller".

| Quantity | Price example | Crossed anchor | Save % | Badge |
|---|---|---|---|---|
| 1 box | 1,990 | (no anchor) | — | — |
| 2 boxes | 2,890 | 3,980 | 27% | ⭐ Best Seller (pre-selected) |
| 3 boxes | 3,490 | 5,970 | 41% | 🔥 Best Value |

## Why it works

- **Anchoring** — the single-box price makes the 2-box deal look like value
- **Pre-selected default** — most people don't change defaults
- **Two badges** — "Best Seller" feels safe and social-proof; "Best Value" appeals to the optimizer
- **Pushes average order value (AOV)** — instead of 1 unit you sell 2-3 per order
- **Especially powerful for consumables** — the customer knows they'll use it up

## When to use

✅ Good fit:
- Supplements (capsule bottles)
- Skincare creams
- Refill packs (toilet wand refills, mosquito balls)
- Small gift items
- Multi-pack accessories (lighters, USB cables, hooks)

❌ Skip:
- Big single-use items (mirror, scrubber, camera, fan)
- Tools the customer only needs one of
- High-ticket products where 2-3x feels excessive

## Implementation note

The product description Liquid file does NOT handle bundle pricing — that's done at the **theme / product variant level** in Shopify, or via a COD bundle app (DCOD, EasyOrders, etc.). What the description CAN do is **promote** the bundle visually with a callout near the top:

```html
<div class="<PREFIX>-bundle-callout">
  <p><strong>💡 Most customers buy 2-3 bottles</strong> — save up to 41% with multi-pack pricing above ↑</p>
</div>
```

Style it as a soft-colored highlight box pointing back up to the variant selector.

## Trust badges placement (also from the same analysis)

That competitor stacks 3 trust badges high on the page in a red callout:
- Free shipping nationwide
- Pay on delivery
- 14-day guarantee

This is essentially the same "trust trio" we use at the bottom, just moved higher. Worth experimenting with **also placing a compact version higher on the page**, between the hook and keypoints, for higher early-page reassurance.

## What NOT to copy from that competitor

Their page also features a **fake doctor figure** in a white coat endorsing the supplement. This is a high-severity compliance violation (see `compliance-rules.md`). Do not replicate this regardless of how much it might lift conversion — it's exactly the kind of thing Meta/TikTok ad reviewers flag and consumer-protection rules disallow.
