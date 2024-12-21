import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from exceptions import NotFoundException

class GridSampler:
    """Lớp GridSampler xử lý việc lấy mẫu từ hình ảnh để tái tạo mã QR, hỗ trợ xử lý biến dạng phối cảnh."""
    
    # Biến toàn cục lưu trữ đối tượng GridSampler
    _grid_sampler = None

    @staticmethod
    def set_grid_sampler(new_grid_sampler):
        """
        Đặt một đối tượng GridSampler cụ thể để sử dụng.
        
        Parameters:
            new_grid_sampler (GridSampler): Đối tượng GridSampler mới.
        """
        GridSampler._grid_sampler = new_grid_sampler

    @staticmethod
    def get_instance(): 
        """
        Lấy đối tượng GridSampler hiện tại.
        
        Returns:
            GridSampler: Đối tượng GridSampler đang được sử dụng.
        """
        return GridSampler._grid_sampler

    def sample_grid(self, image, dimension_x, dimension_y, *args):
        """
        Trích xuất lưới điểm từ hình ảnh với kích thước xác định, hỗ trợ biến dạng phối cảnh.
        
        Parameters:
            image (BitMatrix): Hình ảnh nguồn.
            dimension_x (int): Chiều rộng của lưới.
            dimension_y (int): Chiều cao của lưới.
            *args: Tọa độ của 4 điểm hoặc một đối tượng PerspectiveTransform.
        
        Returns:
            BitMatrix: Lưới các điểm được lấy mẫu.
        """
        raise NotImplementedError("Phương thức này cần được triển khai trong lớp con.")

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

        while offset < max_offset and nudged:
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