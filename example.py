"""
Example usage of TesseractOCR wrapper.
"""

from tesseract_ocr import TesseractOCR
from PIL import Image, ImageDraw, ImageFont
import os


def create_sample_image():
    """Create a sample image for testing."""
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()

    draw.text((20, 30), "Hello World 12345", fill='black', font=font)
    img.save('sample.png')
    return 'sample.png'


def main():
    print("=" * 50)
    print("TesseractOCR Wrapper - Examples")
    print("=" * 50)

    # Create sample image
    print("\n1. Creating sample image...")
    image_path = create_sample_image()
    print(f"   Created: {image_path}")

    # Check Tesseract version
    print("\n2. Checking Tesseract version...")
    with TesseractOCR() as ocr:
        print(f"   Version: {ocr.version()}")

    # Basic OCR with file path
    print("\n3. Basic OCR (file path)...")
    with TesseractOCR() as ocr:
        text = ocr.image_to_text(image_path)
        print(f"   Result: '{text}'")

    # OCR with PIL Image object (both work now!)
    print("\n4. OCR with PIL Image object...")
    with TesseractOCR() as ocr:
        img = Image.open(image_path)
        text = ocr.image_to_text(img)  # Can pass PIL Image directly!
        print(f"   Result: '{text}'")

    # With confidence score
    print("\n5. OCR with confidence score...")
    with TesseractOCR() as ocr:
        text, confidence = ocr.image_to_text_with_confidence(image_path)
        print(f"   Result: '{text}'")
        print(f"   Confidence: {confidence}%")

    # Single line mode (PSM 7)
    print("\n6. Single line mode (PSM 7)...")
    with TesseractOCR() as ocr:
        text = ocr.image_to_text(image_path, psm=TesseractOCR.PSM_SINGLE_LINE)
        print(f"   Result: '{text}'")

    # Cropped region from PIL Image
    print("\n7. Cropped region from PIL Image...")
    with TesseractOCR() as ocr:
        img = Image.open(image_path)
        cropped = img.crop((20, 20, 250, 80))  # Crop a region
        text = ocr.image_to_text(cropped)
        print(f"   Result: '{text}'")

    # Digits only mode
    print("\n8. Digits only mode (whitelist)...")
    with TesseractOCR() as ocr:
        ocr.set_variable('tessedit_char_whitelist', '0123456789')
        text = ocr.image_to_text(image_path)
        print(f"   Result: '{text}'")

    # Cleanup
    os.remove(image_path)

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("=" * 50)


if __name__ == '__main__':
    # main()
    with TesseractOCR() as ocr:
        text, confidence = ocr.image_to_text_with_confidence("./digits_num.png",psm=7)
        print(f"   Result: '{text}'")
        print(f"   Confidence: {confidence}%")
