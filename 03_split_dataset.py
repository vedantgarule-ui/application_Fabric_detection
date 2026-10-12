"""
03_split_dataset.py

Splits fabric_dataset/<class>/ images into train/val/test folders,
using only rows marked verified=YES in dataset_log.csv (falls back to
using all images in a class folder if the class has no verified column
data yet -- e.g. if you added images manually instead of via the scraper).

Output structure:
    fabric_dataset_split/
    ├── train/cotton/, train/linen/, ...
    ├── val/cotton/, val/linen/, ...
    └── test/cotton/, test/linen/, ...

Usage:
    pip install scikit-learn --break-system-packages
    python 03_split_dataset.py
"""

import os
import csv
import shutil
import random
from sklearn.model_selection import train_test_split

SOURCE_DIR = "fabric_dataset"
OUTPUT_DIR = "fabric_dataset_split"
CSV_PATH = os.path.join(SOURCE_DIR, "dataset_log.csv")

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

FABRIC_CLASSES = ["cotton", "linen", "wool", "silk", "polyester", "nylon"]

random.seed(42)


def load_verified_filenames():
    """Returns dict: {fabric_lowercase: set of verified image filenames}."""
    verified = {c: set() for c in FABRIC_CLASSES}
    if not os.path.exists(CSV_PATH):
        return verified

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("verified", "").strip().upper() == "YES":
                fabric = row["fabric"].strip().lower()
                if fabric in verified:
                    verified[fabric].add(row["image_name"])
    return verified


def get_images_for_class(fabric, verified_names):
    class_dir = os.path.join(SOURCE_DIR, fabric)
    if not os.path.isdir(class_dir):
        return []
    all_images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if verified_names:
        # Only use verified images
        return [f for f in all_images if f in verified_names]
    else:
        # No verified data logged for this class -- use everything,
        # but warn so you know to go back and audit it
        print(f"  WARNING: no verified=YES entries found for '{fabric}', "
              f"using all {len(all_images)} images unaudited.")
        return all_images


def split_and_copy(fabric, images):
    if len(images) < 3:
        print(f"  Skipping '{fabric}': only {len(images)} image(s), need at least 3 to split.")
        return

    train_imgs, temp_imgs = train_test_split(
        images, train_size=TRAIN_RATIO, random_state=42, shuffle=True
    )
    val_size_relative = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
    val_imgs, test_imgs = train_test_split(
        temp_imgs, train_size=val_size_relative, random_state=42, shuffle=True
    )

    for split_name, split_imgs in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
        dest_dir = os.path.join(OUTPUT_DIR, split_name, fabric)
        os.makedirs(dest_dir, exist_ok=True)
        for img in split_imgs:
            src = os.path.join(SOURCE_DIR, fabric, img)
            dst = os.path.join(dest_dir, img)
            shutil.copy(src, dst)

    print(f"  {fabric}: {len(train_imgs)} train / {len(val_imgs)} val / {len(test_imgs)} test")


def main():
    verified = load_verified_filenames()

    print("Splitting dataset...")
    for fabric in FABRIC_CLASSES:
        verified_names = verified.get(fabric, set())
        images = get_images_for_class(fabric, verified_names)
        if not images:
            print(f"  {fabric}: no images found, skipping.")
            continue
        split_and_copy(fabric, images)

    print(f"\nDone. Split dataset written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
