import cv2
import numpy as np
from .LuminanceSource import LuminanceSource

class CV2ImageLuminanceSource(LuminanceSource):
    """
    Lớp này thực hiện nguồn ánh sáng từ một ảnh grayscale trong OpenCV.
    Có thể cắt và xoay ảnh theo yêu cầu.
    """

    def __init__(self, image, left=0, top=0, width=None, height=None):
        """
        Khởi tạo đối tượng BufferedImageLuminanceSource.
        
        :param image: Ảnh gốc dưới dạng mảng numpy (OpenCV)
        :param left: Vị trí bắt đầu trên trục X để cắt ảnh (mặc định là 0)
        :param top: Vị trí bắt đầu trên trục Y để cắt ảnh (mặc định là 0)
        :param width: Chiều rộng của vùng cắt (mặc định là chiều rộng của ảnh)
        :param height: Chiều cao của vùng cắt (mặc định là chiều cao của ảnh)
        """
        if len(image.shape) == 3 and image.shape[2] == 3:  # Nếu ảnh là RGB
            # Chuyển ảnh sang grayscale
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            self.image = image

        self.left = left
        self.top = top
        self.width = width if width else image.shape[1]
        self.height = height if height else image.shape[0]

        # Cắt ảnh nếu cần
        self.cropped_image = self.image[self.top:self.top+self.height, self.left:self.left+self.width]

    def get_row(self, y, row=None):
        """
        Lấy một hàng pixel từ ảnh.

        :param y: Vị trí hàng cần lấy
        :param row: Mảng để chứa dữ liệu hàng, nếu không có thì sẽ tạo mảng mới
        :return: Mảng chứa dữ liệu hàng
        """
        if y < 0 or y >= self.height:
            raise ValueError(f"Requested row is outside the image: {y}")
        
        if row is None or len(row) < self.width:
            row = np.zeros(self.width, dtype=np.uint8)
        
        row[:] = self.cropped_image[y, :]
        return row

    def get_matrix(self):
        """
        Lấy toàn bộ dữ liệu ảnh dưới dạng mảng 1 chiều.

        :return: Mảng chứa toàn bộ dữ liệu pixel của ảnh
        """
        return self.cropped_image.flatten()

    def is_crop_supported(self):
        """
        Kiểm tra xem việc cắt ảnh có được hỗ trợ hay không.

        :return: Trả về True nếu cắt ảnh được hỗ trợ
        """
        return True

    def crop(self, left, top, width, height):
        """
        Cắt ảnh từ một vị trí và kích thước cho trước.

        :param left: Vị trí bắt đầu trên trục X
        :param top: Vị trí bắt đầu trên trục Y
        :param width: Chiều rộng của vùng cắt
        :param height: Chiều cao của vùng cắt
        :return: Trả về đối tượng BufferedImageLuminanceSource với ảnh đã cắt
        """
        return CV2ImageLuminanceSource(self.image, self.left + left, self.top + top, width, height)

    def is_rotate_supported(self):
        """
        Kiểm tra xem việc xoay ảnh có được hỗ trợ hay không.

        :return: Trả về True vì lớp này hỗ trợ xoay ảnh
        """
        return True

    def rotate_counter_clockwise(self):
        """
        Xoay ảnh 90 độ ngược chiều kim đồng hồ.

        :return: Trả về đối tượng BufferedImageLuminanceSource với ảnh đã xoay
        """
        rotated_image = cv2.transpose(self.cropped_image)
        rotated_image = cv2.flip(rotated_image, flipCode=0)
        return CV2ImageLuminanceSource(rotated_image)

    def rotate_counter_clockwise_45(self):
        """
        Xoay ảnh 45 độ ngược chiều kim đồng hồ.

        :return: Trả về đối tượng BufferedImageLuminanceSource với ảnh đã xoay
        """
        (h, w) = self.cropped_image.shape
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -45, 1)
        rotated_image = cv2.warpAffine(self.cropped_image, rotation_matrix, (w, h))
        return CV2ImageLuminanceSource(rotated_image)