import re
import cv2
from glob import glob
from pathlib import Path

list_file = sorted(glob("data-contoh/folder-input/*JPG") + glob("data-contoh/folder-input/*jpg"))

for f in list_file:
    src = Path(f)
    target_dir = Path('data-contoh/folder-output')

    new_path = target_dir / f"{src.stem}_compress{src.suffix}"

    img = cv2.imread(f)
    height, width = img.shape[:2]

    if height > width: # Potrait
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.resize(img, (800, 1280))
        h, w = img.shape[:2]
        crop_h = round(h * 0.05)
        crop_w = round(w * 0.70)
    else: # Landscape
        img = cv2.resize(img, (1280, 800))
        h, w = img.shape[:2]
        crop_h = round(h * 0.5)
        crop_w = round(w * 0.80)

    cropped = img[0:crop_h, crop_w:w - 1]

    cv2.imwrite(new_path, cropped)