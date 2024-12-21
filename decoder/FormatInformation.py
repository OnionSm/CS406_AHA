import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from enums import ErrorCorrectionLevel

class FormatInformation:
    FORMAT_INFO_MASK_QR = 0x5412

    FORMAT_INFO_DECODE_LOOKUP = [
        [0x5412, 0x00],
        [0x5125, 0x01],
        [0x5E7C, 0x02],
        [0x5B4B, 0x03],
        [0x45F9, 0x04],
        [0x40CE, 0x05],
        [0x4F97, 0x06],
        [0x4AA0, 0x07],
        [0x77C4, 0x08],
        [0x72F3, 0x09],
        [0x7DAA, 0x0A],
        [0x789D, 0x0B],
        [0x662F, 0x0C],
        [0x6318, 0x0D],
        [0x6C41, 0x0E],
        [0x6976, 0x0F],
        [0x1689, 0x10],
        [0x13BE, 0x11],
        [0x1CE7, 0x12],
        [0x19D0, 0x13],
        [0x0762, 0x14],
        [0x0255, 0x15],
        [0x0D0C, 0x16],
        [0x083B, 0x17],
        [0x355F, 0x18],
        [0x3068, 0x19],
        [0x3F31, 0x1A],
        [0x3A06, 0x1B],
        [0x24B4, 0x1C],
        [0x2183, 0x1D],
        [0x2EDA, 0x1E],
        [0x2BED, 0x1F],
    ]

    def __init__(self, format_info):
        """
        Hàm khởi tạo đối tượng FormatInformation với mã format_info.

        Input: 
            format_info (int): Giá trị mã format thông tin.
        Output:
            Tạo ra một đối tượng FormatInformation chứa thông tin mức độ sửa lỗi và mặt nạ dữ liệu.
        """
        # Các bit 3,4 chỉ định mức độ sửa lỗi
        self.errorCorrectionLevel = ErrorCorrectionLevel.for_bits((format_info >> 3) & 0x03)
        # Các bit dưới cùng 3 chỉ định mặt nạ dữ liệu
        self.dataMask = format_info & 0x07

    @staticmethod
    def num_bits_differring(a, b):
        """
        Hàm tính số bit khác nhau giữa hai giá trị.

        Input: 
            a (int): Giá trị số nguyên thứ nhất.
            b (int): Giá trị số nguyên thứ hai.
        Output:
            int: Số bit khác nhau giữa hai giá trị a và b.
        """
        return bin(a ^ b).count('1')

    @staticmethod
    def decode_format_information(masked_format_info1, masked_format_info2):
        """
        Giải mã thông tin format từ hai giá trị đã bị áp dụng mặt nạ.

        Input:
            masked_format_info1 (int): Thông tin format đã bị mặt nạ lần 1.
            masked_format_info2 (int): Thông tin format đã bị mặt nạ lần 2.
        Output:
            FormatInformation hoặc None: Trả về đối tượng FormatInformation nếu giải mã thành công, 
            ngược lại trả về None.
        """
        format_info = FormatInformation.do_decode_format_information(masked_format_info1, masked_format_info2)
        if format_info:
            return format_info
        # Nếu không tìm thấy, thử áp dụng mặt nạ QR
        return FormatInformation.do_decode_format_information(masked_format_info1 ^ FormatInformation.FORMAT_INFO_MASK_QR,
                                                              masked_format_info2 ^ FormatInformation.FORMAT_INFO_MASK_QR)

    @staticmethod
    def do_decode_format_information(masked_format_info1, masked_format_info2):
        """
        Thực hiện giải mã thông tin format từ hai giá trị đã bị áp dụng mặt nạ.

        Input: 
            masked_format_info1 (int): Thông tin format đã bị mặt nạ lần 1.
            masked_format_info2 (int): Thông tin format đã bị mặt nạ lần 2.
        Output:
            FormatInformation hoặc None: Trả về đối tượng FormatInformation nếu tìm thấy sự tương đồng
            trong bảng mã, ngược lại trả về None.
        """
        best_difference = float('inf')
        best_format_info = 0
        for decode_info in FormatInformation.FORMAT_INFO_DECODE_LOOKUP:
            target_info = decode_info[0]
            if target_info == masked_format_info1 or target_info == masked_format_info2:
                return FormatInformation(decode_info[1])
            bits_difference = FormatInformation.num_bits_differring(masked_format_info1, target_info)
            if bits_difference < best_difference:
                best_format_info = decode_info[1]
                best_difference = bits_difference
            if masked_format_info1 != masked_format_info2:
                bits_difference = FormatInformation.num_bits_differring(masked_format_info2, target_info)
                if bits_difference < best_difference:
                    best_format_info = decode_info[1]
                    best_difference = bits_difference
        if best_difference <= 3:
            return FormatInformation(best_format_info)
        return None

    def get_error_correction_level(self):
        """
        Trả về mức độ sửa lỗi của QR code.

        Output:
            ErrorCorrectionLevel: Mức độ sửa lỗi của QR code.
        """
        return self.errorCorrectionLevel

    def get_data_mask(self):
        """
        Trả về mặt nạ dữ liệu của QR code.

        Output:
            int: Mặt nạ dữ liệu (dưới dạng byte).
        """
        return self.dataMask

    def __eq__(self, other):
        """
        So sánh đối tượng hiện tại với một đối tượng FormatInformation khác.

        Input:
            other (FormatInformation): Đối tượng FormatInformation khác.
        Output:
            bool: True nếu hai đối tượng có cùng mức độ sửa lỗi và mặt nạ dữ liệu, ngược lại trả về False.
        """
        if not isinstance(other, FormatInformation):
            return False
        return self.errorCorrectionLevel == other.errorCorrectionLevel and self.dataMask == other.dataMask

    def __hash__(self):
        """
        Tính toán giá trị hash của đối tượng.

        Output:
            int: Giá trị hash của đối tượng FormatInformation.
        """
        return (self.errorCorrectionLevel << 3) | self.dataMask
