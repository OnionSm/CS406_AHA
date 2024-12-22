import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .GridSampler import GridSampler
from .PerspectiveTransform import PerspectiveTransform
from qrcode import BitMatrix

class DefaultGridSampler(GridSampler):
    def sample_grid(self, image, dimension_x, dimension_y,
                    p1_to_x, p1_to_y, p2_to_x, p2_to_y,
                    p3_to_x, p3_to_y, p4_to_x, p4_to_y,
                    p1_from_x, p1_from_y, p2_from_x, p2_from_y,
                    p3_from_x, p3_from_y, p4_from_x, p4_from_y):
        """
        Lấy mẫu từ một hình ảnh để tạo ra ma trận bit chữ nhật có kích thước được chỉ định. Phép 
        biến đổi để lấy mẫu được xác định bởi tọa độ của 4 điểm trong không gian ảnh gốc và không 
        gian ảnh đã biến đổi.

        Các tham số:
            image (BitMatrix): Hình ảnh cần lấy mẫu.
            dimension_x (int): Chiều rộng của ma trận BitMatrix cần lấy từ hình ảnh.
            dimension_y (int): Chiều cao của ma trận BitMatrix cần lấy từ hình ảnh.
            p1_to_x (float): Tọa độ X của điểm 1 trong không gian đích.
            p1_to_y (float): Tọa độ Y của điểm 1 trong không gian đích.
            p2_to_x (float): Tọa độ X của điểm 2 trong không gian đích.
            p2_to_y (float): Tọa độ Y của điểm 2 trong không gian đích.
            p3_to_x (float): Tọa độ X của điểm 3 trong không gian đích.
            p3_to_y (float): Tọa độ Y của điểm 3 trong không gian đích.
            p4_to_x (float): Tọa độ X của điểm 4 trong không gian đích.
            p4_to_y (float): Tọa độ Y của điểm 4 trong không gian đích.
            p1_from_x (float): Tọa độ X của điểm 1 trong không gian gốc.
            p1_from_y (float): Tọa độ Y của điểm 1 trong không gian gốc.
            p2_from_x (float): Tọa độ X của điểm 2 trong không gian gốc.
            p2_from_y (float): Tọa độ Y của điểm 2 trong không gian gốc.
            p3_from_x (float): Tọa độ X của điểm 3 trong không gian gốc.
            p3_from_y (float): Tọa độ Y của điểm 3 trong không gian gốc.
            p4_from_x (float): Tọa độ X của điểm 4 trong không gian gốc.
            p4_from_y (float): Tọa độ Y của điểm 4 trong không gian gốc.

        Kết quả trả về:
            BitMatrix: Ma trận bit đại diện cho một lưới điểm được lấy mẫu từ hình ảnh trong 
                       vùng được xác định bởi các tham số "from".

        Ngoại lệ:
            Exception: Nếu không thể lấy mẫu từ hình ảnh (ví dụ: phép biến đổi được xác định bởi 
                       các điểm đầu vào không hợp lệ hoặc dẫn đến việc lấy mẫu ngoài giới hạn của hình ảnh).
        """
        transform = PerspectiveTransform.quadrilateral_to_quadrilateral(
            p1_to_x, p1_to_y, p2_to_x, p2_to_y, p3_to_x, p3_to_y, p4_to_x, p4_to_y,
            p1_from_x, p1_from_y, p2_from_x, p2_from_y, p3_from_x, p3_from_y, p4_from_x, p4_from_y
        )
        return self.sample_grid_with_transform(image, dimension_x, dimension_y, transform)

    def sample_grid_with_transform(self, image, dimension_x, dimension_y, transform):
        """
        Input: 
        - image: BitMatrix
        - dimension_x: int
        - dimension_y: int 
        - transform: PerpectiveTransform
        """
        if dimension_x <= 0 or dimension_y <= 0:
            raise Exception("NotFoundException")

        bits = BitMatrix(dimension_x, dimension_y)
        points = [0] * (2 * dimension_x)

        for y in range(dimension_y):
            max_offset = len(points)
            i_value = y + 0.5
            for x in range(0, max_offset, 2):
                points[x] = (x // 2) + 0.5
                points[x + 1] = i_value
            
            # Transform points
            transform.transform_points(points)

            # Kiểm tra và hiệu chỉnh các điểm
            super.check_and_nudge_points(image, points)

            try:
                for x in range(0, max_offset, 2):
                    if image.get(int(points[x]), int(points[x + 1])):
                        bits.set(x // 2, y)  # Đặt pixel trong BitMatrix
            except IndexError:
                # Nếu phép biến đổi làm các điểm nằm ngoài biên ảnh
                raise Exception("NotFoundException")

        return bits