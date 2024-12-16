from enums import ErrorCorrectionLevel

class FormatInformation:
    FORMAT_INFO_MASK_QR = 0x5412

    # ISO 18004:2006, Annex C, Table C.1
    FORMAT_INFO_DECODE_LOOKUP = [
        (0x5412, 0x00),
        (0x5125, 0x01),
        (0x5E7C, 0x02),
        (0x5B4B, 0x03),
        (0x45F9, 0x04),
        (0x40CE, 0x05),
        (0x4F97, 0x06),
        (0x4AA0, 0x07),
        (0x77C4, 0x08),
        (0x72F3, 0x09),
        (0x7DAA, 0x0A),
        (0x789D, 0x0B),
        (0x662F, 0x0C),
        (0x6318, 0x0D),
        (0x6C41, 0x0E),
        (0x6976, 0x0F),
        (0x1689, 0x10),
        (0x13BE, 0x11),
        (0x1CE7, 0x12),
        (0x19D0, 0x13),
        (0x0762, 0x14),
        (0x0255, 0x15),
        (0x0D0C, 0x16),
        (0x083B, 0x17),
        (0x355F, 0x18),
        (0x3068, 0x19),
        (0x3F31, 0x1A),
        (0x3A06, 0x1B),
        (0x24B4, 0x1C),
        (0x2183, 0x1D),
        (0x2EDA, 0x1E),
        (0x2BED, 0x1F),
    ]

    def __init__(self, format_info):
        
        # Bits 3,4
        self.error_correction_level = ErrorCorrectionLevel.for_bits((format_info >> 3) & 0x03)
        # Bottom 3 bits
        self.data_mask = format_info & 0x07

    @staticmethod
    def num_bits_differing(a, b):
        """Calculates the Hamming distance (number of differing bits) between two integers."""
        return bin(a ^ b).count('1')


    @staticmethod 
    def decode_format_infomation(marked_format_info_1, marked_format_info_2):
        """
        Input : 
        - masked_format_info_1 : int 
        - masked_format_info_2 : int
        """
        format_info = FormatInformation.do_decode_format_infomation(marked_format_info_1, marked_format_info_2)
        if format_info != None:
            return format_info
        return FormatInformation.do_decode_format_infomation(marked_format_info_1 ^ FormatInformation.FORMAT_INFO_MASK_QR,
                                                             marked_format_info_2 ^ FormatInformation.FORMAT_INFO_MASK_QR)

    @staticmethod
    def do_decode_format_information(masked_format_info1, masked_format_info2):
        """
        Giải mã thông tin định dạng từ hai giá trị mã hóa.
        
        :param masked_format_info1: Giá trị định dạng đã mã hóa đầu tiên.
        :param masked_format_info2: Giá trị định dạng đã mã hóa thứ hai.
        :return: Một đối tượng FormatInformation nếu tìm thấy kết quả phù hợp, ngược lại trả về None.
        """
        # Tìm giá trị trong FORMAT_INFO_DECODE_LOOKUP có số bit khác nhau ít nhất
        best_difference = float('inf')  # Sử dụng vô cực để so sánh ban đầu
        best_format_info = 0

        for decode_info in FormatInformation.FORMAT_INFO_DECODE_LOOKUP:
            target_info = decode_info[0]

            if target_info == masked_format_info1 or target_info == masked_format_info2:
                # Tìm thấy một kết quả khớp chính xác
                return FormatInformation(decode_info[1])

            bits_difference = FormatInformation.num_bits_differing(masked_format_info1, target_info)
            if bits_difference < best_difference:
                best_format_info = decode_info[1]
                best_difference = bits_difference

            if masked_format_info1 != masked_format_info2:
                # Cũng thử với giá trị còn lại
                bits_difference = FormatInformation.num_bits_differing(masked_format_info2, target_info)
                if bits_difference < best_difference:
                    best_format_info = decode_info[1]
                    best_difference = bits_difference

        # Khoảng cách Hamming của 32 mã đã được mã hóa là 7, nên <= 3 bit khác nhau nghĩa là tìm được kết quả khớp
        if best_difference <= 3:
            return FormatInformation(best_format_info)

        return None
    
    def get_error_correction_level(self):
        return self.error_correction_level
    
    def get_data_mark(self):
        return self.data_mask
    
    def __hash__(self):
        """
        Trả về mã băm của đối tượng, sử dụng cấp độ sửa lỗi (error_correction_level) và data_mask.
        """
        return (self.error_correction_level.ordinal() << 3) | self.data_mask

    def __eq__(self, other):
        """
        Kiểm tra xem hai đối tượng FormatInformation có bằng nhau không.
        """
        if not isinstance(other, FormatInformation):
            return False
        return (self.error_correction_level == other.error_correction_level and
                self.data_mask == other.data_mask)