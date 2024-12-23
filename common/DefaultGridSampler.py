import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .GridSampler import GridSampler
from .PerspectiveTransform import PerspectiveTransform
from qrcode.BitMatrix import BitMatrix
from exceptions import NotFoundException

class DefaultGridSampler(GridSampler):
    """
    Lớp DefaultGridSampler thực hiện việc lấy mẫu lưới điểm từ hình ảnh, hỗ trợ biến dạng phối cảnh.
    """
    def sample_grid(self, image, dimension_x, dimension_y, *args):
        """
        Lấy mẫu lưới điểm từ hình ảnh, sử dụng các đối số truyền vào để áp dụng biến dạng phối cảnh hoặc điểm.

        Parameters:
            image (BitMatrix): Hình ảnh nguồn.
            dimension_x (int): Số lượng điểm theo chiều rộng của lưới.
            dimension_y (int): Số lượng điểm theo chiều cao của lưới.
            *args: Tọa độ của 4 điểm hoặc một đối tượng PerspectiveTransform.

        Returns:
            BitMatrix: Lưới điểm sau khi đã được biến dạng.

        Throws:
            NotFoundException: Nếu không tìm thấy lưới điểm hợp lệ.
        """
        # Kiểm tra số lượng đối số để xác định xem là dùng 4 điểm hay PerspectiveTransform
        if len(args) == 16:  # Nếu có 8 đối số, tức là 4 điểm với tọa độ chuyển tiếp và từ
            return self.sample_grid_from_coordinates(image, dimension_x, dimension_y, *args)
        elif len(args) == 1 and isinstance(args[0], PerspectiveTransform):  # Nếu có một đối số là PerspectiveTransform
            return self.sample_grid_with_transform(image, dimension_x, dimension_y, args[0])
        else:
            raise NotFoundException()

    def sample_grid_from_coordinates(self, image, dimension_x, dimension_y, p1_to_x, p1_to_y, p2_to_x, p2_to_y,
                                     p3_to_x, p3_to_y, p4_to_x, p4_to_y, p1_from_x, p1_from_y, p2_from_x, p2_from_y,
                                     p3_from_x, p3_from_y, p4_from_x, p4_from_y):

        transform = PerspectiveTransform.quadrilateral_to_quadrilateral(
            p1_to_x, p1_to_y, p2_to_x, p2_to_y, p3_to_x, p3_to_y, p4_to_x, p4_to_y,
            p1_from_x, p1_from_y, p2_from_x, p2_from_y, p3_from_x, p3_from_y, p4_from_x, p4_from_y
        )
        return self.sample_grid_with_transform(image, dimension_x, dimension_y, transform)

    def sample_grid_with_transform(self, image, dimension_x, dimension_y, transform):
        """
        Lấy mẫu lưới điểm từ hình ảnh, sử dụng biến dạng phối cảnh đã cho.

        Parameters:
            image (BitMatrix): Hình ảnh nguồn.
            dimension_x (int): Số lượng điểm theo chiều rộng của lưới.
            dimension_y (int): Số lượng điểm theo chiều cao của lưới.
            transform (PerspectiveTransform): Biến dạng phối cảnh cần áp dụng.
        
        Returns:
            BitMatrix: Lưới điểm sau khi đã được biến dạng.
        
        Throws:
            NotFoundException: Nếu không tìm thấy lưới điểm hợp lệ.
        """
        if dimension_x <= 0 or dimension_y <= 0:
            raise NotFoundException()

        # Tạo một đối tượng BitMatrix mới để lưu trữ lưới điểm
        bits = BitMatrix(dimension_x, dimension_y)
        points = [0] * (2 * dimension_x)

        for y in range(dimension_y):
            max_points = len(points)
            i_value = y + 0.5
            for x in range(0, max_points, 2):
                points[x] = (x / 2) + 0.5
                points[x + 1] = i_value
            # Áp dụng biến dạng cho các điểm
            transform.transform_points(points)
            
            # Kiểm tra và điều chỉnh nếu các điểm nằm ngoài ảnh
            self.check_and_nudge_points(image, points)

            try:
                for x in range(0, max_points, 2):
                    if image.get(int(points[x]), int(points[x + 1])):
                        # Nếu điểm là pixel màu đen (hoặc gần đen)
                        bits.set(x // 2, y)
            except IndexError:
                # Nếu có lỗi chỉ số ngoài phạm vi, ném ra NotFoundException
                raise NotFoundException()

        return bits