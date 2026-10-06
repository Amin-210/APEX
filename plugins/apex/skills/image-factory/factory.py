#!/usr/bin/env python3
"""
factory.py  -  APEX step 4 of 4, the Image Factory engine.

Turns <slug>-images.json (written by page-engine's build-image-manifest.py) into finished images on
the live Shopify product page:

  1 SET UP      products/<slug>/  (manifest.json, reference/ = the product photos, output/ = images)
  2 PREFLIGHT   product photo, OpenAI key, (upload runs) Shopify login, app permissions, product
  3 GENERATE    one OpenAI Images call per image, the product photo attached when the prompt needs it
  4 UPLOAD      section images -> Content > Files as <slug>_<image_id>.png (the page finds them by
                that name); catalog slides -> the product gallery, in slide order (the old gallery
                media are detached from the product and stay in Content > Files)
  5 LIVE CHECK  the product page is fetched and the section images on it are counted

Every step is safe to repeat: an image is generated again only when it is missing, its prompt
changed, or it is named in --redo; an image is uploaded again only when its file changed.

Usage (from the image factory folder; run-factory.ps1 calls this for you):
  py factory.py <path>/<slug>-images.json --photos <folder> --no-upload   set up + generate
  py factory.py <slug> --no-upload                                         generate what is missing
  py factory.py <slug> --yes                                               generate what is missing + upload
  py factory.py <slug> --no-upload --redo image_hero,slide_image_03        make those again
  py factory.py <slug> --test                                              all at low quality, no upload

Options:
  --photos <folder>   product photos (1-3 .jpg/.png/.webp, clearest first) copied into reference/
  --no-upload         stop after generating
  --yes               upload without asking
  --redo a,b,c        generate these image ids again
  --only a,b,c        work on these image ids only
  --test              every image at low quality into test/ (the real images are not touched)
  --quality <q>       quality for this run (low, medium, high, xhigh, max)
  --key-quality <q>   quality for the key images image_hero and slide_image_01 (default: high)
  --text none         ask for images with no rendered text (add the captions yourself later)
  --handle <handle>   the product's URL handle when it is not the slug
  --skip-live-check   do not fetch the product page after the upload

Settings in .env (this folder):
  OPENAI_API_KEY      required
  IMAGE_MODEL         default gpt-image-2.5-sunburst (gpt-image-2.5-flare: same price, faster)
  IMAGE_QUALITY       default medium
  IMAGE_WORKERS       images generated at the same time, default 3
Store login in .env.<store> (store = "store" in the images.json):
  SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET (or SHOPIFY_ACCESS_TOKEN)
  App permissions: write_files, read_files, write_products, read_products.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from product_setup import Shopify, get_token, normalize_shop, read_env  # noqa: E402  (ships next to this file)

PRODUCTS = HERE / "products"
OPENAI_URL = "https://api.openai.com/v1/images"
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp"}
QUALITIES = ("low", "medium", "high", "xhigh", "max")
KEY_IMAGES = ("image_hero", "slide_image_01")
NEEDED_SCOPES = ("write_files", "write_products")
MAX_REFERENCE_PHOTOS = 3
NO_TEXT = ("\n\nIMPORTANT: render NO text at all in this image: no captions, letters, numbers, labels or "
           "chips. Leave clean, calm space where the captions would go; they are added later.")

PRINT_LOCK = threading.Lock()


# ---------------------------------------------------------------- output
def say(msg=""):
    with PRINT_LOCK:
        print(msg, flush=True)


def stage(name):
    say(f"\n━━ {name} " + "━" * max(10, 56 - len(name)))


def ok(msg):
    say(f"  ✓ {msg}")


def info(msg):
    say(f"  · {msg}")


def warn(msg):
    say(f"  ! {msg}")


def stop(msg, fix=None):
    say(f"\n  ✗ {msg}")
    if fix:
        say(f"  → {fix}")
    say("\nStopped. Fix the point above and run the same command again (nothing is made twice).")
    sys.exit(1)


# ---------------------------------------------------------------- small helpers
def sha(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:16]


def prompt_key(entry: dict, text_mode: str) -> str:
    """What decides whether an image must be made again: its prompt, the photo use, the text mode."""
    raw = json.dumps({"p": entry.get("prompt", ""), "r": bool(entry.get("use_reference")),
                      "a": entry.get("aspect"), "t": text_mode}, sort_keys=True)
    return sha(raw.encode("utf-8"))


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def id_list(raw: str | None) -> set[str]:
    return {x.strip() for x in (raw or "").split(",") if x.strip()}


def size_for(aspect: str | None, model: str) -> str:
    """Pixel size for an aspect. GPT Images 2.5 takes custom sizes; older models take the three
    standard ones."""
    custom = {"1:1": "1024x1024", "4:3": "1536x1152", "3:4": "1152x1536", "4:5": "1024x1280",
              "5:4": "1280x1024", "3:2": "1536x1024", "2:3": "1024x1536", "16:9": "1536x864",
              "9:16": "864x1536"}
    standard = {"1:1": "1024x1024"}
    a = (aspect or "1:1").strip()
    if model.startswith("gpt-image-2.5"):
        return custom.get(a, "1024x1024")
    if a in standard:
        return standard[a]
    try:
        w, h = (float(x) for x in a.split(":"))
    except ValueError:
        return "1024x1024"
    return "1536x1024" if w > h else "1024x1536" if h > w else "1024x1024"


# ---------------------------------------------------------------- HTTP
def multipart(fields: list[tuple[str, str]], files: list[tuple[str, str, bytes, str]]):
    """Body + content type for multipart/form-data. files = (field, filename, data, mime)."""
    boundary = "----apex" + uuid.uuid4().hex
    out = bytearray()
    for name, value in fields:
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n"
                f"{value}\r\n").encode("utf-8")
    for field, filename, data, mime in files:
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n").encode("utf-8")
        out += data + b"\r\n"
    out += f"--{boundary}--\r\n".encode("utf-8")
    return bytes(out), f"multipart/form-data; boundary={boundary}"


class OpenAIError(Exception):
    def __init__(self, status, message, fatal=False):
        super().__init__(message)
        self.status, self.fatal = status, fatal


def openai_call(path: str, key: str, body: bytes, ctype: str, timeout: int = 600) -> dict:
    """One OpenAI Images request with retries for rate limits and server errors."""
    for attempt in range(4):
        req = urllib.request.Request(f"{OPENAI_URL}/{path}", data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": ctype})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            try:
                err = json.loads(text).get("error", {}) or {}
            except ValueError:
                err = {}
            msg = err.get("message") or text[:300]
            code = err.get("code") or err.get("type") or ""
            if e.code in (401, 403) or code in ("insufficient_quota", "invalid_api_key", "billing_hard_limit_reached"):
                raise OpenAIError(e.code, f"{code or e.code}: {msg}", fatal=True)
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise OpenAIError(e.code, f"HTTP {e.code} {code}: {msg}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise OpenAIError(0, f"network error: {e}")
    raise OpenAIError(0, "no answer after 4 tries")


def generate_one(entry: dict, refs: list[Path], key: str, model: str, quality: str, text_mode: str) -> bytes:
    prompt = entry["prompt"] + (NO_TEXT if text_mode == "none" else "")
    size = size_for(entry.get("aspect"), model)
    if entry.get("use_reference") and refs:
        fields = [("model", model), ("prompt", prompt), ("size", size), ("quality", quality), ("n", "1")]
        files = [("image[]", p.name, p.read_bytes(), mimetypes.guess_type(p.name)[0] or "image/jpeg")
                 for p in refs]
        body, ctype = multipart(fields, files)
        data = openai_call("edits", key, body, ctype)
    else:
        body = json.dumps({"model": model, "prompt": prompt, "size": size, "quality": quality, "n": 1}).encode()
        data = openai_call("generations", key, body, "application/json")
    item = (data.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            return r.read()
    raise OpenAIError(0, "the answer held no image")


# ---------------------------------------------------------------- 1 SET UP
def set_up(target: str, photos: str | None) -> tuple[str, Path]:
    """Accepts a slug or a path to <slug>-images.json. Returns (slug, product folder)."""
    p = Path(target)
    if p.suffix.lower() == ".json":
        if not p.exists():
            stop(f"FileNotFoundError: {p}", "download <slug>-images.json from the chat (or let the "
                 "watcher fetch it from Google Drive), then run again")
        manifest = read_json(p)
        if not isinstance(manifest, dict) or not manifest.get("images"):
            stop(f"{p.name} is not an image manifest", "build it with build-image-manifest.py from the prompts .md")
        slug = manifest.get("slug") or p.name.split("-images")[0]
        folder = PRODUCTS / slug
        (folder / "reference").mkdir(parents=True, exist_ok=True)
        (folder / "output").mkdir(exist_ok=True)
        old = read_json(folder / "manifest.json")
        write_json(folder / "manifest.json", manifest)
        prompts_md = p.with_name(f"{slug}-image-prompts.md")
        if prompts_md.exists():
            shutil.copy2(prompts_md, folder / prompts_md.name)
        ok(f"{'updated' if old else 'set up'} products/{slug}/ from {p.name}")
    else:
        slug = target.strip().lower()
        folder = PRODUCTS / slug
        if not (folder / "manifest.json").exists():
            stop(f"products/{slug}/ is not set up yet",
                 f"run it once with the manifest: py factory.py <path>/{slug}-images.json --photos <folder>")
        ok(f"products/{slug}/ found")
    if photos:
        src = Path(photos)
        if not src.is_dir():
            stop(f"photos folder not found: {src}")
        found = sorted(f for f in src.iterdir() if f.is_file() and f.suffix.lower() in PHOTO_EXT)
        skipped = [f.name for f in src.iterdir() if f.is_file() and f.suffix.lower() not in PHOTO_EXT]
        if skipped:
            warn("skipped (not .jpg/.png/.webp, e.g. iPhone .heic): " + ", ".join(skipped))
        for f in found:
            shutil.copy2(f, folder / "reference" / f.name)
        if found:
            ok(f"{len(found)} photo(s) copied into reference/")
    return slug, folder


# ---------------------------------------------------------------- 2 PREFLIGHT
def references(folder: Path) -> list[Path]:
    refs = sorted(f for f in (folder / "reference").iterdir()
                  if f.is_file() and f.suffix.lower() in PHOTO_EXT)
    return refs[:MAX_REFERENCE_PHOTOS]


def preflight_openai(folder: Path, manifest: dict) -> tuple[str, str, list[Path]]:
    env = read_env(HERE / ".env")
    key = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        stop("OPENAI_API_KEY missing", "add the line OPENAI_API_KEY=... to .env in the image factory folder")
    model = env.get("IMAGE_MODEL") or os.environ.get("IMAGE_MODEL") or "gpt-image-2.5-sunburst"
    ok(f"OpenAI key found · model {model}")
    refs = references(folder)
    if any(x.get("use_reference") and x.get("generate") for x in manifest["images"]):
        if not refs:
            stop("no product photo in reference/",
                 f"put 1-3 product photos in {folder / 'reference'} or run again with --photos <folder>")
        ok("product photo(s): " + ", ".join(p.name for p in refs))
    return key, model, refs


def preflight_shopify(store: str, handle: str):
    store_env = read_env(HERE / f".env.{store}")
    if not store_env:
        stop(f".env.{store} not found in {HERE}",
             f"create .env.{store} with SHOPIFY_SHOP, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET")
    shop = normalize_shop(store_env.get("SHOPIFY_SHOP", ""))
    if not shop:
        stop(f"SHOPIFY_SHOP is not set in .env.{store}", "put your store name in it, e.g. SHOPIFY_SHOP=your-store")
    token = store_env.get("SHOPIFY_ACCESS_TOKEN") or get_token(
        shop, store_env.get("SHOPIFY_CLIENT_ID", ""), store_env.get("SHOPIFY_CLIENT_SECRET", ""))
    sh = Shopify(shop, token)
    scopes = {s["handle"] for s in sh.gql("{ currentAppInstallation { accessScopes { handle } } }")
              ["currentAppInstallation"]["accessScopes"]}
    missing = [s for s in NEEDED_SCOPES if s not in scopes]
    if missing:
        stop(f"the app is missing permission(s): {', '.join(missing)}",
             "Dev Dashboard -> your app -> Versions: add write_files, read_files, write_products, "
             "read_products, release the version, then approve the update on the store")
    ok(f"Shopify: {shop} · login OK · files + products allowed")
    q = sh.gql("query($q: String!) { products(first: 1, query: $q) { nodes { id handle title onlineStoreUrl } } }",
               {"q": f"handle:{handle}"})
    nodes = [n for n in q["products"]["nodes"] if n["handle"] == handle]
    if not nodes:
        stop(f"no product with URL handle '{handle}'",
             "create it first (.\\new-product.ps1 <slug>), or run with --handle <its handle>")
    ok(f"product: {nodes[0]['title']} ({handle})")
    return sh, shop, nodes[0]


# ---------------------------------------------------------------- 3 GENERATE
def generate(folder: Path, manifest: dict, args, key: str, model: str, refs: list[Path]) -> list[str]:
    state = read_json(folder / "state.json", {}) or {}
    test = args.test
    out_dir = folder / ("test" if test else "output")
    out_dir.mkdir(exist_ok=True)
    redo, only = id_list(args.redo), id_list(args.only)
    text_mode = args.text or "rendered"
    base_q = "low" if test else (args.quality or read_env(HERE / ".env").get("IMAGE_QUALITY") or "medium")
    key_q = "low" if test else (args.key_quality or "high")
    for q in (base_q, key_q):
        if q not in QUALITIES:
            stop(f"unknown quality '{q}'", "use one of: " + ", ".join(QUALITIES))

    todo, real = [], []
    for e in manifest["images"]:
        if only and e["id"] not in only:
            continue
        if not e.get("generate"):
            real.append(e)
            continue
        out = out_dir / e.get("output_file", f"{e['id']}.png")
        pk = prompt_key(e, text_mode)
        if test or e["id"] in redo or not out.exists() or state.get(e["id"], {}).get("prompt") != pk:
            todo.append((e, out, pk, key_q if e["id"] in KEY_IMAGES else base_q))
    unknown = (redo | only) - {e["id"] for e in manifest["images"]}
    if unknown:
        warn("not in the manifest: " + ", ".join(sorted(unknown)))

    done_already = sum(1 for e in manifest["images"] if e.get("generate")) - len(todo) if not only else 0
    info(f"{len(todo)} to generate" + (f", {done_already} already done" if done_already > 0 else "")
         + (f" · test run, low quality, into test/" if test else ""))
    failed: list[str] = []
    fatal: list[str] = []
    if todo:
        workers = max(1, int(read_env(HERE / ".env").get("IMAGE_WORKERS") or 3))

        def job(item):
            e, out, pk, q = item
            if fatal:
                return e["id"], None, "skipped after a fatal OpenAI error"
            t0 = time.time()
            try:
                img = generate_one(e, refs, key, model, q, text_mode)
            except OpenAIError as err:
                if err.fatal:
                    fatal.append(str(err))
                return e["id"], None, str(err)
            out.write_bytes(img)
            return e["id"], (pk, q, round(time.time() - t0)), None

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(job, it) for it in todo]
            for f in as_completed(futures):
                iid, res, err = f.result()
                if err:
                    failed.append(iid)
                    say(f"  ✗ {iid:<20} {err}")
                    continue
                pk, q, secs = res
                say(f"  ✓ {iid:<20} {q:<6} {secs}s")
                if not test:
                    st = state.setdefault(iid, {})
                    st.update(prompt=pk, quality=q, model=model, text=text_mode,
                              made=datetime.now().isoformat(timespec="seconds"))
                    write_json(folder / "state.json", state)
    if fatal:
        stop(f"OpenAI: {fatal[0]}", "insufficient_quota / 401: add credit or fix the key on platform.openai.com, "
             "then run the same command again")
    for e in real:
        info(f"{e['id']:<20} REAL PHOTO, not generated: put it in products/{folder.name}/real/{e['id']}.jpg "
             "to have it uploaded with the slides")
    return failed


# ---------------------------------------------------------------- 4 UPLOAD
FILE_FIELDS = "id fileStatus alt ... on MediaImage { image { url } } ... on GenericFile { url }"


def staged_upload(sh: Shopify, name: str, data: bytes, mime: str) -> str:
    res = sh.gql("""mutation($input: [StagedUploadInput!]!) {
        stagedUploadsCreate(input: $input) {
          stagedTargets { url resourceUrl parameters { name value } }
          userErrors { field message } } }""",
                 {"input": [{"filename": name, "mimeType": mime, "httpMethod": "POST",
                             "resource": "IMAGE", "fileSize": str(len(data))}]})["stagedUploadsCreate"]
    if res["userErrors"]:
        stop("staged upload: " + "; ".join(e["message"] for e in res["userErrors"]))
    t = res["stagedTargets"][0]
    body, ctype = multipart([(p["name"], p["value"]) for p in t["parameters"]], [("file", name, data, mime)])
    req = urllib.request.Request(t["url"], data=body, method="POST", headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=300):
            pass
    except urllib.error.HTTPError as e:
        stop(f"upload of {name} failed: HTTP {e.code} {e.read().decode(errors='replace')[:200]}")
    return t["resourceUrl"]


def create_file(sh: Shopify, name: str, data: bytes, alt: str) -> str:
    """Upload one image to Content > Files under exactly this name (replacing an older one)."""
    mime = mimetypes.guess_type(name)[0] or "image/png"
    source = staged_upload(sh, name, data, mime)
    res = sh.gql("""mutation($files: [FileCreateInput!]!) {
        fileCreate(files: $files) { files { id } userErrors { field message } } }""",
                 {"files": [{"originalSource": source, "filename": name, "contentType": "IMAGE",
                             "alt": alt[:500], "duplicateResolutionMode": "REPLACE"}]})["fileCreate"]
    if res["userErrors"]:
        stop(f"fileCreate {name}: " + "; ".join(e["message"] for e in res["userErrors"]))
    return res["files"][0]["id"]


def wait_ready(sh: Shopify, ids: list[str], timeout: int = 180) -> None:
    pending, t0 = set(ids), time.time()
    while pending and time.time() - t0 < timeout:
        nodes = sh.gql("query($ids: [ID!]!) { nodes(ids: $ids) { ... on File { id fileStatus } } }",
                       {"ids": list(pending)})["nodes"]
        for n in nodes:
            if n and n.get("fileStatus") == "READY":
                pending.discard(n["id"])
            elif n and n.get("fileStatus") == "FAILED":
                stop(f"Shopify could not process file {n['id']}", "run the upload again")
        if pending:
            time.sleep(3)
    if pending:
        warn(f"{len(pending)} file(s) still processing in Shopify; they appear on the page in a minute")


def upload(sh: Shopify, folder: Path, manifest: dict, product: dict) -> None:
    slug = manifest["slug"]
    state = read_json(folder / "state.json", {}) or {}
    out_dir = folder / "output"
    real_dir = folder / "real"

    # section images -> Content > Files as <slug>_<id>.png
    sections = [e for e in manifest["images"] if e.get("kind") == "section"]
    n_up = n_same = 0
    for e in sections:
        f = out_dir / e.get("output_file", f"{e['id']}.png")
        if not f.exists():
            info(f"{e['id']:<20} not generated yet, skipped")
            continue
        data = f.read_bytes()
        st = state.setdefault(e["id"], {})
        if st.get("uploaded") == sha(data) and st.get("file_id"):
            n_same += 1
            continue
        name = f"{slug}_{e['id']}.png"
        st["file_id"] = create_file(sh, name, data, e.get("title") or manifest.get("product", ""))
        st["uploaded"] = sha(data)
        write_json(folder / "state.json", state)
        n_up += 1
        ok(f"{name:<34} -> Content > Files")
    info(f"section images: {n_up} uploaded, {n_same} unchanged")

    # catalog slides -> the product gallery, in slide order
    slides = sorted((e for e in manifest["images"] if e.get("kind") == "slide"), key=lambda e: e.get("slide") or 0)
    gallery: list[str] = []
    changed = False
    for e in slides:
        f = out_dir / e.get("output_file", f"{e['id']}.png")
        if not e.get("generate"):
            hits = [p for p in sorted(real_dir.glob(f"{e['id']}.*")) if p.suffix.lower() in PHOTO_EXT] \
                if real_dir.is_dir() else []
            if not hits:
                info(f"{e['id']:<20} real photo not added yet, left out of the gallery")
                continue
            f = hits[0]
        if not f.exists():
            info(f"{e['id']:<20} not generated yet, left out of the gallery")
            continue
        data = f.read_bytes()
        st = state.setdefault(e["id"], {})
        if st.get("uploaded") != sha(data) or not st.get("file_id"):
            name = f"{slug}_{e['id']}{f.suffix.lower()}"
            st["file_id"] = create_file(sh, name, data, e.get("title") or manifest.get("product", ""))
            st["uploaded"] = sha(data)
            write_json(folder / "state.json", state)
            changed = True
            ok(f"{name:<34} -> uploaded")
        gallery.append(st["file_id"])
    if not gallery:
        warn("no slides to put in the gallery")
        return
    wait_ready(sh, gallery)

    pid = product["id"]
    current = [n["id"] for n in sh.gql(
        "query($id: ID!) { product(id: $id) { media(first: 250) { nodes { id } } } }",
        {"id": pid})["product"]["media"]["nodes"]]
    if current == gallery and not changed:
        ok(f"gallery already up to date ({len(gallery)} slides)")
        return
    to_add = [g for g in gallery if g not in current]
    to_remove = [c for c in current if c not in gallery]
    updates = [{"id": g, "referencesToAdd": [pid]} for g in to_add] + \
              [{"id": c, "referencesToRemove": [pid]} for c in to_remove]
    for i in range(0, len(updates), 25):
        res = sh.gql("""mutation($files: [FileUpdateInput!]!) {
            fileUpdate(files: $files) { files { id } userErrors { field message } } }""",
                     {"files": updates[i:i + 25]})["fileUpdate"]
        if res["userErrors"]:
            stop("gallery update: " + "; ".join(e["message"] for e in res["userErrors"]))
    moves = [{"id": g, "newPosition": str(pos)} for pos, g in enumerate(gallery)]
    res = sh.gql("""mutation($id: ID!, $moves: [MoveInput!]!) {
        productReorderMedia(id: $id, moves: $moves) { userErrors { field message } } }""",
                 {"id": pid, "moves": moves})["productReorderMedia"]
    if res["userErrors"]:
        warn("gallery order: " + "; ".join(e["message"] for e in res["userErrors"]))
    ok(f"gallery: {len(gallery)} slides in order" +
       (f" · {len(to_remove)} old image(s) detached (still in Content > Files)" if to_remove else ""))


# ---------------------------------------------------------------- 5 LIVE CHECK
def live_check(shop: str, handle: str, manifest: dict) -> None:
    slug = manifest["slug"]
    ids = [e["id"] for e in manifest["images"] if e.get("kind") == "section"]
    url = f"https://{shop}/products/{handle}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (APEX live check)"})
    html, final = "", url
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                html, final = r.read().decode("utf-8", errors="replace"), r.geturl()
            break
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 2:
                warn(f"live check skipped: the page did not load ({e})")
                return
            time.sleep(5)
    if "/password" in final:
        warn("live check skipped: the store is password-protected")
        return
    showing = [i for i in ids if re.search(re.escape(f"{slug}_{i}") + r"[^\"'\s]*\.(png|jpg|webp)", html)]
    (ok if len(showing) == len(ids) else warn)(f"live check: {len(showing)}/{len(ids)} section images showing on {final}")
    missing = [i for i in ids if i not in showing]
    if missing:
        info("not on the page yet: " + ", ".join(missing) +
             " (Shopify may still be processing; check again in a minute. If it stays, the page section "
             "has no self-filling slot for them: rebuild the section with PageEngine)")


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="APEX Image Factory: generate and upload the page images.")
    ap.add_argument("target", help="<slug>, or the path to <slug>-images.json")
    ap.add_argument("--photos")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--redo")
    ap.add_argument("--only")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--quality")
    ap.add_argument("--key-quality")
    ap.add_argument("--text", choices=["none"])
    ap.add_argument("--handle")
    ap.add_argument("--skip-live-check", action="store_true")
    args = ap.parse_args()

    say(f"\n=== APEX | Image Factory | {Path(args.target).name} ===")
    stage("1 SET UP")
    slug, folder = set_up(args.target, args.photos)
    manifest = read_json(folder / "manifest.json")
    if not manifest or not manifest.get("images"):
        stop(f"products/{slug}/manifest.json is empty or broken", "run again with the path to the images.json")
    manifest.setdefault("slug", slug)
    store = manifest.get("store") or "default"
    handle = args.handle or slug
    uploading = not (args.no_upload or args.test)

    stage("2 PREFLIGHT")
    key, model, refs = preflight_openai(folder, manifest)
    sh = shop = product = None
    if uploading:
        sh, shop, product = preflight_shopify(store, handle)

    stage("3 GENERATE")
    failed = generate(folder, manifest, args, key, model, refs)
    if failed:
        say(f"\n  {len(failed)} image(s) failed: {', '.join(failed)}. Run the same command again: "
            "only the missing ones are made. The same image failing twice = report its error.")
        sys.exit(1)
    if args.test:
        ok(f"test images in products/{slug}/test/ (nothing uploaded)")
        return
    if not uploading:
        ok("generated. Upload with: py factory.py " + slug + " --yes")
        return

    if not args.yes:
        answer = input(f"\nUpload to {shop} now? [y/N] ").strip().lower()
        if answer not in ("y", "yes", "j", "ja"):
            say("Not uploaded. Run again with --yes to upload.")
            return
    stage("4 UPLOAD")
    upload(sh, folder, manifest, product)
    if not args.skip_live_check:
        stage("5 LIVE CHECK")
        live_check(shop, handle, manifest)
    real = [e["id"] for e in manifest["images"] if not e.get("generate")]
    if real:
        info("real photos to add by hand: " + ", ".join(real) +
             f" (or put them in products/{slug}/real/ and run the upload again)")
    say(f"\nDone: {slug}")


if __name__ == "__main__":
    main()
