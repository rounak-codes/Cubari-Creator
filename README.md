---

# 📚 Cubari Creator

A fully automated Python toolchain to:

* ✅ Upload manga/comic chapters to **Catbox**
* ✅ Generate Cubari-compatible JSON
* ✅ Resume uploads without reuploading old pages
* ✅ Convert `.avif` → `.webp` automatically
* ✅ Create CBZ files for every chapter
* ✅ Merge multiple CBZs into a single anthology
* ✅ Regenerate `upload_record.json` from an existing Cubari project

Built for scanlators, archivists, and Cubari users.

---

# 🚀 Features

## 🔹 Smart Uploading

* Uploads images to `catbox.moe`
* Retries automatically on failure
* Skips already uploaded images
* Supports resume via `upload_record.json`

## 🔹 AVIF Support

* Converts `.avif` → `.webp`
* Removes original AVIF safely

## 🔹 Cubari JSON Generator

Creates fully structured JSON:

```json
{
  "title": "...",
  "description": "...",
  "artist": "...",
  "author": "...",
  "cover": "...",
  "status": "...",
  "chapters": { ... }
}
```

## 🔹 CBZ Creator

Each chapter automatically generates:

```
CBZ_Files/Chapter_Name.cbz
```

## 🔹 CBZ Anthology Merger

Merge multiple `.cbz` files into one properly ordered CBZ.

## 🔹 Record Rebuilder

Rebuild `upload_record.json` from an existing Cubari JSON file.

---

# 📦 Project Structure

```
Project Folder/
│
├── Chapter 1/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
│
├── Chapter 2/
│
├── CBZ_Files/
│
├── upload_record.json
│
├── script.py          ← Main uploader :contentReference[oaicite:3]{index=3}
├── update.py          ← Record generator :contentReference[oaicite:4]{index=4}
└── rename.py          ← CBZ merger :contentReference[oaicite:5]{index=5}
```

---

# 🛠 Installation

## 1️⃣ Install Python 3.9+

## 2️⃣ Install Dependencies

```bash
pip install requests pillow send2trash
```

---

# 📘 How To Use

---

# 🔥 1️⃣ Main Upload Script

**File:** `script.py` 

### Run:

```bash
python script.py
```

### You Will Be Asked:

* Title name
* Uploader name (group name)
* Description
* Artist
* Author
* Cover image URL (Catbox link)
* Status (Ongoing / Completed)
* Base folder path
* Existing cubari.json path (optional)

---

### What It Does

For each chapter:

* Sorts images naturally (1,2,3...10 correctly)
* Converts `.avif` → `.webp`
* Uploads new images only
* Reuses existing URLs if found
* Creates chapter CBZ
* Updates `upload_record.json`
* Builds final Cubari JSON

---

### Final Output

```
Title_Name_cubari.json
upload_record.json
CBZ_Files/*.cbz
```

---

# 🔄 2️⃣ Rebuild upload_record.json

If:

* You lost `upload_record.json`
* You already have Cubari JSON
* You want to sync local files with Cubari URLs

Use:

**File:** `update.py` 

### Run:

```bash
python update.py
```

### You Will Be Asked:

* Path to cubari.json
* Base folder path

### What It Does:

* Reads Cubari JSON
* Matches folders to chapter titles
* Maps image index → Cubari URL
* Generates fresh `upload_record.json`

---

# 📚 3️⃣ Merge Multiple CBZ Into One

**File:** `rename.py` 

Edit inside:

```python
input_cbz = [
    "Chapter 1.cbz",
    "Chapter 2.cbz",
]
```

Run:

```bash
python rename.py
```

Creates:

```
Anthology.cbz
```

Pages will be renumbered:

```
0001.jpg
0002.jpg
0003.jpg
...
```

---

# 🧠 Resume Logic

The system prevents reuploads by:

* Tracking every uploaded image in:

  ```
  upload_record.json
  ```
* Reusing existing Cubari URLs
* Matching by:

  * Chapter title
  * Chapter index
  * Relative image path

You can stop anytime and rerun safely.

---

# 📌 Supported Formats

```
.jpg
.jpeg
.png
.webp
.avif (auto-converted)
```

---

# ⚠ Notes

* Catbox has rate limits — tool retries automatically.
* AVIF conversion requires Pillow compiled with AVIF support.
* Chapter folder names must match Cubari titles.
* Natural sorting ensures:

  ```
  1.jpg, 2.jpg, 10.jpg
  ```

  not

  ```
  1.jpg, 10.jpg, 2.jpg
  ```

---

# 💡 Example Cubari Link Format

After uploading your JSON to GitHub:

```
https://cubari.moe/read/gist/YOUR_GIST_ID/
```

or

```
https://cubari.moe/read/github/USERNAME/REPO/main/your_json.json/
```

---

# 🏁 Complete Workflow

1. Prepare chapter folders
2. Run `script.py`
3. Upload generated JSON to GitHub
4. Open Cubari link
5. Done ✅

---
