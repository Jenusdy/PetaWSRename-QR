import cv2
import pyzbar.pyzbar as pyzbar


class QRService:
    def detect(self, image_path: str) -> str | None:
        image = cv2.imread(image_path)
        codes = pyzbar.decode(image)

        if not codes:
            return None

        return codes[0].data.decode()