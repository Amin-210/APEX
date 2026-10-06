#!/usr/bin/env python3
"""
apex_watch.py  -  APEX v2: from the Google Drive hand-off to a finished live page, by itself.

The claude.ai chat (PageEngine) saves each build into Google Drive:  APEX/<slug>/
  <slug>-product.json, product-description-<slug>.liquid, <slug>-image-prompts.md,
  <slug>-review-frames.md (+ build notes), and READY.txt LAST (it lists the files, the intake folder
  on a line "inbox: <name>", and for a changed build a line "rev: <n>").
Google Drive for Desktop syncs that folder to this PC. This watcher finds the work and runs:

  A  COLLECT      files -> incoming/<slug>/, photos from Drive APEX/_inbox/<name>/photos/ (copied,
                  never moved; extra/ is ignored) -> Desktop/<slug>-photos. Old way still works:
                  photos in Desktop/apex-inbox are used when the Drive folder has none.
  B  MANIFEST     <slug>-images.json built from the image prompts (build-image-manifest.py)
  C  PRODUCT+PAGE product_setup.py --install-page (product, prices, tax/inventory/shipping OFF,
                  published, own template, page installed and pushed live)
  D  IMAGES       run-factory.ps1 <slug> (generate + upload + live check)

What starts a run (nothing to type in PowerShell):
  new       a new APEX/<slug>/ folder with READY.txt
  revision  READY.txt changed (the chat saved changed files and a new "rev: <n>" line). When image
            prompts changed, the old factory product folder is set aside so every image is made again
            from the new prompts; when only the page text changed, the images are kept.
  retry     a RETRY.txt file in APEX/<slug>/ (the chat can create it, or: .\\apex-watch.ps1 -Retry <slug>)
  resume    a run that was cut off (PC restarted, window closed) continues when the watcher starts

The output of every stage shows in this window, goes to apex-logs/<slug>.log, and is copied to
Google Drive: APEX/<slug>/STATUS.txt (stage + result) and APEX/<slug>/apex-log.txt (the full output).

Usage (apex-watch.ps1 calls this):
  py apex_watch.py                 watch: check every 30 seconds
  py apex_watch.py --once          check once and exit
  py apex_watch.py --retry <slug>  run that product again (hands it to the running watcher if there is one)
Settings: APEX_DRIVE_DIR (the synced APEX folder; found automatically when not set).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import string
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "apex-state"
LOGS = HERE / "apex-logs"
INBOX = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop" / "apex-inbox"
DESKTOP = INBOX.parent
ROW_INBOX = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop" / "apex-inbox"  # sheet mode: <row>\ folders
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DRIVE_ROOTS = ["My Drive", "Meine Ablage", "Mon Drive", "Mi unidad"]
MAX_RESUMES = 2
_LOG = None          # open log file of the product being run
_MUTEX = None        # keeps the single-instance lock alive


# ---------------------------------------------------------------- output
def _log_write(text):
    if _LOG is not None:
        try:
            _LOG.write(text)
            _LOG.flush()
        except OSError:
            pass


def say(msg, color=None):
    codes = {"cyan": "36", "green": "32", "red": "31", "yellow": "33", "magenta": "35"}
    print(f"\033[{codes[color]}m{msg}\033[0m" if color else msg, flush=True)
    _log_write(msg + "\n")


def notify(title, text):
    """Small Windows notification (bottom right). Never blocks, never fails the run."""
    if os.name != "nt":
        return
    esc = lambda s: str(s).replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing;"
          "$n = New-Object System.Windows.Forms.NotifyIcon;"
          "$n.Icon = [System.Drawing.SystemIcons]::Information; $n.Visible = $true;"
          f"$n.ShowBalloonTip(10000, '{esc(title)}', '{esc(text)}', 'Info'); Start-Sleep 11; $n.Dispose()")
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=0x08000000)  # CREATE_NO_WINDOW
    except OSError:
        pass


def disable_quickedit():
    """Windows console 'QuickEdit': one click in the window pauses everything until Enter is
    pressed. Switch it off for this window, so a run never waits for a key."""
    if os.name != "nt":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-10)                  # STD_INPUT_HANDLE
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, (mode.value | 0x0080) & ~0x0040 & ~0x0020)  # +EXTENDED -QUICK_EDIT -INSERT
    except Exception:
        pass


def other_watcher_running():
    """True when another APEX watcher already runs on this PC (Windows named mutex)."""
    global _MUTEX
    if os.name != "nt":
        return False
    try:
        import ctypes
        k = ctypes.windll.kernel32
        _MUTEX = k.CreateMutexW(None, False, "Local\\APEX-watcher")
        return k.GetLastError() == 183        # ERROR_ALREADY_EXISTS
    except Exception:
        return False


# ---------------------------------------------------------------- Drive + state
def find_drive_dir():
    env = os.environ.get("APEX_DRIVE_DIR")
    if env:
        return Path(env)
    cands = []
    for letter in string.ascii_uppercase:
        for root in DRIVE_ROOTS:
            cands.append(Path(f"{letter}:\\") / root / "APEX")
    home = Path(os.environ.get("USERPROFILE", str(Path.home())))
    for root in DRIVE_ROOTS:
        cands.append(home / "Google Drive" / root / "APEX")
        cands.append(home / "Google Drive" / "APEX")
    for c in cands:
        try:
            if c.is_dir():
                return c
        except OSError:
            pass
    return None


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


def read_state(slug):
    p = STATE / f"{slug}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (OSError, ValueError):
        return {}


def write_state(slug, **kw):
    STATE.mkdir(exist_ok=True)
    s = read_state(slug)
    s.update(kw, updated=datetime.now().isoformat(timespec="seconds"))
    (STATE / f"{slug}.json").write_text(json.dumps(s, indent=2), encoding="utf-8")


def read_ready(folder):
    """READY.txt: one file name per line, plus settings as 'key: value' (inbox: <name>, rev: <n>).
    Returns (file names, settings)."""
    names, settings = [], {}
    for line in (folder / "READY.txt").read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-z_]+):\s*(.+)$", line)
        if m:
            settings[m.group(1)] = m.group(2).strip()
        else:
            names.append(line)
    return names, settings


def ready_sig(folder):
    """Fingerprint of READY.txt. The chat rewrites READY.txt (new rev line) after saving changes."""
    text = (folder / "READY.txt").read_text(encoding="utf-8-sig")
    norm = "\n".join(l.strip() for l in text.splitlines() if l.strip())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def ready_files(folder):
    """Returns (file names, missing or still-syncing file names, settings)."""
    names, settings = read_ready(folder)
    missing = [n for n in names if not (folder / n).exists() or (folder / n).stat().st_size == 0]
    return names, missing, settings


def drive_status(folder, slug, stage, status, detail=""):
    """STATUS.txt in the Drive product folder: what the watcher is doing, readable from the chat."""
    lines = [f"product: {slug}", f"status: {status}", f"stage: {stage}",
             f"time: {datetime.now():%Y-%m-%d %H:%M}"]
    if detail:
        lines.append(f"detail: {detail}")
    try:
        (folder / "STATUS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


def drive_log(folder, slug):
    """Copy this product's log into the Drive folder (apex-log.txt)."""
    src = LOGS / f"{slug}.log"
    try:
        if src.exists():
            shutil.copy2(src, folder / "apex-log.txt")
    except OSError:
        pass


