"""
TesseractWrapper - Pure Python OCR without .exe dependency.

Usage:
    from TesseractWrapper import TesseractOCR

    with TesseractOCR() as ocr:
        text = ocr.image_to_text('image.png')
        print(text)
"""

from .tesseract_ocr import TesseractOCR

__version__ = '1.0.0'
__all__ = ['TesseractOCR']
