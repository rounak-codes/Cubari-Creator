import os
import json
import re

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".avif")

def natural_key(s):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", s)]

def strip_prefix(folder_name):
    """
    Converts:
    '01 - Sidney'                   -> 'Sidney'
    '09.5 - Sidney’s Photoshoot'    -> 'Sidney’s Photoshoot'
    '12 - Janice's Date'            -> "Janice's Date"
    """
    # remove leading numbers, dots, spaces, hyphens
    return re.sub(r"^[0-9\\. ]+- ?", "", folder_name).strip()

cubari_path = input("Enter cubari.json path: ").strip()
base_folder = input("Enter base folder containing chapter folders: ").strip()

print("\n📌 Reading cubari.json ...")
with open(cubari_path, "r", encoding="utf-8") as f:
    cubari = json.load(f)

record = {
    "images": {},
    "chapters_completed": []
}

chapters = cubari.get("chapters", {})

# Map stripped folder names → actual folder name
print("📁 Scanning chapter folders...")
folder_map = {}
for folder in os.listdir(base_folder):
    full_path = os.path.join(base_folder, folder)
    if os.path.isdir(full_path):
        stripped = strip_prefix(folder)
        folder_map[stripped] = folder

# ---- Main Loop ----
for chap_index, chap_data in chapters.items():
    title = chap_data.get("title", "").strip()
    record["chapters_completed"].append(title)

    # find folder that matches this title
    if title not in folder_map:
        print(f"⚠ Could not find folder for: '{title}'")
        continue

    folder_name = folder_map[title]
    chapter_path = os.path.join(base_folder, folder_name)

    # list local images
    local_imgs = sorted(
        (
            f for f in os.listdir(chapter_path)
            if f.lower().endswith(IMAGE_EXTS)
        ),
        key=natural_key
    )

    # get cubari URLs
    groups = chap_data.get("groups", {})
    if not groups:
        print(f"⚠ No URL group for chapter: {title}")
        continue

    urls = next(iter(groups.values()))

    if len(local_imgs) != len(urls):
        print(f"⚠ Image count mismatch for {title}: local={len(local_imgs)}, cubari={len(urls)}")

    # map images to URLs by index
    for i, img in enumerate(local_imgs):
        if i >= len(urls):
            break

        url = urls[i]
        rel_path = f"{folder_name}/{img}"

        ext = os.path.splitext(img)[1].lstrip(".").lower()

        # record entry
        record["images"][rel_path] = {
            "url": url,
            "ext": ext
        }

output_path = os.path.join(base_folder, "upload_record.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(record, f, indent=2)

print("\n✅ upload_record.json successfully generated!")
print("📄 Saved at:", output_path)
