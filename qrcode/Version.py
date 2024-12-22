import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from exceptions import FormatException
from .FormatInformation import FormatInformation
from .BitMatrix import BitMatrix

class Version:
    class ECBlocks:
        """
        EBClocks đại diện cho thông tin sửa lỗi ở một mức độ cụ thể
        QR code có 4 mức độ sửa lỗi là L, M, Q, H
        """
        def __init__(self, ec_codewords_per_block, *ec_blocks):
            """
            Input: 
            - ec_codewords_per_block : int
            - *ec_blocks : ECB
            """
            self.ec_codewords_per_block = ec_codewords_per_block
            self.ec_blocks = list(ec_blocks)  # Chuyển các ECB thành danh sách

        def get_ec_codewords_per_block(self): # ==> int 
            return self.ec_codewords_per_block

        def get_num_blocks(self): # ==> int 
            total = 0
            for ec_block in self.ec_blocks:
                total += ec_block.get_count()
            return total

        def get_total_ec_codewords(self):
            return self.ec_codewords_per_block * self.get_num_blocks()

        def get_ec_blocks(self):
            return self.ec_blocks
    
    class ECB:
        def __init__(self, count, data_codewords):
            """
            Input: count, data_codewords : int
            """
            self.count = count
            self.data_codewords = data_codewords
        
        def get_count(self):
            return self.count
        def get_data_codewords(self):
            return self.data_codewords
        
    VERSION_DECODE_INFO = [
        0x07C94, 0x085BC, 0x09A99, 0x0A4D3, 0x0BBF6,
        0x0C762, 0x0D847, 0x0E60D, 0x0F928, 0x10B78,
        0x1145D, 0x12A17, 0x13532, 0x149A6, 0x15683,
        0x168C9, 0x177EC, 0x18EC4, 0x191E1, 0x1AFAB,
        0x1B08E, 0x1CC1A, 0x1D33F, 0x1ED75, 0x1F250,
        0x209D5, 0x216F0, 0x228BA, 0x2379F, 0x24B0B,
        0x2542E, 0x26A64, 0x27541, 0x28C69
    ]

    def __init__(self, version_number, alignment_pattern_centers, *ec_blocks):
        """
        Input:
        - version_number : int 
        - alignment_pattern_centers : int []
        - *ec_blocks : ECBlocks
        Property: 
        - version_number : int 
        - ec_codewords : int
        - ecb_array : ECB []
        - total_codewords : int
        """
        
        self.version_number = version_number
        self.alignment_pattern_centers = alignment_pattern_centers
        self.ec_blocks = ec_blocks
        total = 0
        ec_codewords = ec_blocks[0].get_ec_codewords_per_block()
        ecb_array = ec_blocks[0].get_ec_blocks()
        for ec_block in ecb_array:
            total += ec_block.get_count() * (ec_block.get_data_codewords() + ec_codewords)
        self.total_codewords = total

    def get_version_number(self):
        return self.version_number

    def get_alignment_pattern_centers(self):
        return self.alignment_pattern_centers

    def get_total_codewords(self):
        return self.total_codewords

    # @staticmethod
    def get_dimension_for_version(self):
        return 17 + 4 * self.version_number

    def get_ec_blocks_for_level(self, ec_level):
        return self.ec_blocks[ec_level.value]  # Assuming ECLevel is an enum

    @staticmethod
    def getProvisionalVersionForDimension(dimension):
        if dimension % 4 != 1:
            raise FormatException.getFormatInstance()

        try:
            return Version.getVersionForNumber((dimension - 17) // 4)
        except ValueError:
            raise FormatException.getFormatInstance()

    # @staticmethod
    # def get_version_for_number(versionNumber):
    #     if versionNumber < 1 or versionNumber > 40:
    #         raise ValueError("Invalid version number")
    #     return Version.VERSIONS[versionNumber - 1]
    
    @staticmethod
    def decode_version_information(version_bits):
        best_difference = float('inf')
        best_version = 0
        version_amount = len(Version.VERSION_DECODE_INFOR)
        for i in range(0, version_amount):
            target_version = Version.VERSION_DECODE_INFO[i]
            if target_version == version_bits:
                return Version.get_version_for_number(i+7)
            bits_difference = FormatInformation.num_bits_differing(version_bits, target_version)
            if bits_difference < best_difference:
                best_version = i + 7
                best_difference = bits_difference
            
        if best_difference <= 3:
            return Version.get_version_for_number(best_version)
        return None

    def build_function_pattern(self):
        """
        Output : bit_matrix: BitMatrix
        """
        dimension = self.get_dimension_for_version()
        bit_matrix = BitMatrix(dimension)
        bit_matrix.set_region(0, 0, 9, 9)
        bit_matrix.set_region(dimension - 8, 0, 8, 9)
        bit_matrix.set_region(0, dimension - 8, 9, 8)
        max = len(self.alignment_pattern_centers)
        for x in range(0, max):
            i = self.alignment_pattern_centers[x] - 2
            for y in range(0, max):
                if ((x != 0 or (y != 0 and y != max - 1)) and (x != max - 1 or y != 0)):
                    bit_matrix.set_region(self.alignment_pattern_centers[y]- 2, i, 5, 5)
                # else no o alignment patterns near the three finder patterns
        
        # Vertical timing pattern
        bit_matrix.set_region(6, 9, 1, dimension - 17)
        # Horizontal timing pattern
        bit_matrix.set_region(9, 6, dimension - 17, 1)
        
        if self.version_number > 6:
            # Version info, top right
            bit_matrix.set_region(dimension - 11, 0, 3, 6)
            # Version info, bottom left
            bit_matrix.set_region(0, dimension - 11, 6, 3)
        
        return bit_matrix
    
def build_versions():
    """
    Output : Version []
    """
    return [
    Version(1, [],
        Version.ECBlocks(7, Version.ECB(1,19)),
        Version.ECBlocks(10, Version.ECB(1,16)),
        Version.ECBlocks(13, Version.ECB(1,13)),
        Version.ECBlocks(17, Version.ECB(1,9))),
        
    Version(2, [6,18],
        Version.ECBlocks(10, Version.ECB(1,34)),
        Version.ECBlocks(16, Version.ECB(1,28)),
        Version.ECBlocks(22, Version.ECB(1,22)),
        Version.ECBlocks(28, Version.ECB(1,16))),

    Version(3, [6,22],
        Version.ECBlocks(15, Version.ECB(1,55)),
        Version.ECBlocks(26, Version.ECB(1,44)),
        Version.ECBlocks(18, Version.ECB(2,17)),
        Version.ECBlocks(22, Version.ECB(2,13))),

    Version(4, [6, 26],
        Version.ECBlocks(20, Version.ECB(1, 80)),
        Version.ECBlocks(18, Version.ECB(2, 32)),
        Version.ECBlocks(26, Version.ECB(2, 24)),
        Version.ECBlocks(16, Version.ECB(4, 9))),

    Version(5, [6, 30],
        Version.ECBlocks(26, Version.ECB(1, 108)),
        Version.ECBlocks(24, Version.ECB(2, 43)),
        Version.ECBlocks(18, Version.ECB(2, 15), Version.ECB(2, 16)),
        Version.ECBlocks(22, Version.ECB(2, 11), Version.ECB(2, 12))),

    Version(6, [6, 34],
        Version.ECBlocks(18, Version.ECB(2, 68)),
        Version.ECBlocks(16, Version.ECB(4, 27)),
        Version.ECBlocks(24, Version.ECB(4, 19)),
        Version.ECBlocks(28, Version.ECB(4, 15))),

    Version(7, [6, 22, 38],
        Version.ECBlocks(20, Version.ECB(2, 78)),
        Version.ECBlocks(18, Version.ECB(4, 31)),
        Version.ECBlocks(18, Version.ECB(2, 14), Version.ECB(4, 15)),
        Version.ECBlocks(26, Version.ECB(4, 13), Version.ECB(1, 14))),

    Version(8, [6, 24, 42],
        Version.ECBlocks(24, Version.ECB(2, 97)),
        Version.ECBlocks(22, Version.ECB(2, 38), Version.ECB(2, 39)),
        Version.ECBlocks(22, Version.ECB(4, 18), Version.ECB(2, 19)),
        Version.ECBlocks(26, Version.ECB(4, 14), Version.ECB(2, 15))),

    Version(9, [6, 26, 46],
        Version.ECBlocks(30, Version.ECB(2, 116)),
        Version.ECBlocks(22, Version.ECB(3, 36), Version.ECB(2, 37)),
        Version.ECBlocks(20, Version.ECB(4, 16), Version.ECB(4, 17)),
        Version.ECBlocks(24, Version.ECB(4, 12), Version.ECB(4, 13))),

    Version(10, [6, 28, 50],
        Version.ECBlocks(18, Version.ECB(2, 68), Version.ECB(2, 69)),
        Version.ECBlocks(26, Version.ECB(4, 43), Version.ECB(1, 44)),
        Version.ECBlocks(24, Version.ECB(6, 19), Version.ECB(2, 20)),
        Version.ECBlocks(28, Version.ECB(6, 15), Version.ECB(2, 16))),
        
    Version(11, [6, 30, 54],
        Version.ECBlocks(20, Version.ECB(4, 81)),
        Version.ECBlocks(30, Version.ECB(1, 50), Version.ECB(4, 51)),
        Version.ECBlocks(28, Version.ECB(4, 22), Version.ECB(4, 23)),
        Version.ECBlocks(24, Version.ECB(3, 12), Version.ECB(8, 13))),

    Version(12, [6, 32, 58],
        Version.ECBlocks(24, Version.ECB(2, 92), Version.ECB(2, 93)),
        Version.ECBlocks(22, Version.ECB(6, 36), Version.ECB(2, 37)),
        Version.ECBlocks(26, Version.ECB(4, 20), Version.ECB(6, 21)),
        Version.ECBlocks(28, Version.ECB(7, 14), Version.ECB(4, 15))),

    Version(13, [6, 34, 62],
        Version.ECBlocks(26, Version.ECB(4, 107)),
        Version.ECBlocks(22, Version.ECB(8, 37), Version.ECB(1, 38)),
        Version.ECBlocks(24, Version.ECB(8, 20), Version.ECB(4, 21)),
        Version.ECBlocks(22, Version.ECB(12, 11), Version.ECB(4, 12))),

    Version(14, [6, 26, 46, 66],
        Version.ECBlocks(30, Version.ECB(3, 115), Version.ECB(1, 116)),
        Version.ECBlocks(24, Version.ECB(4, 40), Version.ECB(5, 41)),
        Version.ECBlocks(20, Version.ECB(11, 16), Version.ECB(5, 17)),
        Version.ECBlocks(24, Version.ECB(11, 12), Version.ECB(5, 13))),

    Version(15, [6, 26, 48, 70],
        Version.ECBlocks(22, Version.ECB(5, 87), Version.ECB(1, 88)),
        Version.ECBlocks(24, Version.ECB(5, 41), Version.ECB(5, 42)),
        Version.ECBlocks(30, Version.ECB(5, 24), Version.ECB(7, 25)),
        Version.ECBlocks(24, Version.ECB(11, 12), Version.ECB(7, 13))),

    Version(16, [6, 26, 50, 74],
        Version.ECBlocks(24, Version.ECB(5, 98), Version.ECB(1, 99)),
        Version.ECBlocks(28, Version.ECB(7, 45), Version.ECB(3, 46)),
        Version.ECBlocks(24, Version.ECB(15, 19), Version.ECB(2, 20)),
        Version.ECBlocks(30, Version.ECB(3, 15), Version.ECB(13, 16))),

    Version(17, [6, 30, 54, 78],
        Version.ECBlocks(28, Version.ECB(1, 107), Version.ECB(5, 108)),
        Version.ECBlocks(28, Version.ECB(10, 46), Version.ECB(1, 47)),
        Version.ECBlocks(28, Version.ECB(1, 22), Version.ECB(15, 23)),
        Version.ECBlocks(28, Version.ECB(2, 14), Version.ECB(17, 15))),

    Version(18, [6, 30, 56, 82],
        Version.ECBlocks(30, Version.ECB(5, 120), Version.ECB(1, 121)),
        Version.ECBlocks(26, Version.ECB(9, 43), Version.ECB(4, 44)),
        Version.ECBlocks(28, Version.ECB(17, 22), Version.ECB(1, 23)),
        Version.ECBlocks(28, Version.ECB(2, 14), Version.ECB(19, 15))),

    Version(19, [6, 30, 58, 86],
        Version.ECBlocks(28, Version.ECB(3, 113), Version.ECB(4, 114)),
        Version.ECBlocks(26, Version.ECB(3, 44), Version.ECB(11, 45)),
        Version.ECBlocks(26, Version.ECB(17, 21), Version.ECB(4, 22)),
        Version.ECBlocks(26, Version.ECB(9, 13), Version.ECB(16, 14))),

    Version(20, [6, 34, 62, 90],
        Version.ECBlocks(28, Version.ECB(3, 107), Version.ECB(5, 108)),
        Version.ECBlocks(26, Version.ECB(3, 41), Version.ECB(13, 42)),
        Version.ECBlocks(30, Version.ECB(15, 24), Version.ECB(5, 25)),
        Version.ECBlocks(28, Version.ECB(15, 15), Version.ECB(10, 16))),

    Version(21, [6, 28, 50, 72, 94],
        Version.ECBlocks(28, Version.ECB(4, 116), Version.ECB(4, 117)),
        Version.ECBlocks(26, Version.ECB(17, 42)),
        Version.ECBlocks(28, Version.ECB(17, 22), Version.ECB(6, 23)),
        Version.ECBlocks(30, Version.ECB(19, 16), Version.ECB(6, 17))),

    Version(22, [6, 26, 50, 74, 98],
        Version.ECBlocks(28, Version.ECB(2, 111), Version.ECB(7, 112)),
        Version.ECBlocks(28, Version.ECB(17, 46)),
        Version.ECBlocks(30, Version.ECB(7, 24), Version.ECB(16, 25)),
        Version.ECBlocks(24, Version.ECB(34, 13))),

    Version(23, [6, 30, 54, 78, 102],
        Version.ECBlocks(30, Version.ECB(4, 121), Version.ECB(5, 122)),
        Version.ECBlocks(28, Version.ECB(4, 47), Version.ECB(14, 48)),
        Version.ECBlocks(30, Version.ECB(11, 24), Version.ECB(14, 25)),
        Version.ECBlocks(30, Version.ECB(16, 15), Version.ECB(14, 16))),

    Version(24, [6, 28, 54, 80, 106],
        Version.ECBlocks(30, Version.ECB(6, 117), Version.ECB(4, 118)),
        Version.ECBlocks(28, Version.ECB(6, 45), Version.ECB(14, 46)),
        Version.ECBlocks(30, Version.ECB(11, 24), Version.ECB(16, 25)),
        Version.ECBlocks(30, Version.ECB(30, 16), Version.ECB(2, 17))),

    Version(25, [6, 32, 58, 84, 110],
        Version.ECBlocks(26, Version.ECB(8, 106), Version.ECB(4, 107)),
        Version.ECBlocks(28, Version.ECB(8, 47), Version.ECB(13, 48)),
        Version.ECBlocks(30, Version.ECB(7, 24), Version.ECB(22, 25)),
        Version.ECBlocks(30, Version.ECB(22, 15), Version.ECB(13, 16))),

    Version(26, [6, 30, 58, 86, 114],
        Version.ECBlocks(28, Version.ECB(10, 114), Version.ECB(2, 115)),
        Version.ECBlocks(28, Version.ECB(19, 46), Version.ECB(4, 47)),
        Version.ECBlocks(28, Version.ECB(28, 22), Version.ECB(6, 23)),
        Version.ECBlocks(30, Version.ECB(33, 16), Version.ECB(4, 17))),

    Version(27, [6, 34, 62, 90, 118],
        Version.ECBlocks(30, Version.ECB(8, 122), Version.ECB(4, 123)),
        Version.ECBlocks(28, Version.ECB(22, 45), Version.ECB(3, 46)),
        Version.ECBlocks(30, Version.ECB(8, 23), Version.ECB(26, 24)),
        Version.ECBlocks(30, Version.ECB(12, 15), Version.ECB(28, 16))),

    Version(28, [6, 26, 50, 74, 98, 122],
        Version.ECBlocks(30, Version.ECB(3, 117), Version.ECB(10, 118)),
        Version.ECBlocks(28, Version.ECB(3, 45), Version.ECB(23, 46)),
        Version.ECBlocks(30, Version.ECB(4, 24), Version.ECB(31, 25)),
        Version.ECBlocks(30, Version.ECB(11, 15), Version.ECB(31, 16))),

    Version(29, [6, 30, 54, 78, 102, 126],
        Version.ECBlocks(30, Version.ECB(7, 116), Version.ECB(7, 117)),
        Version.ECBlocks(28, Version.ECB(21, 45), Version.ECB(7, 46)),
        Version.ECBlocks(30, Version.ECB(1, 23), Version.ECB(37, 24)),
        Version.ECBlocks(30, Version.ECB(19, 15), Version.ECB(26, 16))),

    Version(30, [6, 26, 52, 78, 104, 130],
        Version.ECBlocks(30, Version.ECB(5, 115), Version.ECB(10, 116)),
        Version.ECBlocks(28, Version.ECB(19, 47), Version.ECB(10, 48)),
        Version.ECBlocks(30, Version.ECB(15, 24), Version.ECB(25, 25)),
        Version.ECBlocks(30, Version.ECB(23, 15), Version.ECB(25, 16))),

    Version(31, [6, 30, 56, 82, 108, 134],
        Version.ECBlocks(30, Version.ECB(13, 115), Version.ECB(3, 116)),
        Version.ECBlocks(28, Version.ECB(2, 46), Version.ECB(29, 47)),
        Version.ECBlocks(30, Version.ECB(42, 24), Version.ECB(1, 25)),
        Version.ECBlocks(30, Version.ECB(23, 15), Version.ECB(28, 16))),

    Version(32, [6, 34, 60, 86, 112, 138],
        Version.ECBlocks(30, Version.ECB(17, 115)),
        Version.ECBlocks(28, Version.ECB(10, 46), Version.ECB(23, 47)),
        Version.ECBlocks(30, Version.ECB(10, 24), Version.ECB(35, 25)),
        Version.ECBlocks(30, Version.ECB(19, 15), Version.ECB(35, 16))),

    Version(33, [6, 30, 58, 86, 114, 142],
        Version.ECBlocks(30, Version.ECB(17, 115), Version.ECB(1, 116)),
        Version.ECBlocks(28, Version.ECB(14, 46), Version.ECB(21, 47)),
        Version.ECBlocks(30, Version.ECB(29, 24), Version.ECB(19, 25)),
        Version.ECBlocks(30, Version.ECB(11, 15), Version.ECB(46, 16))),

    Version(34, [6, 34, 62, 90, 118, 146],
        Version.ECBlocks(30, Version.ECB(13, 115), Version.ECB(6, 116)),
        Version.ECBlocks(28, Version.ECB(14, 46), Version.ECB(23, 47)),
        Version.ECBlocks(30, Version.ECB(44, 24), Version.ECB(7, 25)),
        Version.ECBlocks(30, Version.ECB(59, 16), Version.ECB(1, 17))),

    Version(35, [6, 30, 54, 78, 102, 126, 150],
        Version.ECBlocks(30, Version.ECB(12, 121), Version.ECB(7, 122)),
        Version.ECBlocks(28, Version.ECB(12, 47), Version.ECB(26, 48)),
        Version.ECBlocks(30, Version.ECB(39, 24), Version.ECB(14, 25)),
        Version.ECBlocks(30, Version.ECB(22, 15), Version.ECB(41, 16))),

    Version(36, [6, 24, 50, 76, 102, 128, 154],
        Version.ECBlocks(30, Version.ECB(6, 121), Version.ECB(14, 122)),
        Version.ECBlocks(28, Version.ECB(6, 47), Version.ECB(34, 48)),
        Version.ECBlocks(30, Version.ECB(46, 24), Version.ECB(10, 25)),
        Version.ECBlocks(30, Version.ECB(2, 15), Version.ECB(64, 16))),

    Version(37, [6, 28, 54, 80, 106, 132, 158],
        Version.ECBlocks(30, Version.ECB(17, 122), Version.ECB(4, 123)),
        Version.ECBlocks(28, Version.ECB(29, 46), Version.ECB(14, 47)),
        Version.ECBlocks(30, Version.ECB(49, 24), Version.ECB(10, 25)),
        Version.ECBlocks(30, Version.ECB(24, 15), Version.ECB(46, 16))),

    Version(38, [6, 32, 58, 84, 110, 136, 162],
        Version.ECBlocks(30, Version.ECB(4, 122), Version.ECB(18, 123)),
        Version.ECBlocks(28, Version.ECB(13, 46), Version.ECB(32, 47)),
        Version.ECBlocks(30, Version.ECB(48, 24), Version.ECB(14, 25)),
        Version.ECBlocks(30, Version.ECB(42, 15), Version.ECB(32, 16))),

    Version(39, [6, 26, 54, 82, 110, 138, 166],
        Version.ECBlocks(30, Version.ECB(20, 117), Version.ECB(4, 118)),
        Version.ECBlocks(28, Version.ECB(40, 47), Version.ECB(7, 48)),
        Version.ECBlocks(30, Version.ECB(43, 24), Version.ECB(22, 25)),
        Version.ECBlocks(30, Version.ECB(10, 15), Version.ECB(67, 16))),

    Version(40, [6, 30, 58, 86, 114, 142, 170],
        Version.ECBlocks(30, Version.ECB(19, 118), Version.ECB(6, 119)),
        Version.ECBlocks(28, Version.ECB(18, 47), Version.ECB(31, 48)),
        Version.ECBlocks(30, Version.ECB(34, 24), Version.ECB(34, 25)),
        Version.ECBlocks(30, Version.ECB(20, 15), Version.ECB(61, 16)))
    ]


class VersionManager:
    VERSIONS = build_versions()
    def __init__(self):
        pass 

    @staticmethod
    def get_version_for_number(versionNumber):
        if versionNumber < 1 or versionNumber > 40:
            raise ValueError("Invalid version number")
        return Version.VERSIONS[versionNumber - 1]
