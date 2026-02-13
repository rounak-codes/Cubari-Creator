import zipfile, os, shutil

# ==== CONFIG ====
input_cbz = [
    "Chapter 1.cbz",
    "Chapter 2.cbz",
    "Chapter 3.cbz",
]  # order here = final page order
output_cbz = "Anthology.cbz"
temp_dir = "temp_extract"
# =================

# Clean temp folder
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

page_counter = 1

for cbz in input_cbz:
    with zipfile.ZipFile(cbz, 'r') as z:
        file_list = sorted(
            [f for f in z.namelist() if f.lower().endswith(('.jpg','.png','.jpeg'))]
        )
        for f in file_list:
            ext = f.split('.')[-1]
            new_name = f"{page_counter:04d}.{ext}"
            with z.open(f) as src, open(os.path.join(temp_dir, new_name), 'wb') as dst:
                dst.write(src.read())
            page_counter += 1

# Create final CBZ
with zipfile.ZipFile(output_cbz, 'w') as out:
    for f in sorted(os.listdir(temp_dir)):
        out.write(os.path.join(temp_dir, f), arcname=f)

shutil.rmtree(temp_dir)

print("Done! Created:", output_cbz)
