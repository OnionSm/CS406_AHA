import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from exceptions import FormatException
print(FormatException.get_format_instance())
from decoder import FormatInformation
from .Version import Version
from enums import DataMask
from .Version import VersionManager
from enums.DataMask import DataMask
class BitMatrixParser:

    def __init__(self, bit_matrix):
        """
        Hàm khởi tạo cho đối tượng BitMatrixParser.
        - Input: bit_matrix (BitMatrix): Đối tượng BitMatrix cần phân tích.
        - Hàm kiểm tra xem chiều cao của BitMatrix có hợp lệ (>= 21 và chia cho 4 dư 1) không.
        - Output: None (nếu không hợp lệ, sẽ ném ra ngoại lệ FormatException).
        """
        self.bit_matrix = bit_matrix
        self.parsed_version = None
        self.parsed_format_info = None
        self.mirror = False
        
        dimension = bit_matrix.get_height()
        if dimension < 21 or (dimension & 0x03) != 1:
            raise FormatException.get_format_instance()

    def read_format_information(self):
        """
        Đọc thông tin định dạng từ một trong hai vị trí của QR Code.
        - Input: None.
        - Hàm sẽ lấy thông tin định dạng của QR Code từ hai vị trí.
        - Output: trả về đối tượng FormatInformation chứa thông tin định dạng QR Code.
        - Nếu không thể đọc thông tin, sẽ ném ra ngoại lệ FormatException.
        """
        if self.parsed_format_info is not None:
            return self.parsed_format_info

        # Đọc các bit format thông tin từ phần trên bên trái
        format_info_bits1 = 0
        for i in range(6):
            format_info_bits1 = self.copy_bit(i, 8, format_info_bits1)
        format_info_bits1 = self.copy_bit(7, 8, format_info_bits1)
        format_info_bits1 = self.copy_bit(8, 8, format_info_bits1)
        format_info_bits1 = self.copy_bit(8, 7, format_info_bits1)
        for j in range(5, -1, -1):
            format_info_bits1 = self.copy_bit(8, j, format_info_bits1)

        # Đọc format thông tin từ phần trên bên phải và dưới bên trái
        dimension = self.bit_matrix.get_height()
        format_info_bits2 = 0
        j_min = dimension - 7
        for j in range(dimension - 1, j_min - 1, -1):
            format_info_bits2 = self.copy_bit(8, j, format_info_bits2)
        for i in range(dimension - 8, dimension):
            format_info_bits2 = self.copy_bit(i, 8, format_info_bits2)

        self.parsed_format_info = FormatInformation.decode_format_information(format_info_bits1, format_info_bits2)
        if self.parsed_format_info is not None:
            return self.parsed_format_info
        raise FormatException.get_format_instance()

    def read_version(self):
        """
        Đọc thông tin phiên bản từ một trong hai vị trí của QR Code.
        - Input: None.
        - Hàm sẽ lấy thông tin phiên bản của QR Code từ hai vị trí.
        - Output: trả về đối tượng Version chứa thông tin phiên bản của QR Code.
        - Nếu không thể đọc thông tin, sẽ ném ra ngoại lệ FormatException.
        """
        if self.parsed_version is not None:
            return self.parsed_version

        dimension = self.bit_matrix.get_height()

        provisional_version = (dimension - 17) // 4
        if provisional_version <= 6:
            return VersionManager.get_version_for_number(provisional_version)

        # Đọc thông tin phiên bản từ góc trên bên phải
        version_bits = 0
        ij_min = dimension - 11
        for j in range(5, -1, -1):
            for i in range(dimension - 9, ij_min - 1, -1):
                version_bits = self.copy_bit(i, j, version_bits)

        parsed_version = Version.decode_version_information(version_bits)
        if parsed_version is not None and parsed_version.get_dimension_for_version() == dimension:
            self.parsed_version = parsed_version
            return parsed_version

        # Thử đọc từ góc dưới bên trái
        version_bits = 0
        for i in range(5, -1, -1):
            for j in range(dimension - 9, ij_min - 1, -1):
                version_bits = self.copy_bit(i, j, version_bits)

        parsed_version = Version.decode_version_information(version_bits)
        if parsed_version is not None and parsed_version.get_dimension_for_version() == dimension:
            self.parsed_version = parsed_version
            return parsed_version
        raise FormatException.get_format_instance()

    def copy_bit(self, i, j, version_bits):
        """
        Sao chép bit từ BitMatrix vào version_bits.
        - Input:
            i (int): Chỉ số dòng của bit cần sao chép.
            j (int): Chỉ số cột của bit cần sao chép.
            version_bits (int): Biến chứa các bit đã sao chép.
        - Output: Trả về version_bits với bit mới được sao chép.
        """
        bit = self.bit_matrix.get(j, i) if not self.mirror else self.bit_matrix.get(i, j)
        return (version_bits << 1) | 0x1 if bit else version_bits << 1

    def read_codewords(self):
        """
        Đọc các mã codewords trong BitMatrix theo đúng thứ tự, tái tạo lại các byte chứa mã QR Code.
        - Input: None.
        - Hàm sẽ đọc thông tin mã hóa từ QR Code và trả về mảng byte chứa các codeword.
        - Output: Trả về mảng byte chứa codewords của QR Code.
        - Nếu không đọc đúng số byte mong muốn, sẽ ném ra ngoại lệ FormatException.
        """
        DATA_MASKS = {
            0: DataMask000,
            1: DataMask001,
            2: DataMask010,
            3: DataMask011,
            4: DataMask100,
            5: DataMask101,
            6: DataMask110,
            7: DataMask111,
        }
        format_info = self.read_format_information()
        version = self.read_version()

        # Lấy data mask cho định dạng QR Code, loại bỏ các bit không cần thiết.
        data_mask = DataMask.values()[format_info.get_data_mask()]
        dimension = self.bit_matrix.get_height()
        data_mask.unmask_bit_matrix(self.bit_matrix, dimension)

        function_pattern = version.build_function_pattern()

        reading_up = True
        result = bytearray(version.get_total_codewords())
        result_offset = 0
        current_byte = 0
        bits_read = 0

        # Đọc cột theo cặp từ phải sang trái
        for j in range(dimension - 1, 0, -2):
            if j == 6:
                j -= 1
            for count in range(dimension):
                i = dimension - 1 - count if reading_up else count
                for col in range(2):
                    if not function_pattern.get(j - col, i):
                        bits_read += 1
                        current_byte <<= 1
                        if self.bit_matrix.get(j - col, i):
                            current_byte |= 1
                        if bits_read == 8:
                            result[result_offset] = current_byte
                            result_offset += 1
                            bits_read = 0
                            current_byte = 0
            reading_up ^= True  # Thay đổi chiều đọc
        if result_offset != version.get_total_codewords():
            raise FormatException.get_format_instance()
        return bytes(result)

    def remask(self):
        """
        Đảo ngược việc bỏ mask khi đọc codewords. Trả lại BitMatrix về trạng thái ban đầu.
        - Input: None.
        - Output: Không có trả về. Chỉ thực hiện thao tác đảo ngược mask.
        """
        if self.parsed_format_info is None:
            return  # Không có format info, không có data mask để bỏ
        data_mask = DataMask.values()[self.parsed_format_info.get_data_mask()]
        dimension = self.bit_matrix.get_height()
        data_mask.unmask_bit_matrix(self.bit_matrix, dimension)

    def set_mirror(self, mirror):
        """
        Chuẩn bị parser cho phép thao tác với dữ liệu dạng gương (mirrored).
        - Input: mirror (bool): Cờ cho biết có áp dụng thao tác gương hay không.
        - Output: Không có trả về. Thiết lập cờ mirror và làm mới thông tin version và format.
        """
        self.parsed_version = None
        self.parsed_format_info = None
        self.mirror = mirror

    def mirror(self):
        """
        Lật ngược BitMatrix để thử đọc lại từ gương (mirrored) nếu cần.
        - Input: None.
        - Output: Thực hiện đảo ngược (flip) các bit trong BitMatrix.
        """
        for x in range(self.bit_matrix.get_width()):
            for y in range(x + 1, self.bit_matrix.get_height()):
                if self.bit_matrix.get(x, y) != self.bit_matrix.get(y, x):
                    self.bit_matrix.flip(y, x)
                    self.bit_matrix.flip(x, y)
