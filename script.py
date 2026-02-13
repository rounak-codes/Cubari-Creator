import os
import requests
import json
import time
import zipfile
import re
from PIL import Image
import send2trash

# ---------------- User Inputs ----------------
title_name = input("Enter title name: ").strip()
uploader_name = input("Enter uploader name: ").strip()
series_description = input("Enter series description: ").strip()
artist_name = input("Enter artist name: ").strip()
author_name = input("Enter author name: ").strip()
cover_url = input("Enter cover image URL (catbox link): ").strip()
status_value = input("Enter series status: ").strip().capitalize()

base_folder = input("Enter path to main folder containing all chapter folders: ").strip()
cubari_json_path = input("Enter path to existing cubari.json (leave empty to skip): ").strip()

cbz_folder = os.path.join(base_folder, "CBZ_Files")
os.makedirs(cbz_folder, exist_ok=True)

# ---------------- Config ----------------
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".avif")

def natural_key(s):
    """Natural sort key (numbers as ints)."""
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", s)]

# ---------------- Load existing Cubari (if provided) ----------------
cubari_lookup_by_title = {}
cubari_lookup_by_index = {}

if cubari_json_path:
    try:
        with open(cubari_json_path, "r", encoding="utf-8") as f:
            existing_cubari = json.load(f)
    except Exception as e:
        print("Failed to read existing cubari.json:", e)
        existing_cubari = {}

    for key, chapter_data in existing_cubari.get("chapters", {}).items():
        groups = chapter_data.get("groups", {})
        urls = None
        if groups:
            first_group = next(iter(groups.values()))
            if isinstance(first_group, list):
                urls = first_group
        if not urls:
            continue
        title = chapter_data.get("title", "")
        cubari_lookup_by_title[title] = urls
        cubari_lookup_by_index[str(key)] = urls

    print(f"Loaded {len(cubari_lookup_by_title)} chapters from Cubari JSON.")

# ---------------- Load or init upload_record.json ----------------
record_file = os.path.join(base_folder, "upload_record.json")

if os.path.exists(record_file):
    try:
        with open(record_file, "r", encoding="utf-8") as f:
            uploaded_record = json.load(f)
    except Exception as e:
        print("Failed to read upload_record.json, starting fresh:", e)
        uploaded_record = {}
else:
    uploaded_record = {}

uploaded_record.setdefault("images", {})
uploaded_record.setdefault("chapters_completed", [])

# ---------------- helper: upload with retry ----------------
def upload_file(fp, timeout=120):
    """Upload a single file to catbox; returns the returned URL (str). Retries on failure."""
    while True:
        try:
            with open(fp, "rb") as f:
                r = requests.post(
                    "https://catbox.moe/user/api.php",
                    data={"reqtype": "fileupload"},
                    files={"fileToUpload": f},
                    timeout=timeout
                )
            if r.status_code == 200:
                return r.text.strip()
            print(f"Upload error {r.status_code}, retrying in 5s...")
        except Exception as e:
            print("Upload exception:", e, "- retrying in 5s")
            time.sleep(5)

# ---------------- AVIF → WEBP conversion (only AVIF) ----------------
def convert_to_webp(path):
    """Convert only .avif → .webp and remove original AVIF (send2trash)."""
    if not path.lower().endswith(".avif"):
        return path
    try:
        im = Image.open(path).convert("RGB")
        newp = os.path.splitext(path)[0] + ".webp"
        im.save(newp, "webp", quality=100)
        try:
            send2trash.send2trash(path)
        except Exception:
            # fallback to remove if send2trash fails
            try:
                os.remove(path)
            except Exception:
                pass
        print("Converted AVIF → WEBP:", os.path.basename(path))
        return newp
    except Exception as e:
        print("⚠ AVIF conversion failed for", path, "error:", e)
        return path

# ---------------- create CBZ (include all image extensions) ----------------
def create_cbz(chapter_path, chapter_name):
    out = os.path.join(cbz_folder, f"{chapter_name}.cbz")
    imgs = sorted(
        (
            f for f in os.listdir(chapter_path)
            if f.lower().endswith(IMAGE_EXTS)
        ),
        key=natural_key
    )
    with zipfile.ZipFile(out, "w") as cbz:
        ci = os.path.join(chapter_path, "ComicInfo.xml")
        if os.path.exists(ci):
            cbz.write(ci, arcname="ComicInfo.xml")
        for f in imgs:
            fp = os.path.join(chapter_path, f)
            if os.path.exists(fp):
                cbz.write(fp, arcname=f)
    print("Created CBZ:", out, "with", len(imgs), "pages")

