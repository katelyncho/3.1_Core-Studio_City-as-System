import os
import json
import random
import shutil
import kagglehub

SAMPLES_PER_BREED = 3
TARGET_DIR = "dogs"
MANIFEST_FILE = "dogs_manifest.json"

def log(*a): print("[dogs]", *a)

def nice_breed_name(folder_name: str) -> str:
    # Stanford Dogs breed folder looks like: n02085620-Chihuahua
    if "-" in folder_name:
        return folder_name.split("-", 1)[1].replace("_", " ")
    return folder_name.replace("_", " ")

# 1) Download dataset via kagglehub
path = kagglehub.dataset_download("jessicali9530/stanford-dogs-dataset")
log("Dataset path:", path)
log("Top-level contents:", os.listdir(path))

# 2) Locate the top-level "images" (case-insensitive)
images_root = None
for name in os.listdir(path):
    p = os.path.join(path, name)
    if os.path.isdir(p) and name.lower() == "images":
        images_root = p
        break

if not images_root:
    log("ERROR: Couldn't find an 'images' folder at the dataset root.")
    raise SystemExit(1)

log("Images root:", images_root)
log("Immediate contents of images root:", os.listdir(images_root)[:10])

# 3) Walk the tree to find ALL breed directories (dirs that contain image files)
breed_dirs = []
for curr_dir, subdirs, files in os.walk(images_root):
    # If THIS directory has image files, then its parent is the breed folder OR this is the breed folder.
    # In Stanford Dogs, the breed folder itself contains the images.
    has_imgs_here = any(
        f.lower().endswith((".jpg", ".jpeg", ".png"))
        for f in files
    )
    if has_imgs_here:
        breed_dirs.append(curr_dir)

log("Total candidate breed directories found:", len(breed_dirs))
if breed_dirs:
    log("Example breed dir:", breed_dirs[0])
    ex_files = [f for f in os.listdir(breed_dirs[0]) if f.lower().endswith((".jpg",".jpeg",".png"))][:5]
    log("Example image files in that dir:", ex_files)

# 4) Prepare output
os.makedirs(TARGET_DIR, exist_ok=True)
manifest = {}
copied_count = 0

for breed_path in breed_dirs:
    folder_name = os.path.basename(breed_path)
    breed_name = nice_breed_name(folder_name)

    imgs = [f for f in os.listdir(breed_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
            and os.path.isfile(os.path.join(breed_path, f))]
    if not imgs:
        continue

    sample_imgs = random.sample(imgs, min(SAMPLES_PER_BREED, len(imgs)))
    manifest.setdefault(breed_name, [])
    for img in sample_imgs:
        src = os.path.join(breed_path, img)
        dst_name = f"{breed_name.replace(' ', '_')}__{img}"
        dst = os.path.join(TARGET_DIR, dst_name)
        shutil.copy(src, dst)
        manifest[breed_name].append(f"./{TARGET_DIR}/{dst_name}")
        copied_count += 1

# 5) Write manifest
with open(MANIFEST_FILE, "w") as f:
    json.dump(manifest, f, indent=2)

log(f"Done. Copied {copied_count} images into ./{TARGET_DIR}")
log(f"Manifest written to ./{MANIFEST_FILE} with {len(manifest)} breeds.")
