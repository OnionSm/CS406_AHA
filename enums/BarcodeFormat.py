import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from enum import Enum

class BarcodeFormat(Enum):
    """Enumerates barcode formats known to this package."""
    
    AZTEC = "AZTEC"  # Aztec 2D barcode format
    CODABAR = "CODABAR"  # CODABAR 1D format
    CODE_39 = "CODE_39"  # Code 39 1D format
    CODE_93 = "CODE_93"  # Code 93 1D format
    CODE_128 = "CODE_128"  # Code 128 1D format
    DATA_MATRIX = "DATA_MATRIX"  # Data Matrix 2D barcode format
    EAN_8 = "EAN_8"  # EAN-8 1D format
    EAN_13 = "EAN_13"  # EAN-13 1D format
    ITF = "ITF"  # ITF (Interleaved Two of Five) 1D format
    MAXICODE = "MAXICODE"  # MaxiCode 2D barcode format
    PDF_417 = "PDF_417"  # PDF417 format
    QR_CODE = "QR_CODE"  # QR Code 2D barcode format
    RSS_14 = "RSS_14"  # RSS 14
    RSS_EXPANDED = "RSS_EXPANDED"  # RSS Expanded
    UPC_A = "UPC_A"  # UPC-A 1D format
    UPC_E = "UPC_E"  # UPC-E 1D format
    UPC_EAN_EXTENSION = "UPC_EAN_EXTENSION"  # UPC/EAN extension format

    def __str__(self):
        return self.value
