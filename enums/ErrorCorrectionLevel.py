import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from enum import Enum

class ErrorCorrectionLevel(Enum):
    L = 0x01  # ~7% correction
    M = 0x00  # ~15% correction
    Q = 0x03  # ~25% correction
    H = 0x02  # ~30% correction

    def __init__(self, bits):
        # Khởi tạo phương thức __init__ để gán giá trị bits
        self.bits = bits
        
    def get_bits(self):
        # Trả về giá trị bits
        return self.bits

    @staticmethod
    def for_bits(bits):
        # Tìm kiếm ErrorCorrectionLevel theo bits
        for level in ErrorCorrectionLevel:
            if level.bits == bits:
                return level
        raise ValueError("Invalid bits value")