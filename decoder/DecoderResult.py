import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from typing import List

class DecoderResult:
    """
    Lớp này chứa kết quả giải mã từ một ma trận bit, thường áp dụng cho các định dạng mã vạch 2D.
    Kết quả này bao gồm các byte thô, chuỗi biểu diễn các byte này (nếu có), và các thông tin liên quan khác.
    """

    def __init__(self, raw_bytes: bytes, text: str, byte_segments: List[bytes], ec_level: str, 
                 sa_sequence: int = -1, sa_parity: int = -1, symbology_modifier: int = 0):
        """
        Hàm khởi tạo để tạo một đối tượng DecoderResult.
        
        Input:
            - raw_bytes: Mảng byte chứa dữ liệu thô từ quá trình giải mã (kiểu dữ liệu: bytes)
            - text: Chuỗi đại diện cho kết quả giải mã (kiểu dữ liệu: str)
            - byte_segments: Danh sách các mảng byte chứa các phân đoạn byte (kiểu dữ liệu: List[bytes])
            - ec_level: Mức độ sửa lỗi của mã (kiểu dữ liệu: str)
            - sa_sequence: Số hiệu chuỗi của phần append có cấu trúc (mặc định là -1, kiểu dữ liệu: int)
            - sa_parity: Parity của phần append có cấu trúc (mặc định là -1, kiểu dữ liệu: int)
            - symbology_modifier: Bộ sửa đổi mã vạch (mặc định là 0, kiểu dữ liệu: int)
        
        Output:
            - Tạo đối tượng DecoderResult với các thuộc tính tương ứng.
        """
        self.raw_bytes = raw_bytes
        self.num_bits = 0 if raw_bytes is None else 8 * len(raw_bytes)
        self.text = text
        self.byte_segments = byte_segments
        self.ec_level = ec_level
        self.structured_append_parity = sa_parity
        self.structured_append_sequence_number = sa_sequence
        self.symbology_modifier = symbology_modifier

        self.errors_corrected = None
        self.erasures = None
        self.other = None

    def get_raw_bytes(self) -> bytes:
        """
        Trả về mảng byte thô đại diện cho kết quả giải mã.

        Input:
            - Không có đầu vào.
        
        Output:
            - Mảng byte thô (kiểu dữ liệu: bytes), hoặc None nếu không có.
        """
        return self.raw_bytes

    def get_num_bits(self) -> int:
        """
        Trả về số bit hợp lệ trong mảng byte thô.

        Input:
            - Không có đầu vào.
        
        Output:
            - Số bit hợp lệ, thường là 8 lần độ dài của mảng byte thô (kiểu dữ liệu: int).
        """
        return self.num_bits

    def set_num_bits(self, num_bits: int):
        """
        Cập nhật số bit hợp lệ trong mảng byte thô.

        Input:
            - num_bits: Số bit hợp lệ trong mảng byte thô (kiểu dữ liệu: int)
        
        Output:
            - Cập nhật thuộc tính num_bits của đối tượng.
        """
        self.num_bits = num_bits

    def get_text(self) -> str:
        """
        Trả về chuỗi biểu diễn kết quả giải mã.

        Input:
            - Không có đầu vào.
        
        Output:
            - Chuỗi kết quả giải mã (kiểu dữ liệu: str).
        """
        return self.text

    def get_byte_segments(self) -> List[bytes]:
        """
        Trả về danh sách các phân đoạn byte trong kết quả giải mã.

        Input:
            - Không có đầu vào.
        
        Output:
            - Danh sách các phân đoạn byte (kiểu dữ liệu: List[bytes]), hoặc None nếu không có.
        """
        return self.byte_segments

    def get_ec_level(self) -> str:
        """
        Trả về mức độ sửa lỗi được sử dụng.

        Input:
            - Không có đầu vào.
        
        Output:
            - Mức độ sửa lỗi (kiểu dữ liệu: str), hoặc None nếu không có.
        """
        return self.ec_level

    def get_errors_corrected(self) -> int:
        """
        Trả về số lỗi đã được sửa chữa trong quá trình giải mã.

        Input:
            - Không có đầu vào.
        
        Output:
            - Số lượng lỗi đã được sửa chữa (kiểu dữ liệu: int), hoặc None nếu không có.
        """
        return self.errors_corrected

    def set_errors_corrected(self, errors_corrected: int):
        """
        Cập nhật số lỗi đã được sửa chữa.

        Input:
            - errors_corrected: Số lỗi đã được sửa chữa (kiểu dữ liệu: int)
        
        Output:
            - Cập nhật thuộc tính errors_corrected của đối tượng.
        """
        self.errors_corrected = errors_corrected

    def get_erasures(self) -> int:
        """
        Trả về số lượng các xóa đã được sửa chữa trong quá trình giải mã.

        Input:
            - Không có đầu vào.
        
        Output:
            - Số lượng xóa đã được sửa chữa (kiểu dữ liệu: int), hoặc None nếu không có.
        """
        return self.erasures

    def set_erasures(self, erasures: int):
        """
        Cập nhật số lượng xóa đã được sửa chữa.

        Input:
            - erasures: Số lượng xóa đã được sửa chữa (kiểu dữ liệu: int)
        
        Output:
            - Cập nhật thuộc tính erasures của đối tượng.
        """
        self.erasures = erasures

    def get_other(self) -> object:
        """
        Trả về thông tin metadata khác (nếu có).

        Input:
            - Không có đầu vào.
        
        Output:
            - Thông tin metadata khác (kiểu dữ liệu: object), hoặc None nếu không có.
        """
        return self.other

    def set_other(self, other: object):
        """
        Cập nhật thông tin metadata khác.

        Input:
            - other: Thông tin metadata khác (kiểu dữ liệu: object)
        
        Output:
            - Cập nhật thuộc tính other của đối tượng.
        """
        self.other = other

    def has_structured_append(self) -> bool:
        """
        Kiểm tra xem có phần append có cấu trúc hay không.

        Input:
            - Không có đầu vào.
        
        Output:
            - True nếu có phần append có cấu trúc, ngược lại False (kiểu dữ liệu: bool).
        """
        return self.structured_append_parity >= 0 and self.structured_append_sequence_number >= 0

    def get_structured_append_parity(self) -> int:
        """
        Trả về giá trị parity của phần append có cấu trúc.

        Input:
            - Không có đầu vào.
        
        Output:
            - Giá trị parity của phần append có cấu trúc (kiểu dữ liệu: int).
        """
        return self.structured_append_parity

    def get_structured_append_sequence_number(self) -> int:
        """
        Trả về số hiệu chuỗi của phần append có cấu trúc.

        Input:
            - Không có đầu vào.
        
        Output:
            - Số hiệu chuỗi của phần append có cấu trúc (kiểu dữ liệu: int).
        """
        return self.structured_append_sequence_number

    def get_symbology_modifier(self) -> int:
        """
        Trả về bộ sửa đổi mã vạch.

        Input:
            - Không có đầu vào.
        
        Output:
            - Bộ sửa đổi mã vạch (kiểu dữ liệu: int).
        """
        return self.symbology_modifier
