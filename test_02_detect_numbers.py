import pytesseract
from PIL import Image

# Configure to only detect digits (0-9)
custom_config = r'--oem 3 --psm 6 outputbase digits'
img = Image.open('image.png')
digits = pytesseract.image_to_string(img, config=custom_config)
print(digits)