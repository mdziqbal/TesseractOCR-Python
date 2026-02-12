# TesseractOCR-Python

A lightweight, pure Python wrapper for Tesseract OCR that **eliminates the need for `tesseract.exe`**.

## Why This Exists

Traditional Python OCR solutions like `pytesseract` require:
- Installing Tesseract executable separately
- Adding `tesseract.exe` to system PATH
- Subprocess calls for every OCR operation

**This wrapper solves these problems by:**
- Loading Tesseract DLLs directly via `ctypes`
- No subprocess overhead
- Self-contained package (just copy and use)
- Same accuracy as the official Tesseract

## Features

- **No .exe dependency** - Uses DLL directly
- **Self-contained** - All required files included
- **Lightweight** - Only ~11 MB total
- **Simple API** - Drop-in replacement for pytesseract
- **Context manager support** - Automatic resource cleanup

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install Pillow numpy
   ```
3. Import and use

## Usage

### Basic OCR

```python
from tesseract_ocr import TesseractOCR

with TesseractOCR() as ocr:
    text = ocr.image_to_text('image.png')
    print(text)
```

### With Confidence Score

```python
with TesseractOCR() as ocr:
    text, confidence = ocr.image_to_text_with_confidence('image.png')
    print(f"Text: {text}")
    print(f"Confidence: {confidence}%")
```

### From PIL Image

```python
from PIL import Image

with TesseractOCR() as ocr:
    img = Image.open('scan.png')
    img = img.crop((100, 200, 500, 300))  # Crop region
    text = ocr.pil_to_text(img)
    print(text)
```

### Page Segmentation Modes

```python
with TesseractOCR() as ocr:
    # Single line mode (for form fields)
    text = ocr.image_to_text('field.png', psm=TesseractOCR.PSM_SINGLE_LINE)

    # Single word mode
    text = ocr.image_to_text('word.png', psm=TesseractOCR.PSM_SINGLE_WORD)
```

Available PSM modes:
| Mode | Constant | Description |
|------|----------|-------------|
| 3 | `PSM_AUTO` | Fully automatic (default) |
| 4 | `PSM_SINGLE_COLUMN` | Single column of text |
| 6 | `PSM_SINGLE_BLOCK` | Single uniform block |
| 7 | `PSM_SINGLE_LINE` | Single text line |
| 8 | `PSM_SINGLE_WORD` | Single word |
| 10 | `PSM_SINGLE_CHAR` | Single character |
| 13 | `PSM_RAW_LINE` | Raw line |

### Digits Only Mode

```python
with TesseractOCR() as ocr:
    ocr.set_variable('tessedit_char_whitelist', '0123456789')
    text = ocr.image_to_text('numbers.png')
    print(text)  # Only digits
```

## Package Structure

```
TesseractOCR-Python/
├── tesseract_ocr.py        # Main wrapper module
├── __init__.py             # Package init
├── example.py              # Usage examples
├── dlls/
│   ├── tesseract55.dll     # Tesseract 5.5 library
│   └── leptonica-1.85.0.dll # Image processing library
└── tessdata/
    └── eng.traineddata     # English language model
```

## Supported Image Formats

Any format supported by Pillow:
- PNG, JPG/JPEG, BMP, TIFF, GIF, WebP, and more

## Adding More Languages

1. Download `.traineddata` files from [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast)
2. Place them in the `tessdata/` folder
3. Initialize with the language code:

```python
ocr = TesseractOCR(lang='fra')  # French
ocr = TesseractOCR(lang='deu')  # German
ocr = TesseractOCR(lang='eng+fra')  # Multiple languages
```

## Requirements

- Python 3.8+
- Windows (64-bit)
- Pillow
- NumPy

## DLL Source

The included DLLs are from the [TesseractOCR NuGet package](https://www.nuget.org/packages/TesseractOCR) by Sicos1977, which is based on official Tesseract 5.5.0.

## Comparison with pytesseract

| Feature | This Wrapper | pytesseract |
|---------|--------------|-------------|
| Requires .exe | No | Yes |
| Subprocess calls | No | Yes |
| Self-contained | Yes | No |
| Package size | ~11 MB | Needs separate install |
| OCR Accuracy | Same | Same |
| Performance | Faster (no subprocess) | Slower |

## License

This project is licensed under the Apache License 2.0.

Tesseract OCR is licensed under the Apache License 2.0.
