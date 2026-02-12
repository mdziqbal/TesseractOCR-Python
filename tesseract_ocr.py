"""
TesseractOCR - Pure Python wrapper for Tesseract OCR using ctypes.

No .exe dependency - loads DLLs directly.
Requires: Pillow, NumPy

Usage:
    from tesseract_ocr import TesseractOCR

    ocr = TesseractOCR()
    text = ocr.image_to_text('image.png')
    print(text)
    ocr.close()

Or using context manager:
    with TesseractOCR() as ocr:
        text = ocr.image_to_text('image.png')
        print(text)
"""

import ctypes
import os
from PIL import Image
import numpy as np


class TesseractOCR:
    """
    Pure Python Tesseract OCR wrapper using ctypes.
    No subprocess calls - loads DLL directly.
    """

    # Page Segmentation Modes
    PSM_AUTO = 3            # Fully automatic page segmentation
    PSM_SINGLE_COLUMN = 4   # Assume a single column of text
    PSM_SINGLE_BLOCK = 6    # Assume a single uniform block of text
    PSM_SINGLE_LINE = 7     # Treat the image as a single text line
    PSM_SINGLE_WORD = 8     # Treat the image as a single word
    PSM_SINGLE_CHAR = 10    # Treat the image as a single character
    PSM_RAW_LINE = 13       # Raw line, no OSD or OCR

    def __init__(self, dll_dir=None, tessdata_dir=None, lang='eng'):
        """
        Initialize Tesseract OCR.

        Args:
            dll_dir: Path to folder containing tesseract DLLs.
                     Defaults to 'dlls' subfolder next to this file.
            tessdata_dir: Path to tessdata folder.
                          Defaults to 'tessdata' subfolder next to this file.
            lang: Language code (default: 'eng')
        """
        # Resolve paths relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.dll_dir = dll_dir or os.path.join(base_dir, 'dlls')
        self.tessdata_dir = tessdata_dir or os.path.join(base_dir, 'tessdata')
        self.lang = lang
        self.api = None
        self.tess_lib = None

        self._load_library()
        self._setup_api_functions()
        self._init_api()

    # Bundled DLLs (included in this package)
    # tesseract55.dll depends on leptonica, which Windows loads automatically
    TESSERACT_DLL = 'tesseract55.dll'
    LEPTONICA_DLL = 'leptonica-1.85.0.dll'

    def _load_library(self):
        """Load the Tesseract DLL."""
        # Add DLL directory to search path (so Windows can find leptonica)
        os.environ['PATH'] = self.dll_dir + ';' + os.environ['PATH']
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(self.dll_dir)

        # Verify both DLLs exist
        tesseract_path = os.path.join(self.dll_dir, self.TESSERACT_DLL)
        leptonica_path = os.path.join(self.dll_dir, self.LEPTONICA_DLL)

        missing = []
        if not os.path.exists(tesseract_path):
            missing.append(self.TESSERACT_DLL)
        if not os.path.exists(leptonica_path):
            missing.append(self.LEPTONICA_DLL)

        if missing:
            raise FileNotFoundError(
                f"Missing DLL(s) in {self.dll_dir}:\n"
                f"  {', '.join(missing)}\n"
                f"Required: {self.TESSERACT_DLL}, {self.LEPTONICA_DLL}"
            )

        # Load Tesseract DLL (Windows automatically loads leptonica as dependency)
        try:
            self.tess_lib = ctypes.cdll.LoadLibrary(tesseract_path)
        except OSError as e:
            raise RuntimeError(f"Failed to load {self.TESSERACT_DLL}: {e}")

    def _setup_api_functions(self):
        """Define C API function signatures."""
        lib = self.tess_lib

        # TessBaseAPICreate() -> TessBaseAPI*
        lib.TessBaseAPICreate.restype = ctypes.c_void_p
        lib.TessBaseAPICreate.argtypes = []

        # TessBaseAPIInit3(api, datapath, language) -> int
        lib.TessBaseAPIInit3.restype = ctypes.c_int
        lib.TessBaseAPIInit3.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
        ]

        # TessBaseAPISetImage(api, imagedata, width, height, bpp, bpl)
        lib.TessBaseAPISetImage.restype = None
        lib.TessBaseAPISetImage.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]

        # TessBaseAPISetSourceResolution(api, ppi)
        lib.TessBaseAPISetSourceResolution.restype = None
        lib.TessBaseAPISetSourceResolution.argtypes = [ctypes.c_void_p, ctypes.c_int]

        # TessBaseAPIGetUTF8Text(api) -> char*
        lib.TessBaseAPIGetUTF8Text.restype = ctypes.c_void_p
        lib.TessBaseAPIGetUTF8Text.argtypes = [ctypes.c_void_p]

        # TessBaseAPISetVariable(api, name, value) -> bool
        lib.TessBaseAPISetVariable.restype = ctypes.c_bool
        lib.TessBaseAPISetVariable.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
        ]

        # TessBaseAPIMeanTextConf(api) -> int
        lib.TessBaseAPIMeanTextConf.restype = ctypes.c_int
        lib.TessBaseAPIMeanTextConf.argtypes = [ctypes.c_void_p]

        # TessBaseAPISetPageSegMode(api, mode)
        lib.TessBaseAPISetPageSegMode.restype = None
        lib.TessBaseAPISetPageSegMode.argtypes = [ctypes.c_void_p, ctypes.c_int]

        # Cleanup functions
        lib.TessBaseAPIEnd.restype = None
        lib.TessBaseAPIEnd.argtypes = [ctypes.c_void_p]

        lib.TessBaseAPIDelete.restype = None
        lib.TessBaseAPIDelete.argtypes = [ctypes.c_void_p]

        lib.TessDeleteText.restype = None
        lib.TessDeleteText.argtypes = [ctypes.c_void_p]

        # TessVersion() -> const char*
        lib.TessVersion.restype = ctypes.c_char_p
        lib.TessVersion.argtypes = []

    def version(self):
        """
        Get Tesseract version.

        Returns:
            Version string (e.g., '5.5.0')
        """
        return self.tess_lib.TessVersion().decode('utf-8')

    def _init_api(self):
        """Initialize the Tesseract API."""
        self.api = self.tess_lib.TessBaseAPICreate()
        if not self.api:
            raise RuntimeError("TessBaseAPICreate returned NULL")

        ret = self.tess_lib.TessBaseAPIInit3(
            self.api,
            self.tessdata_dir.encode('utf-8'),
            self.lang.encode('utf-8')
        )
        if ret != 0:
            raise RuntimeError(
                f"Failed to initialize Tesseract (code {ret}). "
                f"Check tessdata path: {self.tessdata_dir}"
            )

    def set_variable(self, name, value):
        """
        Set a Tesseract configuration variable.

        Example:
            ocr.set_variable('tessedit_char_whitelist', '0123456789')
        """
        return self.tess_lib.TessBaseAPISetVariable(
            self.api,
            name.encode('utf-8'),
            value.encode('utf-8')
        )

    def set_psm(self, mode):
        """
        Set page segmentation mode.

        Args:
            mode: One of PSM_* constants or integer value
        """
        self.tess_lib.TessBaseAPISetPageSegMode(self.api, mode)

    def image_to_text(self, image, psm=None):
        """
        Extract text from an image file or PIL Image.

        Args:
            image: Path to image file (str) or PIL Image object
            psm: Optional page segmentation mode

        Returns:
            Extracted text as string
        """
        # Handle both file path and PIL Image
        if isinstance(image, Image.Image):
            img = image
        else:
            img = Image.open(image)
        return self.pil_to_text(img, psm=psm)

    def pil_to_text(self, pil_image, psm=None):
        """
        Extract text from a PIL Image object.

        Args:
            pil_image: PIL Image object
            psm: Optional page segmentation mode

        Returns:
            Extracted text as string
        """
        # Convert to RGB if needed
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        elif pil_image.mode not in ('RGB', 'L'):
            pil_image = pil_image.convert('RGB')

        # Convert to numpy array
        img_array = np.array(pil_image)
        height, width = img_array.shape[:2]

        if len(img_array.shape) == 2:
            bpp = 1  # grayscale
        else:
            bpp = img_array.shape[2]  # 3 for RGB

        bpl = width * bpp  # bytes per line

        # Ensure contiguous memory
        img_data = np.ascontiguousarray(img_array)

        if psm is not None:
            self.set_psm(psm)

        # Set the image
        self.tess_lib.TessBaseAPISetImage(
            self.api,
            img_data.ctypes.data,
            width, height, bpp, bpl
        )
        self.tess_lib.TessBaseAPISetSourceResolution(self.api, 300)

        # Get text
        text_ptr = self.tess_lib.TessBaseAPIGetUTF8Text(self.api)
        if not text_ptr:
            return ""

        text = ctypes.string_at(text_ptr).decode('utf-8')
        self.tess_lib.TessDeleteText(text_ptr)

        return text.strip()

    def image_to_text_with_confidence(self, image, psm=None):
        """
        Extract text with confidence score.

        Args:
            image: Path to image file (str) or PIL Image object
            psm: Optional page segmentation mode

        Returns:
            Tuple of (text, confidence_percentage)
        """
        text = self.image_to_text(image, psm=psm)
        confidence = self.tess_lib.TessBaseAPIMeanTextConf(self.api)
        return text, confidence

    def pil_to_text_with_confidence(self, pil_image, psm=None):
        """
        Extract text from PIL Image with confidence score.

        Args:
            pil_image: PIL Image object
            psm: Optional page segmentation mode

        Returns:
            Tuple of (text, confidence_percentage)
        """
        text = self.pil_to_text(pil_image, psm=psm)
        confidence = self.tess_lib.TessBaseAPIMeanTextConf(self.api)
        return text, confidence

    def close(self):
        """Release resources."""
        if self.api:
            self.tess_lib.TessBaseAPIEnd(self.api)
            self.tess_lib.TessBaseAPIDelete(self.api)
            self.api = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()
