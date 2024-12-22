import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from enum import Enum

class ResultMetadataType(Enum):
    """
    Represents some type of metadata about the result of the decoding that the decoder
    wishes to communicate back to the caller.
    """
    
    OTHER = "OTHER"
    ORIENTATION = "ORIENTATION"
    BYTE_SEGMENTS = "BYTE_SEGMENTS"
    ERROR_CORRECTION_LEVEL = "ERROR_CORRECTION_LEVEL"
    ERRORS_CORRECTED = "ERRORS_CORRECTED"
    ERASURES_CORRECTED = "ERASURES_CORRECTED"
    ISSUE_NUMBER = "ISSUE_NUMBER"
    SUGGESTED_PRICE = "SUGGESTED_PRICE"
    POSSIBLE_COUNTRY = "POSSIBLE_COUNTRY"
    UPC_EAN_EXTENSION = "UPC_EAN_EXTENSION"
    PDF417_EXTRA_METADATA = "PDF417_EXTRA_METADATA"
    STRUCTURED_APPEND_SEQUENCE = "STRUCTURED_APPEND_SEQUENCE"
    STRUCTURED_APPEND_PARITY = "STRUCTURED_APPEND_PARITY"
    SYMBOLOGY_IDENTIFIER = "SYMBOLOGY_IDENTIFIER"
    
    def __str__(self):
        return self.value
