import re
import cv2
from pathlib import Path
import pytesseract

BASE_DIR = Path(__file__).resolve().parent

pytesseract.pytesseract.tesseract_cmd = str(
    BASE_DIR / "vendor" / "tesseract" / "tesseract.exe"
)


class OCRService:
    def detect(self, image_path: str) -> str | None:
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        if height > width:
            img = cv2.resize(img, (904, 1280))
            h, w = img.shape[:2]
            crop_h = round(h * 0.04)
            crop_w = round(w * 0.70)
        else:
            img = cv2.resize(img, (1280, 904))
            h, w = img.shape[:2]
            crop_h = round(h * 0.05)
            crop_w = round(w * 0.80)

        cropped = img[0:crop_h, crop_w:w - 1]
        text = pytesseract.image_to_string(cropped)

        numbers = "".join(re.findall(r"\d+", text))
        return numbers if numbers else None