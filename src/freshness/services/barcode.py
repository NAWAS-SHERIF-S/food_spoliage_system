"""Barcode decoding service for packaged produce items."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

# Sample lookup table for food product barcodes (UPC/EAN)
BARCODE_DATABASE: dict[str, dict[str, str | int]] = {
    "012345678905": {"type": "apple", "name": "Fresh Organic Apples (Bag)", "days": 14},
    "098765432104": {"type": "banana", "name": "Cavendish Bananas (Bunch)", "days": 5},
    "041331021481": {"type": "carrot", "name": "Whole Carrots 1lb", "days": 21},
    "033383600020": {"type": "tomato", "name": "Vine Ripened Tomatoes 4pk", "days": 7},
    "021130070548": {"type": "strawberry", "name": "Fresh Strawberries 16oz", "days": 4},
}


def decode_barcode_image(image: Image.Image) -> dict[str, str | int] | None:
    """Detect and decode QR code / barcode from a PIL image."""
    try:
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(cv_img)
        if data and data in BARCODE_DATABASE:
            return BARCODE_DATABASE[data]
    except Exception:
        pass
    return None
