import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from decoder import Decoder
from enums import DecodeHintType, ResultMetadataType, BarcodeFormat
from qr_patterns import Detector, DetectorResult, FinderPatternInfo
from qrcode import Result, QRCodeDecoderMetaData, BitMatrix, BinaryBitmap
from exceptions import NotFoundException


class QRCodeReader:
    """
    Lớp này có thể phát hiện và giải mã QR Code trong một bức ảnh.
    """

    NO_POINTS = []

    def __init__(self):
        self.decoder = Decoder()

    def get_decoder(self):
        """ 
        Trả về đối tượng giải mã QR code.
        """
        return self.decoder
    
    def decode(self, image: BinaryBitmap, hints=None):
        """
        Phát hiện và giải mã QR code trong bức ảnh.

        Input:
        - image: đối tượng BinaryBitmap, chứa thông tin ảnh cần giải mã.
        - hints: một từ điển chứa các gợi ý giải mã (tùy chọn).

        Hàm này sẽ phát hiện và giải mã QR code trong bức ảnh được truyền vào.

        Output:
        - Trả về đối tượng Result chứa kết quả giải mã (nội dung, byte segments, points, thông tin bổ sung).
        """
        decoder_result = None
        points = None
        if hints and DecodeHintType.PURE_BARCODE in hints:
            bits: BitMatrix = self.extract_pure_bits(image.get_black_matrix())
            decoder_result = self.decoder.decode(bits, hints)
            points = self.NO_POINTS
        else:
            detector_result ,  info  = Detector(image.get_black_matrix()).detect(hints)
            return detector_result, info
        
    def decode2(self, image:BinaryBitmap, finder_pattern_info):
        detector_result, info = Detector(image.get_black_matrix()).process_finder_pattern_info(finder_pattern_info)
        return detector_result, info
    
    def reset(self):
        """
        Hàm này không làm gì cả, không có tác dụng.
        """
        pass

    def extract_pure_bits(self, image):
        """
        Phát hiện mã trong ảnh "thuần túy", tức là ảnh chỉ chứa một mã không xoay hoặc không nghiêng, với biên trắng xung quanh.

        Input:
        - image: đối tượng BitMatrix, ảnh chứa QR code cần giải mã.

        Hàm này sẽ trả về một ma trận bit (BitMatrix) từ ảnh.

        Output:
        - Trả về một đối tượng BitMatrix chứa mã QR code đã được trích xuất.
        """
        left_top_black = image.get_top_left_on_bit()
        right_bottom_black = image.get_bottom_right_on_bit()
        if left_top_black is None or right_bottom_black is None:
            raise NotFoundException("Không tìm thấy QR code trong ảnh")

        module_size = self.module_size(left_top_black, image)

        top = left_top_black[1]
        bottom = right_bottom_black[1]
        left = left_top_black[0]
        right = right_bottom_black[0]

        if left >= right or top >= bottom:
            raise NotFoundException("Không tìm thấy QR code trong ảnh")

        if bottom - top != right - left:
            right = left + (bottom - top)
            if right >= image.get_width():
                raise NotFoundException("Không tìm thấy QR code trong ảnh")

        matrix_width = round((right - left + 1) / module_size)
        matrix_height = round((bottom - top + 1) / module_size)
        if matrix_width <= 0 or matrix_height <= 0:
            raise NotFoundException("Không tìm thấy QR code trong ảnh")
        if matrix_height != matrix_width:
            raise NotFoundException("QR code phải có hình vuông")

        # Nudge để tránh bị lệch
        nudge = int(module_size / 2.0)
        top += nudge
        left += nudge

        nudged_too_far_right = left + int((matrix_width - 1) * module_size) - right
        if nudged_too_far_right > 0:
            if nudged_too_far_right > nudge:
                raise NotFoundException("Không tìm thấy QR code trong ảnh")
            left -= nudged_too_far_right

        nudged_too_far_down = top + int((matrix_height - 1) * module_size) - bottom
        if nudged_too_far_down > 0:
            if nudged_too_far_down > nudge:
                raise NotFoundException("Không tìm thấy QR code trong ảnh")
            top -= nudged_too_far_down

        bits = BitMatrix(matrix_width, matrix_height)
        for y in range(matrix_height):
            i_offset = top + int(y * module_size)
            for x in range(matrix_width):
                if image.get(left + int(x * module_size), i_offset):
                    bits.set(x, y)
        return bits

    def module_size(self, left_top_black, image):
        """
        Tính toán kích thước module (kích thước của mỗi module trong QR code).

        Input:
        - left_top_black: tọa độ điểm đen ở góc trái trên của mã QR.
        - image: đối tượng BitMatrix chứa ảnh mã QR code.

        Hàm này sẽ tính toán và trả về kích thước của mỗi module trong mã QR.

        Output:
        - Trả về kích thước của module QR code dưới dạng số thực (float).
        """
        height = image.get_height()
        width = image.get_width()
        x = left_top_black[0]
        y = left_top_black[1]
        in_black = True
        transitions = 0
        while x < width and y < height:
            if in_black != image.get(x, y):
                if transitions == 5:
                    break
                transitions += 1
                in_black = not in_black
            x += 1
            y += 1
        if x == width or y == height:
            raise NotFoundException("Không tìm thấy QR code trong ảnh")
        return (x - left_top_black[0]) / 7.0
