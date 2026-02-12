"""
Example usage of TesseractWrapper.
"""

from tesseract_ocr import TesseractOCR
from PIL import Image, ImageDraw, ImageFont


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
    print("TesseractWrapper Example")
    print("=" * 50)

    # Create sample image
    print("\n1. Creating sample image...")
    image_path = create_sample_image()
    print(f"   Created: {image_path}")

    # Basic usage with context manager
    print("\n2. Basic OCR...")
    with TesseractOCR() as ocr:
        text = ocr.image_to_text(image_path)
        print(f"   Result: '{text}'")

    # With confidence score
    print("\n3. OCR with confidence...")
    with TesseractOCR() as ocr:
        text, confidence = ocr.image_to_text_with_confidence(image_path)
        print(f"   Result: '{text}'")
        print(f"   Confidence: {confidence}%")

    # Single line mode
    print("\n4. Single line mode (PSM 7)...")
    with TesseractOCR() as ocr:
        text = ocr.image_to_text(image_path, psm=TesseractOCR.PSM_SINGLE_LINE)
        print(f"   Result: '{text}'")

    # From PIL image directly
    print("\n5. From PIL Image...")
    with TesseractOCR() as ocr:
        img = Image.open(image_path)
        text = ocr.pil_to_text(img)
        print(f"   Result: '{text}'")

    # Digits only mode
    print("\n6. Digits only mode...")
    with TesseractOCR() as ocr:
        ocr.set_variable('tessedit_char_whitelist', '0123456789')
        text = ocr.image_to_text(image_path)
        print(f"   Result: '{text}'")

    # Cleanup
    import os
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
