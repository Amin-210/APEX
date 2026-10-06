# Compliance Rules — What to Refuse and Rewrite

These rules protect against three things:
1. **Refunds and COD rejections** when the product doesn't deliver what the page promises
2. **Ad-platform bans** from Meta (Facebook/Instagram), TikTok, Google
3. **Legal trouble** under the market's health-product regulator and consumer protection law (store profile `regulator notes`)

## 🚫 REFUSE these requests (high severity)

### Weight loss with specific numbers
- ❌ "Lose 6kg in 30 days"
- ❌ "Drop 2 dress sizes guaranteed"
- ❌ "Burn 500 calories per session"
- ✅ Alternative: "Supports a slimming lifestyle alongside healthy eating and exercise" (and only on actual supplements that are legal)

### Sexual performance / ED
- ❌ "Increases stamina in bed"
- ❌ "Penis enlargement"
- ❌ "Cures premature ejaculation"
- ✅ For relevant supplements: focus on "athletic performance, daily energy, circulation" — not bedroom claims

### Disease cure claims
- ❌ "Cures eczema / psoriasis / acne"
- ❌ "Treats diabetes / arthritis / cancer"
- ❌ "Eliminates eczema permanently"
- ✅ Use FDA-safe verbs: **soothes, supports, helps with, calms, relieves, nourishes, promotes**
- ✅ Example: "Soothes irritation and supports the skin barrier"

### Authority misuse
- ❌ Fake doctor in a white coat endorsing a supplement
- ❌ "Doctor recommended" without an actual doctor
- ❌ Celebrity / athlete photos without licensing
- ✅ Use a REAL customer count ("trusted by [real number]+ customers") or real testimonials

### Branded IP
- ❌ Apple, Disney, Marvel, NBA, Premier League logos
- ❌ Specific named athletes/celebrities
- ❌ "Find My"-branded copy on a non-Apple tracker (use "compatible with iPhone Find My network" if technically true)
- ✅ Generic product names: "WiFi Light Bulb Security Camera" not "Ring-style Bulb Cam"

### Minors and sexual/harmful content
- Absolutely refuse anything sexualizing minors or facilitating harm to minors

## ⚠️ REWRITE these patterns (medium severity)

| Don't say | Do say |
|---|---|
| "Cures dry skin" | "Soothes and hydrates dry skin" |
| "Burns belly fat" | "Supports active metabolism" |
| "Eliminates bacteria" | "Helps reduce bacteria on contact" |
| "Doctor approved" | "Trusted by thousands of customers" |
| "Guaranteed results in 7 days" | "Many customers see results within 7 days" |
| "100% effective" | "Highly effective for most users" |
| "Instant relief from pain" | "Provides cooling, soothing relief" |
| "Natural Viagra alternative" | (refuse entirely, suggest other angle) |

## ✅ Required additions for certain product categories

### Supplements (oral consumables)
- FDA-safe verbs throughout: supports/helps/promotes
- Always add a disclaimer footer
- Note "consult a healthcare provider" if user has medical conditions
- Never claim treatment of any specific medical condition

### Skincare / topicals
- "Intended for external use only"
- Patch-test recommendation for first-time users
- Disclaimer footer
- "Soothes, supports, helps with" — not "heals, cures, treats"

### Cleaning / chemical products
- Note ingredients are "safe for home use" not "non-toxic" unless verified
- Warning if eye/skin contact recommendations apply
- Don't claim "kills 99.9%" without third-party certification

### Electronics
- Specify voltage compatibility for the market (e.g. 230-240V)
- Note warranty terms
- Be specific about what's NOT included (memory cards, batteries, adapters)

## Market-specific notes (example market: Kenya)

Every market has its own regulator; put yours in the store profile's `regulator notes`. The example market:

### Kenya Pharmacy and Poisons Board
- Health supplements technically require registration
- Selling unregistered "medicines" is illegal
- Stick to general wellness positioning, never disease claims
- Energy/athletic/daily wellness > medicinal

### Consumer protection
- Cash on delivery means customers reject easily if disappointed
- Page promises must match the product — this is your #1 refund driver
- Always state the store's real guarantee (store profile), never a generic one

### Ad platforms (Meta, TikTok, Google)
- All three have automated AI reviewers that flag specific words
- Avoid: "guaranteed, miracle, breakthrough, instant cure, FDA approved (unless true)"
- The disclaimer footer helps but doesn't override flagged claims

## How to flag during analysis

When analyzing a product, if you find compliance issues, list them in the analysis output as:

```json
"compliance_flags": [
  {
    "flag": "User wants 'cures eczema in 7 days' as the hook",
    "severity": "high",
    "action": "Refuse the cure claim. Suggest 'Soothes Itchy, Red Skin in 7 Days' instead."
  }
]
```

Severity levels:
- **high** = workflow should pause; this could get the user's ads banned or their COD rejected
- **medium** = rewrite is needed before generating copy
- **low** = note for the user but proceed

## When to push back on the user

The user is running a real business and trusts these guardrails. When they request a banned claim, don't lecture — give them a **better alternative** that achieves the same business goal:

- "I want to claim it cures eczema in 7 days" → "I can't write that as a cure, but here's a hook that converts better and won't get your ads banned: 'From Itchy & Flaky → Smooth & Glowing in 7 Days*' with a disclaimer footer."

The goal is to be a *useful partner* who keeps the business alive, not a content moderator.