# ---------------------------------------------------------------- running the steps
def run(cmd, stage):
    """Run one step. Its output shows live in this window AND goes to the log. The keyboard stays
    connected, but nothing in APEX asks for a key."""
    say(f"  $ {' '.join(cmd)}")
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    p = subprocess.Popen(cmd, cwd=str(HERE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    fd = p.stdout.fileno()
    while True:
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        text = chunk.decode("utf-8", errors="replace")
        sys.stdout.write(text)
        sys.stdout.flush()
        _log_write(text)
    code = p.wait()
    if code != 0:
        raise RuntimeError(f"{stage} stopped (exit code {code}), see the output above")


def image_entries(path):
    """{image id: entry} from a <slug>-images.json, or {} when there is none."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return {e.get("id"): e for e in data.get("images", []) if e.get("id")}
    except (OSError, ValueError):
        return {}


def image_sig(entries):
    """{image id: fingerprint of its prompt and settings}."""
    return {i: hashlib.sha1(json.dumps(e, sort_keys=True).encode("utf-8")).hexdigest()[:12]
            for i, e in entries.items()}


def process(folder, slug, reason):
    global _LOG
    LOGS.mkdir(exist_ok=True)
    _LOG = open(LOGS / f"{slug}.log", "a", encoding="utf-8")
    prev = read_state(slug)
    try:
        _process(folder, slug, reason, prev)
    finally:
        drive_log(folder, slug)
        _LOG.close()
        _LOG = None


def _process(folder, slug, reason, prev):
    say(f"\n{'=' * 64}\n=== APEX | {slug} | {reason} | {datetime.now():%Y-%m-%d %H:%M} ===", "magenta")
    notify("APEX started", f"{slug} ({reason})")
    for old in ("DONE.txt",):
        try:
            (folder / old).unlink()
        except OSError:
            pass

    def stage(name):
        write_state(slug, status="running", stage=name, reason=reason)
        drive_status(folder, slug, name, "running", reason)
        drive_log(folder, slug)

    # ---------------------------------------------------------------- A COLLECT
    stage("A COLLECT")
    say("\n=== A  COLLECT ===", "cyan")
    names, missing, settings = ready_files(folder)
    if missing:
        raise RuntimeError("still syncing, missing: " + ", ".join(missing))
    inbox_name = settings.get("inbox", "").strip().strip("/").replace("_inbox/", "")
    intake = folder.parent / "_inbox" / inbox_name if inbox_name else None
    if intake is not None and not intake.is_dir():
        raise RuntimeError(f"still syncing, missing: the intake folder _inbox/{inbox_name}")
    inbox = HERE / "incoming" / slug
    inbox.mkdir(parents=True, exist_ok=True)
    images_json = inbox / f"{slug}-images.json"
    old_images = image_entries(images_json)          # the last run's image list, for revisions
    for n in names:
        shutil.copy2(folder / n, inbox / n)
        say(f"  found   {n}", "green")
    if settings.get("rev"):
        say(f"  revision {settings['rev']}", "green")
    manifest = inbox / f"{slug}-product.json"
    if not manifest.exists():
        raise RuntimeError(f"{slug}-product.json is not in the Drive folder")
    for liq in inbox.glob("*.liquid"):
        n_fixed = fix_hash_comments(liq)
        if n_fixed:
            say(f"  fixed {n_fixed} {{# #}} note(s) in {liq.name} (Shopify would print them as text)", "yellow")

    photos_dir = DESKTOP / f"{slug}-photos"
    photos_dir.mkdir(exist_ok=True)
    source = None
    photos_row = settings.get("photos_row", "").strip()
    if photos_row and not photos_row.isdigit():
        raise RuntimeError(f"READY.txt has 'photos_row: {photos_row}', which is not a row number")
    row_dir = ROW_INBOX / photos_row if photos_row else None
    if row_dir is not None and row_dir.is_dir():        # sheet mode: Desktop\apex-inbox\<row>\ (kept)
        pics = [f for f in sorted(row_dir.iterdir()) if f.is_file() and f.suffix.lower() in PHOTO_EXT]
        for f in pics:
            shutil.copy2(f, photos_dir / f.name)       # copy: the row folder keeps its photos
            source = row_dir
        skipped = [f.name for f in row_dir.iterdir() if f.is_file() and f.suffix.lower() not in PHOTO_EXT]
        if skipped:
            say("  skipped (not .jpg/.png/.webp, e.g. iPhone .heic): " + ", ".join(skipped), "yellow")
    drive_sources = [d for d in ((intake / "photos") if intake else None, folder / "photos") if d and d.is_dir()]
    for src_dir in drive_sources:
        pics = [f for f in sorted(src_dir.iterdir()) if f.is_file() and f.suffix.lower() in PHOTO_EXT]
        if pics:
            for f in pics:
                shutil.copy2(f, photos_dir / f.name)   # copy: the Drive folder keeps its photos
            source = src_dir
            break
    if source is None and not photos_row and INBOX.is_dir():               # old way: Desktop\apex-inbox
        for f in sorted(INBOX.iterdir()):
            if f.is_file() and f.suffix.lower() in PHOTO_EXT:
                shutil.move(str(f), str(photos_dir / f.name))
                source = INBOX
    have = [f for f in photos_dir.iterdir() if f.suffix.lower() in PHOTO_EXT]
    if not have:
        where = (str(ROW_INBOX / photos_row) + " (the product's row number in APEX Products)" if photos_row
                 else f"_inbox/{inbox_name}/photos in Google Drive" if inbox_name else str(INBOX))
        raise RuntimeError(f"no product photos: put 1-3 photos (.jpg/.png/.webp) in {where}, "
                           f"then add RETRY.txt to APEX/{slug}/ (or tell Claude: APEX retry {slug})")
    say(f"  photos: {len(have)} in {photos_dir}" + (f" (from {source})" if source else ""), "green")
    if intake is not None and (intake / "photos").is_dir():
        skipped = [f.name for f in (intake / "photos").iterdir()
                   if f.is_file() and f.suffix.lower() not in PHOTO_EXT]
        if skipped:
            say("  skipped (not .jpg/.png/.webp, e.g. iPhone .heic): " + ", ".join(skipped), "yellow")

    # ---------------------------------------------------------------- B MANIFEST
    stage("B MANIFEST")
    say("\n=== B  IMAGE MANIFEST ===", "cyan")
    prompts = inbox / f"{slug}-image-prompts.md"
    launch = json.loads(manifest.read_text(encoding="utf-8-sig"))
    store = launch.get("store", "default")
    if prompts.exists():
        cmd = [sys.executable, str(HERE / "build-image-manifest.py"), str(prompts), "--slug", slug,
               "--store", store, "--liquid", str(inbox / f"product-description-{slug}.liquid")]
        if launch.get("language"):
            cmd += ["--language", launch["language"]]
        run(cmd, "image manifest")
    elif not images_json.exists():
        raise RuntimeError(f"neither {prompts.name} nor {images_json.name} is in the Drive folder")
    # run-factory looks in Downloads/Desktop/Documents; give it the fresh files on the Desktop
    for f in (images_json, prompts):
        if f.exists():
            shutil.copy2(f, DESKTOP / f.name)

    # images: which prompts changed since the factory made this product's images
    skip_images = False
    new_sig = image_sig(image_entries(images_json))
    base_sig = prev.get("images_sig") or image_sig(old_images)
    if reason != "new" and base_sig:                 # revision, retry or resume
        changed = sorted(i for i in set(base_sig) | set(new_sig) if base_sig.get(i) != new_sig.get(i))
        factory_product = HERE / "products" / slug
        if changed:
            say(f"  image prompts changed: {', '.join(changed)}", "yellow")
            if factory_product.is_dir():
                base = f"{slug}-old-{datetime.now():%Y%m%d-%H%M%S}"
                aside, n = HERE / "products" / base, 1
                while aside.exists():
                    n += 1
                    aside = HERE / "products" / f"{base}-{n}"
                factory_product.rename(aside)
                say(f"  old images set aside in {aside.name}; every image is made again from the new prompts", "yellow")
            write_state(slug, images_sig=new_sig)    # the factory now works from the new prompts
        elif reason == "revision" and prev.get("status") == "done":
            skip_images = True
            say("  image prompts unchanged: the images on the page are kept", "green")

    # ---------------------------------------------------------------- C PRODUCT + PAGE
    stage("C PRODUCT+PAGE")
    say("\n=== C  PRODUCT SETUP + PAGE INSTALL ===", "cyan")
    run([sys.executable, str(HERE / "product_setup.py"), str(manifest), "--install-page"], "product setup")

    # ---------------------------------------------------------------- D IMAGES
    if skip_images:
        say("\n=== D  IMAGE FACTORY: skipped (images unchanged) ===", "cyan")
    else:
        stage("D IMAGES")
        say("\n=== D  IMAGE FACTORY ===", "cyan")
        run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(HERE / "run-factory.ps1"), slug, "-Photos", str(photos_dir)], "image factory")
        write_state(slug, images_sig=new_sig)

    write_state(slug, status="done", stage="finished", error="", resumes=0)
    drive_status(folder, slug, "finished", "done", reason)
    stamp = f"finished {datetime.now():%Y-%m-%d %H:%M}\n"
    (folder / "DONE.txt").write_text(stamp, encoding="utf-8")
    if intake is not None and intake.is_dir():
        (intake / "DONE.txt").write_text(f"built as {slug}\n" + stamp, encoding="utf-8")
    say(f"\n=== APEX | {slug} | DONE: live page with images ===", "green")
    notify("APEX done", f"{slug}: live page with images")


# ---------------------------------------------------------------- deciding what to run
def decide(folder, slug):
    """Returns the reason to run this folder now, or None."""
    st = read_state(slug)
    status = st.get("status")
    sig = ready_sig(folder)
    if (folder / "RETRY.txt").exists():
        return "retry"
    if not st or status == "waiting":
        return st.get("reason") or "new"
    if status == "stale":
        return "resume"
    if status in ("done", "failed"):
        if not st.get("sig"):                        # state from an older watcher: remember, do not rerun
            write_state(slug, sig=sig)
            return None
        if sig != st["sig"]:
            return "revision"
    return None


def run_folder(folder, slug, reason):
    sig = ready_sig(folder)
    if reason == "retry":
        try:
            (folder / "RETRY.txt").unlink()
        except OSError:
            pass
    if reason == "resume":
        write_state(slug, resumes=read_state(slug).get("resumes", 0) + 1)
    try:
        process(folder, slug, reason)
        write_state(slug, sig=sig)
    except RuntimeError as e:
        if str(e).startswith("still syncing"):
            say(f"  {slug}: {e} (waiting for Google Drive)", "yellow")
            write_state(slug, status="waiting", stage="A COLLECT", reason=reason)
            drive_status(folder, slug, "A COLLECT", "waiting", str(e))
            return
        fail_run(folder, slug, sig, str(e))
    except Exception as e:                           # never let one product stop the watcher
        fail_run(folder, slug, sig, f"{type(e).__name__}: {e}")


def fail_run(folder, slug, sig, err):
    stage = read_state(slug).get("stage", "")
    write_state(slug, status="failed", error=err, sig=sig)
    drive_status(folder, slug, stage, "failed", err + "  |  fix it, then add RETRY.txt to this folder "
                 f"(or tell Claude: APEX retry {slug})")
    say(f"\n  X {slug}: {err}", "red")
    say(f"  -> fix it, then add RETRY.txt to APEX/{slug}/ in Google Drive (or: .\\apex-watch.ps1 -Retry {slug})", "yellow")
    notify("APEX stopped", f"{slug}: {err[:180]}")


def ready_time(folder):
    """When READY.txt arrived: products run in hand-off order (batch builds keep their order)."""
    try:
        return (folder / "READY.txt").stat().st_mtime
    except OSError:
        return float("inf")


def scan(drive, only=None, force_reason=None):
    folders = [p for p in drive.iterdir() if p.is_dir() and not p.name.startswith("_")]
    for folder in sorted(folders, key=lambda p: (ready_time(p), p.name)):
        slug = folder.name
        if only and slug != only:
            continue
        try:
            if not (folder / "READY.txt").exists():
                continue
            reason = force_reason or decide(folder, slug)
        except OSError:
            continue                                 # Drive still copying this folder
        if reason:
            run_folder(folder, slug, reason)


def mark_stale_runs():
    """A run still marked 'running' when the watcher starts was cut off: resume it (at most
    MAX_RESUMES times in a row, then it is marked failed)."""
    if not STATE.is_dir():
        return
    for p in STATE.glob("*.json"):
        slug = p.stem
        st = read_state(slug)
        if st.get("status") != "running":
            continue
        if st.get("resumes", 0) >= MAX_RESUMES:
            write_state(slug, status="failed", error="cut off several times; see apex-logs")
        else:
            write_state(slug, status="stale")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--retry")
    ap.add_argument("--interval", type=int, default=30)
    a = ap.parse_args()
    if os.name == "nt":
        os.system("")  # enable colours in the Windows console
    disable_quickedit()
    INBOX.mkdir(parents=True, exist_ok=True)
    drive = find_drive_dir()
    if not drive:
        say("X Google Drive folder 'APEX' not found on this PC.", "red")
        say("  -> install Google Drive for Desktop, sign in with the Google account used in claude.ai,", "yellow")
        say("     let it sync, or set it by hand: setx APEX_DRIVE_DIR \"G:\\My Drive\\APEX\"", "yellow")
        sys.exit(1)

    busy = other_watcher_running()
    if a.retry:
        folder = drive / a.retry
        if not (folder / "READY.txt").exists():
            say(f"X APEX/{a.retry}/READY.txt not found in Google Drive", "red")
            sys.exit(1)
        if busy:
            (folder / "RETRY.txt").write_text("retry\n", encoding="utf-8")
            say(f"The APEX watcher is already running: it picks up {a.retry} within 30 seconds (see its window).", "green")
            return
        scan(drive, only=a.retry, force_reason="retry")
        return
    if busy:
        say("The APEX watcher is already running on this PC (see its window or the taskbar). Nothing to do.", "green")
        return

    say(f"APEX watcher | Drive: {drive} | intake: {drive / '_inbox'}", "magenta")
    mark_stale_runs()
    while True:
        try:
            scan(drive)
        except Exception as e:                       # e.g. Drive offline for a moment
            say(f"  scan problem: {type(e).__name__}: {e} (trying again)", "yellow")
        if a.once:
            return
        say(f"  [{datetime.now():%H:%M:%S}] waiting for new products...")
        time.sleep(a.interval)


if __name__ == "__main__":
    main()
