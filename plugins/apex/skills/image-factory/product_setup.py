#!/usr/bin/env python3
"""
product_setup.py  -  APEX step 2 of 4, Product setup: the product and its unique template (no page design).

Order of the whole flow:  PageEngine -> product_setup (this) -> Claude Code in VS Code designs the
page in the template created here -> Image Factory.

Reads <slug>-product.json (written by page-engine) and does what used to be done by hand:
  1/7 READ           the launch manifest
  2/7 PREFLIGHT      Shopify login (.env.<store>), app permissions, Shopify CLI, theme folder
  3/7 PRODUCT        create it (title, URL handle = slug, active), price + compare-at price (both from
                     the user), charge tax OFF, track inventory OFF, physical product / shipping OFF
  4/7 SALES CHANNEL  publish it to the Online Store
  5/7 TEMPLATE       templates/product.<slug>.json = a copy of the default product template
                     (same as "Create template -> based on product")
  6/7 PUSH + ASSIGN  push the template to the live theme, assign it to the product
  7/7 HAND-OFF       check the live page, write the Claude Code prompt (claude-code-prompt.md)

Every step is safe to repeat: an existing product with this handle is reused (never duplicated),
an existing template is never overwritten.

Usage (from the image factory folder; new-product.ps1 calls this for you):
  py product_setup.py incoming/<slug>/<slug>-product.json [--dry-run] [--product-only] [--install-page]
  --install-page  also install the page into the template by script (APEX v2, used by the watcher):
                  journey badge first, the sections above the buy button, the main product section,
                  then the description; everything below the buy button is left out. No Claude Code.
  --product-only  only stages 1-4 (update price, compare-at, tax, inventory, shipping), no template work

Settings:
  .env.<store>   SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET (or SHOPIFY_ACCESS_TOKEN)
  THEME_DIR      the local theme folder Claude Code works in (Windows variable, or THEME_DIR= in .env)
App permissions needed: write_products, read_products, write_inventory, read_inventory,
  write_publications, read_publications.
The template goes through Shopify CLI because the Admin API only writes theme files with a
special Shopify exemption.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_VERSION = "2026-07"
HERE = Path(__file__).resolve().parent
TOTAL = 7
NEEDED_SCOPES = ["write_products", "write_publications", "write_inventory"]


# ---------------------------------------------------------------- output helpers
def stage(n, name):
    print(f"\n━━ {n}/{TOTAL} {name} " + "━" * max(10, 50 - len(name)))


def ok(msg):
    print(f"  ✓ {msg}")


def info(msg):
    print(f"  · {msg}")


def fail(msg, fix=None):
    print(f"\n  ✗ {msg}")
    if fix:
        print(f"  → {fix}")
    print("\nStopped. Fix the point above and run the same command again (nothing is duplicated).")
    sys.exit(1)


# ---------------------------------------------------------------- settings
def read_env(path):
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def normalize_shop(raw):
    """Accept 'store', 'store.myshopify.com', with or without https:// or /admin, and
    admin.shopify.com/store/<store> links. Returns 'store.myshopify.com' (or '' if empty)."""
    s = raw.strip().strip('"').strip("'").lower()
    s = re.sub(r"^https?://", "", s)
    m = re.match(r"admin\.shopify\.com/store/([a-z0-9-]+)", s)
    if m:
        s = m.group(1)
    s = s.split("/")[0]
    if not s:
        return ""
    return s if s.endswith(".myshopify.com") else f"{s.split('.')[0]}.myshopify.com"


# ---------------------------------------------------------------- Shopify Admin API
class Shopify:
    def __init__(self, shop, token):
        self.shop, self.token = shop, token

    def gql(self, query, variables=None):
        body = json.dumps({"query": query, "variables": variables or {}}).encode()
        req = urllib.request.Request(
            f"https://{self.shop}/admin/api/{API_VERSION}/graphql.json",
            data=body,
            headers={"Content-Type": "application/json", "X-Shopify-Access-Token": self.token},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            fail(f"Shopify GraphQL HTTP {e.code}: {e.read().decode(errors='replace')[:300]}",
                 "check SHOPIFY_SHOP / the app login in .env.<store>")
        if data.get("errors"):
            fail(f"Shopify GraphQL error: {json.dumps(data['errors'])[:400]}")
        return data["data"]


def get_token(shop, cid, secret):
    body = urllib.parse.urlencode(
        {"grant_type": "client_credentials", "client_id": cid, "client_secret": secret}).encode()
    req = urllib.request.Request(f"https://{shop}/admin/oauth/access_token", data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.load(r)
    except urllib.error.HTTPError as e:
        fail(f"Shopify token request failed (HTTP {e.code}): {e.read().decode(errors='replace')[:200]}",
             "check SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET in .env.<store>, "
             "and that the app is installed on this store")
    return j["access_token"]


def check_user_errors(result, what):
    errs = result.get("userErrors") or []
    if errs:
        fail(f"{what}: " + "; ".join(f"{'.'.join(e.get('field') or [])} {e['message']}" for e in errs))


# ---------------------------------------------------------------- Shopify CLI
def run_cli(cli, args, show=True):
    """Run Shopify CLI without ever waiting for a key.
    - SHOPIFY_FLAG_FORCE=1: skips the CLI question "this does not look like a theme directory,
      proceed?" (the local theme folder only holds the files APEX pulls). The live-theme question
      is skipped by --allow-live on the push.
    - stdin closed: if the CLI ever asks anything else, it stops with its question in the output
      (shown below) instead of waiting invisibly for Enter."""
    cmd = [cli] + args
    print("  $ shopify " + " ".join(f'"{a}"' if " " in a else a for a in args))
    env = dict(os.environ, SHOPIFY_FLAG_FORCE="1")
    p = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, env=env)
    out = (p.stdout or "") + (p.stderr or "")
    if show:
        for line in out.strip().splitlines():
            print("    " + line)
    if "Failed to prompt" in out or "non-interactive" in out.lower():
        print("  ! Shopify CLI wanted to ask a question (see above). If it is a login, run once in "
              "PowerShell: shopify theme list --store <your-store>.myshopify.com")
    return p.returncode, out


def schema_defaults(path):
    """Setting defaults from a section's schema. A section added to a JSON template with empty
    settings does NOT get these defaults from Shopify, so the template must carry them."""
    try:
        m = re.search(r"{% schema %}(.*?){% endschema %}", path.read_text(encoding="utf-8"), re.S)
        return {s["id"]: s["default"] for s in json.loads(m.group(1)).get("settings", [])
                if "id" in s and "default" in s and s["default"] not in ("", None)}
    except Exception:
        return {}


HASH_COMMENT_RE = re.compile(r"\{#-?(.*?)-?#\}", re.S)


def fix_hash_comments(path):
    """Shopify Liquid has no {# ... #} comments: it prints them as text on the live page.
    Turn every one into {%- comment -%} ... {%- endcomment -%}. Returns how many were fixed."""
    text = path.read_text(encoding="utf-8")
    found = HASH_COMMENT_RE.findall(text)
    if found:
        text = HASH_COMMENT_RE.sub(lambda m: "{%- comment -%}" + m.group(1) + "{%- endcomment -%}", text)
        path.write_text(text, encoding="utf-8")
    return len(found)


def fix_schema_names(path):
    """Shopify rejects a section whose section / block / preset names are longer than 25
    characters, whose setting labels are longer than 70, whose header texts are longer than 50,
    or whose text settings have an
    empty default. Shorten them in place (editor labels only, the page copy is untouched)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"{% schema %}(.*?){% endschema %}", text, re.S)
    if not m:
        return []
    schema = json.loads(m.group(1))
    fixed = []
    def cut(obj, kind):
        n = obj.get("name")
        if isinstance(n, str) and len(n) > 25:
            short = n.split("(")[0].strip()[:25].strip()
            fixed.append(f"{kind} name '{n}' -> '{short}'")
            obj["name"] = short
    def cut_labels(settings, kind):
        for st in settings:
            if st.get("default", None) == "":
                del st["default"]
                fixed.append(f"{kind} setting '{st.get('id')}': empty default removed")
            c = st.get("content")
            if st.get("type") == "header" and isinstance(c, str) and len(c) > 50:
                short = c.split(" (")[0].split(":")[0][:50].rstrip()
                fixed.append(f"{kind} header '{c[:40]}...' -> '{short}'")
                st["content"] = short
            l = st.get("label")
            if isinstance(l, str) and len(l) > 70:
                short = l.split(" (")[0][:70].rstrip()
                fixed.append(f"{kind} label '{l[:40]}...' -> '{short}'")
                st["label"] = short
    cut(schema, "section")
    cut_labels(schema.get("settings", []), "section")
    for b in schema.get("blocks", []):
        cut(b, "block")
        cut_labels(b.get("settings", []), "block")
    for pr in schema.get("presets", []):
        cut(pr, "preset")
    if fixed:
        new = json.dumps(schema, ensure_ascii=False, indent=2)
        path.write_text(text[:m.start(1)] + "\n" + new + "\n" + text[m.end(1):], encoding="utf-8")
    return fixed


