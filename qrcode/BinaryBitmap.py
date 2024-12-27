import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from exceptions import NotFoundException
from .BitArray import BitArray
from .BitMatrix import BitMatrix
from common import Binarizer

class BinaryBitmap:
    """
    Lớp chính để biểu diễn dữ liệu bitmap 1 bit trong ZXing. 
    Các đối tượng Reader chấp nhận một BinaryBitmap và cố gắng giải mã nó.
    """

    def __init__(self, binarizer : Binarizer):
        """
        Khởi tạo một đối tượng BinaryBitmap.

        :param binarizer: Binarizer - Đối tượng chịu trách nhiệm chuyển đổi dữ liệu sang dạng nhị phân.
        :raises ValueError: Nếu binarizer là None.
        """
        if binarizer is None:
            raise ValueError("Binarizer phải không được rỗng.")
        self.binarizer = binarizer
        self.matrix = None

    def get_width(self) -> int:
        """
        Lấy chiều rộng của bitmap.

        :return: int - Chiều rộng của bitmap.
        """
        return self.binarizer.get_width()

    def get_height(self) -> int:
        """
        Lấy chiều cao của bitmap.

        :return: int - Chiều cao của bitmap.
        """
        return self.binarizer.get_height()

    def get_black_row(self, y: int, row: 'BitArray') -> 'BitArray':
        """
        Chuyển đổi một hàng dữ liệu sáng tối (luminance) sang dữ liệu 1 bit.

        :param y: int - Chỉ số hàng cần lấy, phải nằm trong khoảng [0, chiều cao của bitmap).
        :param row: BitArray - Một mảng được cấp phát trước (có thể là None hoặc quá nhỏ).
        :return: BitArray - Mảng bit cho hàng này (True đại diện cho màu đen).
        :raises NotFoundException: Nếu không thể chuyển đổi hàng thành dạng nhị phân.
        """
        return self.binarizer.get_black_row(y, row)

    def get_black_matrix(self) -> 'BitMatrix':
        """
        Chuyển đổi dữ liệu sáng tối 2D thành dữ liệu 1 bit.

        :return: BitMatrix - Ma trận bit 2D của hình ảnh (True đại diện cho màu đen).
        :raises NotFoundException: Nếu không thể chuyển đổi dữ liệu thành ma trận.
        """
        if self.matrix is None:
            self.matrix = self.binarizer.get_black_matrix()
        return self.matrix

    def is_crop_supported(self) -> bool:
        """
        Kiểm tra xem bitmap có hỗ trợ cắt hay không.

        :return: bool - True nếu hỗ trợ cắt, False nếu không.
        """
        return self.binarizer.get_luminance_source().is_crop_supported()

    def crop(self, left: int, top: int, width: int, height: int) -> 'BinaryBitmap':
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh đã được cắt.

        :param left: int - Tọa độ bên trái, phải nằm trong [0, chiều rộng của bitmap).
        :param top: int - Tọa độ phía trên, phải nằm trong [0, chiều cao của bitmap).
        :param width: int - Chiều rộng của vùng cần cắt.
        :param height: int - Chiều cao của vùng cần cắt.
        :return: BinaryBitmap - Phiên bản đã cắt của bitmap.
        """
        new_source = self.binarizer.get_luminance_source().crop(left, top, width, height)
        return BinaryBitmap(self.binarizer.create_binarizer(new_source))

    def is_rotate_supported(self) -> bool:
        """
        Kiểm tra xem bitmap có hỗ trợ xoay ngược chiều kim đồng hồ hay không.

        :return: bool - True nếu hỗ trợ xoay, False nếu không.
        """
        return self.binarizer.get_luminance_source().is_rotate_supported()

    def rotate_counter_clockwise(self) -> 'BinaryBitmap':
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh đã xoay 90 độ ngược chiều kim đồng hồ.

        :return: BinaryBitmap - Phiên bản đã xoay của bitmap.
        """
        new_source = self.binarizer.get_luminance_source().rotate_counter_clockwise()
        return BinaryBitmap(self.binarizer.create_binarizer(new_source))

    def rotate_counter_clockwise_45(self) -> 'BinaryBitmap':
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh đã xoay 45 độ ngược chiều kim đồng hồ.

        :return: BinaryBitmap - Phiên bản đã xoay của bitmap.
        """
        new_source = self.binarizer.get_luminance_source().rotate_counter_clockwise_45()
        return BinaryBitmap(self.binarizer.create_binarizer(new_source))

    def __str__(self) -> str:
        """
        Trả về chuỗi biểu diễn của bitmap.

        :return: str - Chuỗi biểu diễn của bitmap.
        """
        try:
            return str(self.get_black_matrix())
        except NotFoundException:
            return ""
