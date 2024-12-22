import numpy as np
import cv2
from scipy.ndimage import rotate
import math
from .LuminanceSource import LuminanceSource

class CV2ImageLuminanceSource(LuminanceSource):
    """
    Lớp BufferedImageLuminanceSource này triển khai một nguồn ánh sáng cho hình ảnh dạng grayscale (mức xám),
    sử dụng thư viện PIL để xử lý hình ảnh.
    """

    MINUS_45_IN_RADIANS = -0.7853981633974483  # Math.toRadians(-45.0)

    def __init__(self, image, left=0, top=0, width=None, height=None):
        """
        Khởi tạo lớp với hình ảnh đầu vào.
        
        Nếu hình ảnh không phải là hình ảnh grayscale, nó sẽ được chuyển đổi thành grayscale.
        Nếu có tọa độ crop (cắt hình), hình ảnh sẽ được cắt theo các tham số tương ứng.
        
        :param image: Hình ảnh đầu vào (PIL Image object).
        :param left: Tọa độ trái của vùng cần cắt.
        :param top: Tọa độ trên của vùng cần cắt.
        :param width: Chiều rộng của vùng cần cắt.
        :param height: Chiều cao của vùng cần cắt.
        """
        self.left = left
        self.top = top
        
        # Giả sử image là một numpy array
        if len(image.shape) == 3:  # Nếu hình ảnh có 3 kênh màu (RGB)
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            self._image = image  # Hình ảnh đã là grayscale
                
        # Nếu có thông số crop, cắt hình ảnh theo yêu cầu
        if width is not None and height is not None:
            self.image = self.image.crop((left, top, left + width, top + height))
        
        self.width, self.height = self.image.shape[1], self.image.shape[0]

    def get_row(self, y, row=None):
        """
        Lấy một hàng pixel từ hình ảnh.
        
        :param y: Chỉ số hàng cần lấy.
        :param row: Dữ liệu hàng nếu đã có, nếu không thì sẽ được khởi tạo mới.
        :return: Mảng byte chứa dữ liệu hàng.
        """
        if y < 0 or y >= self.height:
            raise ValueError(f"Requested row is outside the image: {y}")
        
        if row is None or len(row) < self.width:
            row = bytearray(self.width)

        # Lấy dữ liệu pixel từ hình ảnh
        row[:] = np.array(self.image.getdata(self.width * y, self.width), dtype=np.uint8)
        
        return row

    def get_matrix(self):
        """
        Lấy toàn bộ ma trận luminance của hình ảnh.
        
        :return: Mảng byte chứa toàn bộ dữ liệu pixel (luminance) của hình ảnh.
        """
        matrix = np.array(self.image, dtype=np.uint8)
        return matrix.flatten()

    def is_crop_supported(self):
        """
        Kiểm tra xem hình ảnh có hỗ trợ cắt không.
        
        :return: Trả về True nếu hỗ trợ cắt, ngược lại False.
        """
        return True

    def crop(self, left, top, width, height):
        """
        Cắt hình ảnh theo vùng đã cho.
        
        :param left: Tọa độ trái của vùng cắt.
        :param top: Tọa độ trên của vùng cắt.
        :param width: Chiều rộng của vùng cắt.
        :param height: Chiều cao của vùng cắt.
        :return: Một đối tượng `BufferedImageLuminanceSource` mới đã cắt.
        """
        return CV2ImageLuminanceSource(self.image, self.left + left, self.top + top, width, height)

    def is_rotate_supported(self):
        """
        Kiểm tra xem hình ảnh có hỗ trợ xoay không.
        
        :return: Trả về True vì hình ảnh hỗ trợ xoay.
        """
        return True

    def rotate_counter_clockwise(self):
        """
        Xoay hình ảnh 90 độ ngược chiều kim đồng hồ.
        
        :return: Một đối tượng `BufferedImageLuminanceSource` mới đã xoay.
        """
        rotated_image = self.image.rotate(90, expand=True)
        return CV2ImageLuminanceSource(rotated_image, self.top, self.image.width - (self.left + self.width), self.height, self.width)

    def rotate_counter_clockwise_45(self):
        """
        Xoay hình ảnh 45 độ ngược chiều kim đồng hồ.
        
        :return: Một đối tượng `BufferedImageLuminanceSource` mới đã xoay 45 độ.
        """
        old_center_x = self.left + self.width // 2
        old_center_y = self.top + self.height // 2

        # Tạo ma trận xoay 45 độ
        rotated_image = rotate(np.array(self.image), self.MINUS_45_IN_RADIANS, reshape=True)
        
        # Tính toán kích thước mới sau khi xoay và vị trí crop
        new_left = max(0, old_center_x - rotated_image.shape[1] // 2)
        new_top = max(0, old_center_y - rotated_image.shape[0] // 2)
        new_right = min(rotated_image.shape[1] - 1, old_center_x + rotated_image.shape[1] // 2)
        new_bottom = min(rotated_image.shape[0] - 1, old_center_y + rotated_image.shape[0] // 2)

        return CV2ImageLuminanceSource(rotated_image, new_left, new_top, new_right - new_left, new_bottom - new_top)