PUSH_ERR_RE = re.compile(r"pushed with errors|^\s*error\b|Invalid block|does not refer to an existing", re.I | re.M)


# ---------------------------------------------------------------- page install (APEX v2)
MAIN_RE = re.compile(r"main-product|product-information|product-main|^main$", re.I)


def load_theme_json(path):
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"^\s*/\*.*?\*/", "", text, flags=re.S)  # Shopify's auto-generated comment
    return json.loads(text)


def find_main_section(tpl):
    sections, order = tpl.get("sections", {}), tpl.get("order", [])
    for k in order:
        if MAIN_RE.search(sections.get(k, {}).get("type", "")) or k == "main":
            return k
    return order[0] if order else None


def install_page(tpl, desc_type, badge_settings, desc_defaults=None):
    """journey badge first, the sections above the buy button, the main product section, then the
    description. Everything below the main section is left out. Safe to run twice."""
    secs, order = tpl.get("sections", {}), list(tpl.get("order", []))
    main_key = find_main_section(tpl)
    if not main_key:
        fail("the product template has no sections")
    has_desc = next((k for k, s in secs.items() if s.get("type") == desc_type), None)
    main_pos = order.index(main_key)
    above = [k for k in order[:main_pos] if secs[k].get("type") != "journey-badge"]
    below = [k for k in order[main_pos + 1:] if k != has_desc]
    badge_key = next((k for k, s in secs.items() if s.get("type") == "journey-badge"), "journey-badge")
    new_secs = {badge_key: secs.get(badge_key) or {"type": "journey-badge", "settings": badge_settings}}
    for k in above + [main_key]:
        new_secs[k] = secs[k]
    desc_key = has_desc or "description"
    new_secs[desc_key] = secs.get(has_desc) if has_desc else {"type": desc_type, "settings": {}}
    for k, v in (desc_defaults or {}).items():
        new_secs[desc_key].setdefault("settings", {}).setdefault(k, v)
    tpl["sections"] = new_secs
    tpl["order"] = [badge_key] + above + [main_key, desc_key]
    removed = [f"{k} ({secs[k].get('type')})" for k in below]
    kept_above = [f"{k} ({secs[k].get('type')})" for k in above]
    return tpl, main_key, kept_above, removed


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="PageEngine launch: product + template + page")
    ap.add_argument("manifest", help="path to <slug>-product.json")
    ap.add_argument("--dry-run", action="store_true", help="read + preflight only, change nothing")
    ap.add_argument("--install-page", action="store_true",
                    help="install the PageEngine page into the template by script (no Claude Code step)")
    ap.add_argument("--product-only", action="store_true",
                    help="only the product (price, compare-at, tax, inventory, shipping) and sales channel")
    a = ap.parse_args()

    # ---------------------------------------------------------- 1 READ
    stage(1, "READ")
    mpath = Path(a.manifest).resolve()
    if not mpath.exists():
        fail(f"not found: {mpath}", "download <slug>-product.json from the chat into Downloads")
    m = json.loads(mpath.read_text(encoding="utf-8-sig"))
    for key in ("store", "title", "slug", "price", "description_section"):
        if not m.get(key):
            fail(f"{mpath.name} has no '{key}'")
    slug, store = m["slug"], m["store"]
    suffix = m.get("template_suffix") or slug
    desc_type = m["description_section"]
    desc_file = mpath.parent / f"{desc_type}.liquid"
    badge_file = mpath.parent / "journey-badge.liquid"
    badge = m.get("journey_badge", {})
    badge_settings = {
        "banner_text": badge.get("banner_text", "FREE DELIVERY"),
        "circle_color": badge.get("circle_color", "#22c55e"),
        "banner_color": badge.get("banner_color", "#16a34a"),
    }
    compare_at = m.get("compare_at_price")
    if compare_at in (None, "", 0, "0"):
        fail(f"{mpath.name} has no compare_at_price",
             "give PageEngine the compare price together with the selling price; it goes into <slug>-product.json")
    try:
        if float(compare_at) <= float(m["price"]):
            fail(f"compare_at_price ({compare_at}) must be higher than the price ({m['price']})")
    except ValueError:
        fail(f"price or compare_at_price is not a number: {m['price']} / {compare_at}")
    ok(f"title: {m['title']}")
    ok(f"URL handle: {slug}   template: product.{suffix}")
    ok(f"price: {m.get('currency', '')} {m['price']}   compare-at: {m.get('currency', '')} {compare_at}")
    for f in (desc_file, badge_file):
        (ok if f.exists() else info)(f"{f.name}: {'found (for Claude Code)' if f.exists() else 'not found in the downloads'}")

    # ---------------------------------------------------------- 2 PREFLIGHT
    stage(2, "PREFLIGHT")
    base_env = read_env(HERE / ".env")
    store_env = read_env(HERE / f".env.{store}")
    if not store_env:
        fail(f".env.{store} not found in {HERE}",
             f"create .env.{store} with SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET")
    shop = normalize_shop(store_env.get("SHOPIFY_SHOP", ""))
    if not shop:
        fail(f"SHOPIFY_SHOP is empty in .env.{store}",
             "put your store name in it, e.g. SHOPIFY_SHOP=your-store (or your-store.myshopify.com)")
    if store_env.get("SHOPIFY_ACCESS_TOKEN"):
        token = store_env["SHOPIFY_ACCESS_TOKEN"]
    else:
        token = get_token(shop, store_env.get("SHOPIFY_CLIENT_ID", ""), store_env.get("SHOPIFY_CLIENT_SECRET", ""))
    sh = Shopify(shop, token)
    scopes = [s["handle"] for s in sh.gql("{ currentAppInstallation { accessScopes { handle } } }")
              ["currentAppInstallation"]["accessScopes"]]
    ok(f"Shopify: {shop} · login OK")
    missing = [s for s in NEEDED_SCOPES if s not in scopes]
    if missing:
        fail(f"the app is missing permission(s): {', '.join(missing)}",
             "Dev Dashboard -> your app -> Versions: add write_products, read_products, write_inventory, read_inventory, "
             "write_publications, read_publications, release the version, then approve the update on the store")
    ok("app permissions: products + sales channels")

    cli = shutil.which("shopify")
    if not cli:
        fail("Shopify CLI not found", "install it once: npm install -g @shopify/cli")
    ok("Shopify CLI found")

    theme_dir = os.environ.get("THEME_DIR") or base_env.get("THEME_DIR") or store_env.get("THEME_DIR")
    if not theme_dir:
        fail("THEME_DIR is not set (your local theme folder)",
             'run once: setx THEME_DIR "C:\\path\\to\\your\\theme"  and open a new PowerShell window')
    theme = Path(theme_dir)
    if not (theme / "sections").is_dir() or not (theme / "templates").is_dir():
        fail(f"{theme} is not a theme folder (no sections/ and templates/)",
             f"pull the live theme once: shopify theme pull --live --store {shop} --path \"{theme}\"")
    ok(f"theme folder: {theme}")

    if a.dry_run:
        print("\n━━ DRY RUN: everything is ready, nothing was changed.")
        return

    # ---------------------------------------------------------- 3 PRODUCT
    stage(3, "PRODUCT")
    q = sh.gql("""query($q:String!){ products(first:1, query:$q){ nodes{ id handle title templateSuffix } } }""",
               {"q": f"handle:{slug}"})
    nodes = [n for n in q["products"]["nodes"] if n["handle"] == slug]
    if nodes:
        pid = nodes[0]["id"]
        info(f"product with handle '{slug}' already exists, reusing it (no duplicate)")
    else:
        r = sh.gql("""mutation($p:ProductCreateInput!){ productCreate(product:$p){
                        product{ id handle } userErrors{ field message } } }""",
                   {"p": {"title": m["title"], "handle": slug, "status": m.get("status", "ACTIVE")}})
        check_user_errors(r["productCreate"], "product create")
        pid = r["productCreate"]["product"]["id"]
        if r["productCreate"]["product"]["handle"] != slug:
            fail(f"Shopify gave the handle '{r['productCreate']['product']['handle']}' instead of '{slug}'")
        ok(f"product created: {m['title']}")
    ok(f"URL handle: {slug}")

    v = sh.gql("""query($id:ID!){ product(id:$id){ variants(first:1){ nodes{ id } } } }""", {"id": pid})
    vid = v["product"]["variants"]["nodes"][0]["id"]
    variant = {"id": vid, "price": str(m["price"]), "compareAtPrice": str(compare_at) if compare_at else None,
               "taxable": False, "inventoryItem": {"tracked": False, "requiresShipping": False}}
    r = sh.gql("""mutation($pid:ID!,$v:[ProductVariantsBulkInput!]!){ productVariantsBulkUpdate(productId:$pid, variants:$v){
                    productVariants{ id price } userErrors{ field message } } }""", {"pid": pid, "v": [variant]})
    check_user_errors(r["productVariantsBulkUpdate"], "price / compare-at / tax / inventory / shipping")
    ok(f"price: {m.get('currency', '')} {m['price']}")
    ok(f"compare-at price: {m.get('currency', '')} {compare_at}")
    ok("charge tax: OFF")
    ok("track inventory: OFF")
    ok("physical product / shipping: OFF")

    # ---------------------------------------------------------- 4 SALES CHANNEL
    stage(4, "SALES CHANNEL")
    pubs = sh.gql("{ publications(first:25){ nodes{ id name } } }")["publications"]["nodes"]
    online = next((p for p in pubs if p["name"].lower() == "online store"), None)
    if not online:
        fail("no 'Online Store' sales channel found on this store")
    r = sh.gql("""mutation($id:ID!,$in:[PublicationInput!]!){ publishablePublish(id:$id, input:$in){ userErrors{ field message } } }""",
               {"id": pid, "in": [{"publicationId": online["id"]}]})
    check_user_errors(r["publishablePublish"], "publish to Online Store")
    ok("published to the Online Store")

    if a.product_only:
        print("\n━━ DONE (product only) " + "━" * 36)
        print("  Price, compare-at, tax, inventory, shipping and sales channel are set. Template untouched.")
        return

    # ---------------------------------------------------------- 5 TEMPLATE
    stage(5, "TEMPLATE")
    tpl_rel = f"templates/product.{suffix}.json"
    info("pulling the default product template (and this product's, if it exists) from the live theme")
    code, _ = run_cli(cli, ["theme", "pull", "--path", str(theme), "--store", shop, "--live",
                            "--only", "templates/product.json", "--only", tpl_rel,
                            "--only", "sections/journey-badge.liquid"])
    if code != 0:
        fail("Shopify CLI pull failed (see above)", f"log in once: shopify theme list --store {shop}")
    tpl_path, base_path = theme / tpl_rel, theme / "templates" / "product.json"
    if tpl_path.exists():
        info(f"{tpl_rel} already exists on the theme, kept as it is (never overwritten)")
    else:
        if not base_path.exists():
            fail("templates/product.json not found on the live theme")
        tpl_path.write_bytes(base_path.read_bytes())
        ok(f"created {tpl_rel} (a copy of the default product template)")
    try:
        tj = json.loads(re.sub(r"^\s*/\*.*?\*/", "", tpl_path.read_text(encoding="utf-8-sig"), flags=re.S))
        info("sections in it: " + ", ".join(f"{k} ({tj['sections'][k].get('type')})" for k in tj.get("order", [])))
    except Exception:
        pass

    # ---------------------------------------------------------- 6 PUSH + ASSIGN
    stage(6, "PUSH + ASSIGN")
    push = ["--only", tpl_rel]
    if a.install_page:
        tpl, main_key, kept_above, removed = install_page(load_theme_json(tpl_path), desc_type, badge_settings,
                                                          schema_defaults(desc_file))
        tpl_path.write_text(json.dumps(tpl, indent=2, ensure_ascii=False), encoding="utf-8")
        ok("page installed in the template: " + " -> ".join(tpl["order"]))
        info("kept above the buy button: " + (", ".join(kept_above) if kept_above else "nothing"))
        info("left out below the buy button: " + (", ".join(removed) if removed else "nothing"))
        if not desc_file.exists():
            fail(f"{desc_file.name} not found next to the manifest")
        shutil.copy2(desc_file, theme / "sections" / desc_file.name)
        for note in fix_schema_names(theme / "sections" / desc_file.name):
            info("fixed for Shopify limits: " + note)
        n_fixed = fix_hash_comments(theme / "sections" / desc_file.name)
        if n_fixed:
            info(f"fixed {n_fixed} {{# #}} note(s): Shopify would print them as text; now {{% comment %}} tags")
        push += ["--only", f"sections/{desc_file.name}"]
        ok(f"sections/{desc_file.name} copied into the theme")
        if (theme / "sections" / "journey-badge.liquid").exists():
            info("sections/journey-badge.liquid already in the theme, kept as it is")
        else:
            src = badge_file if badge_file.exists() else HERE / "journey-badge.liquid"
            if not src.exists():
                fail("journey-badge.liquid is missing (not in the theme, not in the factory folder)")
            shutil.copy2(src, theme / "sections" / "journey-badge.liquid")
            push += ["--only", "sections/journey-badge.liquid"]
            ok("sections/journey-badge.liquid copied into the theme")

    code, out = run_cli(cli, ["theme", "push", "--path", str(theme), "--store", shop,
                              "--live", "--allow-live"] + push)
    if code != 0 or PUSH_ERR_RE.search(out):
        fail("Shopify rejected part of the push (see the error box above)",
             "fix what Shopify names, then run the same command again")
    ok("pushed to the live theme: " + ", ".join(push[1::2]))
    r = sh.gql("""mutation($p:ProductUpdateInput!){ productUpdate(product:$p){ product{ templateSuffix } userErrors{field message} } }""",
               {"p": {"id": pid, "templateSuffix": suffix}})
    check_user_errors(r["productUpdate"], "template assignment")
    ok(f"template assigned to the product: product.{suffix}")

    # ---------------------------------------------------------- 7 HAND-OFF
    stage(7, "HAND-OFF")
    url_q = sh.gql("""query($id:ID!){ product(id:$id){ onlineStoreUrl } }""", {"id": pid})
    url = url_q["product"]["onlineStoreUrl"] or f"https://{shop}/products/{slug}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            ok(f"live page answers (HTTP {resp.status})")
    except Exception as e:
        info(f"live page not reachable yet ({e}); Shopify may need a minute")

    if a.install_page:
        prefix = m.get("prefix", "")
        marks = {"journey badge": "jb-wrap", "description": f"{prefix}-page" if prefix else desc_type}
        found = {}
        for _ in range(4):
            try:
                req = urllib.request.Request(url + ("&" if "?" in url else "?") + f"v={int(time.time())}",
                                             headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                found = {n: (mk in html) for n, mk in marks.items()}
                if all(found.values()):
                    break
            except Exception:
                pass
            time.sleep(10)
        for n, hit in found.items():
            print(f"  {'✓' if hit else '✗'} {n} {'showing on the live page' if hit else 'NOT on the live page'}")
        if not found or not all(found.values()):
            fail("the page is not showing on the live product page, so the images would have nowhere to go",
                 f"check the push output above; open {url} in a private window; then run again")
        admin_id = pid.rsplit("/", 1)[-1]
        print("\n━━ DONE " + "━" * 50)
        print(f"  Live page:  {url}")
        print(f"  Admin:      https://admin.shopify.com/store/{shop.replace('.myshopify.com', '')}/products/{admin_id}")
        print(f"  Template:   {tpl_rel} (page installed)")
        return

    badge = m.get("journey_badge", {})
    badge_line = (f'circle_color "{badge_settings["circle_color"]}", banner_color "{badge_settings["banner_color"]}", '
                  f'banner_text "{badge_settings["banner_text"]}"')
    prompt = f"""PageEngine: design the product page for "{m['title']}" (store: {store}).

The product and its unique template already exist (created by product_setup):
- Template: {tpl_rel} (a copy of the default product template), already assigned to the product
- Live page: {url}
- Theme folder: {theme}

PageEngine files (use them as they are, do not rewrite the copy):
- {desc_file}
- {badge_file}
- {mpath}

Do this:
1. Copy {desc_file.name} into sections/. Copy journey-badge.liquid into sections/ only if the theme does not have it yet.
2. In {tpl_rel} keep only the main product section (gallery, title, price, buy button). Remove every other section below the buy button.
3. Add the section "journey-badge" as the FIRST section (above the gallery) with {badge_line}.
4. Add the section "{desc_type}" directly after the main product section, with no blocks. Update "order".
5. Run shopify theme check on the changed files and fix real errors without changing the copy.
6. Push only these files to the live theme:
   shopify theme push --live --allow-live --only {tpl_rel} --only sections/{desc_type}.liquid --only sections/journey-badge.liquid
7. Show me the template before and after, and confirm the page at {url} shows the badge and the description.
"""
    prompt_path = mpath.parent / "claude-code-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    ok(f"Claude Code prompt written: {prompt_path}")

    admin_id = pid.rsplit("/", 1)[-1]
    store_handle = shop.replace(".myshopify.com", "")
    print("\n━━ DONE " + "━" * 50)
    print(f"  Live page:  {url}")
    print(f"  Admin:      https://admin.shopify.com/store/{store_handle}/products/{admin_id}")
    print(f"  Template:   {tpl_rel}")
    print("  Next:       paste the Claude Code prompt into Claude Code in VS Code (it is on your clipboard)")
    print(f"  Then:       .\\run-factory.ps1 {slug}   (images, after the page is designed)")


if __name__ == "__main__":
    main()
