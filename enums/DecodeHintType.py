from enum import Enum
from typing import List

class DecodeHintType(Enum):
    OTHER = object
    PURE_BARCODE = None
    POSSIBLE_FORMATS = List
    TRY_HARDER = None
    CHARACTER_SET = str
    ALLOWED_LENGTHS = list
    ASSUME_CODE_39_CHECK_DIGIT = None
    ASSUME_GS1 = None
    RETURN_CODABAR_START_END = None
    NEED_RESULT_POINT_CALLBACK = 'ResultPointCallback'  # You can define this class if needed
    ALLOWED_EAN_EXTENSIONS = list
    ALSO_INVERTED = None

    def __init__(self, value_type):
        self.value_type = value_type

    @property
    def get_value_type(self):
        return self.value_type
