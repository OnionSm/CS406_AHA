import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from exceptions import NotFoundException
from .PerspectiveTransform import PerspectiveTransform

class DefaultGridSampler:
    """
    Lớp DefaultGridSampler thực hiện việc lấy mẫu lưới điểm từ hình ảnh, hỗ trợ biến dạng phối cảnh.
    """
    def __init__(self):
        pass

    @staticmethod
    def sample_grid(image, dimension_x, dimension_y, *args):
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

        print("ARG",len(args))
        print(*args)
        # Kiểm tra số lượng đối số để xác định xem là dùng 4 điểm hay PerspectiveTransform
        if len(args) == 16:  # Nếu có 8 đối số, tức là 4 điểm với tọa độ chuyển tiếp và từ
            return DefaultGridSampler.sample_grid_from_coordinates(image, dimension_x, dimension_y, *args)
        elif len(args) == 1 and isinstance(args[0], PerspectiveTransform):  # Nếu có một đối số là PerspectiveTransform
            return DefaultGridSampler.sample_grid_with_transform(image, dimension_x, dimension_y, args[0])
        else:
            raise NotFoundException()

    @staticmethod
    def sample_grid_from_coordinates(image, dimension_x, dimension_y, p1_to_x, p1_to_y, p2_to_x, p2_to_y,
                                     p3_to_x, p3_to_y, p4_to_x, p4_to_y, p1_from_x, p1_from_y, p2_from_x, p2_from_y,
                                     p3_from_x, p3_from_y, p4_from_x, p4_from_y):

        transform = PerspectiveTransform.quadrilateral_to_quadrilateral(
            p1_to_x, p1_to_y, p2_to_x, p2_to_y, p3_to_x, p3_to_y, p4_to_x, p4_to_y,
            p1_from_x, p1_from_y, p2_from_x, p2_from_y, p3_from_x, p3_from_y, p4_from_x, p4_from_y
        )
        return DefaultGridSampler.sample_grid_with_transform(image, dimension_x, dimension_y, transform)

    @staticmethod
    def sample_grid_with_transform(image, dimension_x, dimension_y, transform):
        from qrcode.BitMatrix import BitMatrix
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
        print("Dimension", dimension_x, dimension_y)
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
            DefaultGridSampler.check_and_nudge_points(image, points)

            try:
                for x in range(0, max_points, 2):
                    if image.get(int(points[x]), int(points[x + 1])):
                        # Nếu điểm là pixel màu đen (hoặc gần đen)
                        bits.set(x // 2, y)
            except IndexError:
                # Nếu có lỗi chỉ số ngoài phạm vi, ném ra NotFoundException
                raise NotFoundException()

        return bits

    @staticmethod
    def check_and_nudge_points(image, points):
        """
        Input:
        - image: BitMatrix
        - points: float []
        """
        width = image.get_width()
        height = image.get_height()

        # Check and nudge points from start until we see some that are OK:
        nudged = True
        max_offset = len(points) - 1  # points length must be even
        offset = 0
        print("POINT", points)
        while offset < max_offset and nudged:
            x = int(points[offset])
            y = int(points[offset + 1])
            print(x,y)
            if x < -1 or x > width or y < -1 or y > height:
                raise Exception("NotFoundException")

            nudged = False
            if x == -1:
                points[offset] = 0.0
                nudged = True
            elif x == width:
                points[offset] = width - 1
                nudged = True

            if y == -1:
                points[offset + 1] = 0.0
                nudged = True
            elif y == height:
                points[offset + 1] = height - 1
                nudged = True

            offset += 2

        # Check and nudge points from end:
        nudged = True
        offset = len(points) - 2

        while offset >= 0 and nudged:
            x = int(points[offset])
            y = int(points[offset + 1])
            if x < -1 or x > width or y < -1 or y > height:
                raise Exception("NotFoundException")

            nudged = False
            if x == -1:
                points[offset] = 0.0
                nudged = True
            elif x == width:
                points[offset] = width - 1
                nudged = True

            if y == -1:
                points[offset + 1] = 0.0
                nudged = True
            elif y == height:
                points[offset + 1] = height - 1
                nudged = True

            offset -= 2