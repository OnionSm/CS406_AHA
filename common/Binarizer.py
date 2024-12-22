from abc import ABC, abstractmethod
import numpy as np
from .LuminanceSource import LuminanceSource
from qrcode import BitMatrix, BitArray

class Binarizer(ABC):
    """ 
    Lớp trừu tượng này cung cấp một tập hợp các phương thức để chuyển đổi dữ liệu độ sáng (luminance) thành dữ liệu 1-bit. 
    Lớp này cho phép thuật toán biến thể, ví dụ, cho phép một kỹ thuật thresholding tốn kém cho các máy chủ và một kỹ thuật nhanh cho di động.
    """

    def __init__(self, source: LuminanceSource):
        """ 
        Khởi tạo Binarizer với nguồn sáng.
        
        :param source: Đối tượng LuminanceSource đại diện cho nguồn dữ liệu độ sáng.
        """
        self.source = source
    
    def get_luminance_source(self):
        """ 
        Trả về đối tượng LuminanceSource mà Binarizer đang sử dụng.
        """
        return self.source
    
    @abstractmethod
    def get_black_row(self, y, row):
        """ 
        Chuyển đổi một dòng dữ liệu độ sáng thành dữ liệu 1-bit.
        
        :param y: Dòng cần lấy, phải nằm trong phạm vi chiều cao của ảnh.
        :param row: Một mảng BitArray có thể được sử dụng để lưu trữ kết quả.
        :return: Mảng BitArray với dữ liệu 1-bit cho dòng này.
        :raises NotFoundException: Nếu không thể chuyển đổi dòng này.
        """
        pass
    
    @abstractmethod
    def get_black_matrix(self):
        """ 
        Chuyển đổi toàn bộ dữ liệu độ sáng thành ma trận 1-bit.
        
        :return: Ma trận BitMatrix đại diện cho toàn bộ ảnh dưới dạng 1-bit.
        :raises NotFoundException: Nếu không thể chuyển đổi ảnh thành ma trận 1-bit.
        """
        pass
    
    @abstractmethod
    def create_binarizer(self, source: LuminanceSource):
        """ 
        Tạo một đối tượng Binarizer mới với nguồn sáng giống hệt.
        
        :param source: LuminanceSource sẽ được Binarizer sử dụng.
        :return: Một đối tượng Binarizer mới.
        """
        pass
    
    def get_width(self):
        """ 
        Trả về chiều rộng của ảnh từ nguồn sáng.
        """
        return self.source.get_width()
    
    def get_height(self):
        """ 
        Trả về chiều cao của ảnh từ nguồn sáng.
        """
        return self.source.get_height()