# ---------------- new Cubari JSON to build ----------------
cubari_data = {
    "title": title_name,
    "description": series_description,
    "artist": artist_name,
    "author": author_name,
    "cover": cover_url,
    "status": status_value,
    "chapters": {}
}

# ---------------- main loop ----------------
chapter_dirs = sorted(
    (
        d for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
        and d != os.path.basename(cbz_folder)
    ),
    key=natural_key
)

chapter_index = 1
for chapter in chapter_dirs:
    chapter_path = os.path.join(base_folder, chapter)

    # skip if complete
    if chapter in uploaded_record["chapters_completed"]:
        print("\n⏩ Skipping completed chapter:", chapter)
        chapter_index += 1
        continue

    local_imgs = sorted(
        (
            f for f in os.listdir(chapter_path)
            if f.lower().endswith(IMAGE_EXTS)
        ),
        key=natural_key
    )

    print(f"\n📘 Chapter {chapter_index}: {chapter} — {len(local_imgs)} images")

    # find existing URLs for this chapter (strict index reuse)
    if chapter in cubari_lookup_by_title:
        existing_urls = cubari_lookup_by_title[chapter]
    elif str(chapter_index) in cubari_lookup_by_index:
        existing_urls = cubari_lookup_by_index[str(chapter_index)]
    else:
        existing_urls = None

    urls_out = []

    if existing_urls:
        print(f"ℹ Found {len(existing_urls)} Cubari URLs — reusing those for the first {len(existing_urls)} pages.")
        # Reuse by index: for i < len(existing_urls) reuse that URL
        for i, img in enumerate(local_imgs):
            ip = os.path.join(chapter_path, img)
            ip = convert_to_webp(ip)  # convert if avif; returns final path

            rel = os.path.relpath(ip, base_folder).replace("\\", "/")
            ext = os.path.splitext(ip)[1].lstrip(".").lower()

            if i < len(existing_urls):
                url = existing_urls[i]
                urls_out.append(url)
                uploaded_record["images"][rel] = {"url": url, "ext": ext}
                continue

            # beyond existing URLs → check record else upload
            if rel in uploaded_record["images"]:
                urls_out.append(uploaded_record["images"][rel]["url"])
            else:
                print("⬆ Uploading new image (beyond existing URLs):", ip)
                new_url = upload_file(ip)
                urls_out.append(new_url)
                uploaded_record["images"][rel] = {"url": new_url, "ext": ext}

    else:
        # normal chapter upload
        for img in local_imgs:
            ip = convert_to_webp(os.path.join(chapter_path, img))
            rel = os.path.relpath(ip, base_folder).replace("\\", "/")
            ext = os.path.splitext(ip)[1].lstrip(".").lower()

            if rel in uploaded_record["images"]:
                urls_out.append(uploaded_record["images"][rel]["url"])
                continue

            print("⬆ Uploading:", ip)
            url = upload_file(ip)
            urls_out.append(url)
            uploaded_record["images"][rel] = {"url": url, "ext": ext}

    # final checks
    if len(urls_out) != len(local_imgs):
        print(f"⚠ MISMATCH: local images={len(local_imgs)} but urls_out={len(urls_out)}; check for missing uploads or filename changes.")

    # Build Cubari JSON chapter entry
    cubari_data[str(chapter_index)] = {
        "title": chapter,
        "volume": "1",
        "last_updated": str(int(time.time())),
        "groups": {uploader_name: urls_out}
    }

    # Create CBZ
    create_cbz(chapter_path, chapter)

    # mark done
    uploaded_record["chapters_completed"].append(chapter)

    # persist progress after each chapter
    try:
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(uploaded_record, f, indent=2)
    except Exception as e:
        print("Failed to write upload_record.json:", e)

    chapter_index += 1

# ---------------- Write final cubari JSON ----------------
out_json = os.path.join(base_folder, f"{title_name.replace(' ', '_')}_cubari.json")
try:
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(cubari_data, f, indent=2)
    print("\n✅ DONE — No reuploads for old images.")
    print("📄 Cubari JSON:", out_json)
    print("📄 upload_record.json:", record_file)
except Exception as e:
    print("Failed to write final cubari json:", e)
