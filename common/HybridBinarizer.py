from . import LuminanceSource
from .GlobalHistogramBinarizer import GlobalHistogramBinarizer
from qrcode.BitMatrix import BitMatrix
import numpy as np
from typing import List


class HybridBinarizer(GlobalHistogramBinarizer):
    """
    Class này thực hiện thuật toán ngưỡng cục bộ, mặc dù chậm hơn so với GlobalHistogramBinarizer,
    nhưng khá hiệu quả cho mục đích của nó. Nó được thiết kế cho các hình ảnh có tần số cao 
    của mã vạch với dữ liệu đen trên nền trắng. Đối với ứng dụng này, nó làm việc tốt hơn so với 
    một điểm đen toàn cục trong các trường hợp có bóng và gradient mạnh. Tuy nhiên, nó có thể tạo ra 
    các hiện tượng lạ trong các hình ảnh có tần số thấp và do đó không phải là lựa chọn tốt cho các 
    mục đích chung ngoài ZXing.
    
    Class này kế thừa từ GlobalHistogramBinarizer, sử dụng phương pháp histogram cũ cho các bộ 
    giải mã 1D và phương pháp cục bộ mới cho các bộ giải mã 2D. Việc giải mã 1D sử dụng histogram 
    theo từng dòng đã có tính chất cục bộ và chỉ gặp vấn đề với các gradient ngang.
    
    Đây là Binarizer mặc định cho các bài kiểm tra đơn vị và là class được khuyến nghị cho người dùng thư viện.
    """

    # Class này sử dụng các block 5x5 để tính toán độ sáng cục bộ, mỗi block có kích thước 8x8 pixel.
    BLOCK_SIZE_POWER = 3
    BLOCK_SIZE = 1 << BLOCK_SIZE_POWER  # ...0100...00
    BLOCK_SIZE_MASK = BLOCK_SIZE - 1   # ...0011...11
    MINIMUM_DIMENSION = BLOCK_SIZE * 5
    MIN_DYNAMIC_RANGE = 24

    def __init__(self, source):
        """
        Khởi tạo HybridBinarizer với nguồn luminance.
        """
        super().__init__(source)
        self.matrix = None

    def get_black_matrix(self):
        """
        Tính toán BitMatrix cuối cùng chỉ một lần cho tất cả các yêu cầu. Việc này có thể được gọi 
        trong constructor, nhưng có một số ưu điểm khi thực hiện theo cách lazy, ví dụ như giúp dễ dàng 
        trong việc profiling và không thực hiện các tác vụ nặng khi người gọi không mong đợi.

        Nếu kích thước của hình ảnh nhỏ hơn MINIMUM_DIMENSION, nó sẽ sử dụng phương pháp histogram toàn cục.
        """
        if self.matrix is not None:
            return self.matrix

        source : LuminanceSource = self.get_luminance_source()
        width: int = source.get_width()
        height: int  = source.get_height()
        if width >= self.MINIMUM_DIMENSION and height >= self.MINIMUM_DIMENSION:
            luminances: List = source.get_matrix()
            sub_width: int = width >> HybridBinarizer.BLOCK_SIZE_POWER
            if (width & HybridBinarizer.BLOCK_SIZE_MASK) != 0:
                sub_width += 1
            sub_height: int = height >> HybridBinarizer.BLOCK_SIZE_POWER
            if (height & HybridBinarizer.BLOCK_SIZE_MASK) != 0:
                sub_height += 1

            black_points: np.array = self.calculate_black_points(luminances, sub_width, sub_height, width, height)
            new_matrix: BitMatrix = BitMatrix(width, height)
            self.calculate_threshold_for_block(luminances, sub_width, sub_height, width, height, black_points, new_matrix)
            self.matrix = new_matrix
        else:
            # Nếu hình ảnh quá nhỏ, rơi về phương pháp histogram toàn cục.
            self.matrix = super().get_black_matrix()

        return self.matrix

    def create_binarizer(self, source):
        """
        Tạo một binarizer mới từ nguồn luminance.
        """
        return HybridBinarizer(source)

    @staticmethod
    def calculate_threshold_for_block(luminances, sub_width, sub_height, width, height, black_points, matrix):
        """
        Tính toán ngưỡng cho mỗi block trong hình ảnh. Với mỗi block, nó tính toán điểm đen trung bình 
        dựa trên một lưới 5x5 các block xung quanh nó.
        """
        max_y_offset = height - HybridBinarizer.BLOCK_SIZE
        max_x_offset = width - HybridBinarizer.BLOCK_SIZE
        for y in range(sub_height):
            y_offset: int  = y << HybridBinarizer.BLOCK_SIZE_POWER
            if y_offset > max_y_offset:
                y_offset = max_y_offset

            top: int = HybridBinarizer.cap(y, sub_height - 3)
            for x in range(sub_width):
                x_offset: int  = x << HybridBinarizer.BLOCK_SIZE_POWER
                if x_offset > max_x_offset:
                    x_offset = max_x_offset

                left: int = HybridBinarizer.cap(x, sub_width - 3)
                sum_black_points = 0
                for z in range(-2, 3):
                    black_row = np.array(black_points[top + z], dtype=np.int64)  # Chuyển đổi kiểu dữ liệu
                    sum_black_points += black_row[left - 2:left + 3].sum()  # Tính tổng

                average = sum_black_points // 25
                HybridBinarizer.threshold_block(luminances, x_offset, y_offset, average, width, matrix)

    @staticmethod
    def cap(value, max_value):
        """
        Giới hạn giá trị sao cho không nhỏ hơn 2 và không lớn hơn max_value.
        """
        return max(2, min(value, max_value))

    @staticmethod
    def threshold_block(luminances: List, x_offset: int, y_offset: int, threshold: int, stride:int, matrix: BitMatrix):
        """
        Áp dụng ngưỡng cho một block các pixel.
        """
        for y in range(HybridBinarizer.BLOCK_SIZE):
            offset = y_offset * stride + x_offset + y * stride
            for x in range(HybridBinarizer.BLOCK_SIZE):
                # Comparison needs to be <= so that black == 0 pixels are black even if the threshold is 0.
                if (luminances[offset + x] & 0xFF) <= threshold:
                    matrix.set(x_offset + x, y_offset + y)

    @staticmethod
    def calculate_black_points(luminances, sub_width, sub_height, width, height):
        """
        Tính toán điểm đen cho mỗi block pixel và lưu lại kết quả.

        Parameters:
        - luminances: mảng 1D chứa độ sáng của các pixel (byte).
        - sub_width: số lượng block theo chiều ngang.
        - sub_height: số lượng block theo chiều dọc.
        - width: chiều rộng của ảnh (tính theo pixel).
        - height: chiều cao của ảnh (tính theo pixel).

        Returns:
        - black_points: danh sách 2D lưu giá trị trung bình của các block pixel.
        """
        max_y_offset = height - HybridBinarizer.BLOCK_SIZE
        max_x_offset = width - HybridBinarizer.BLOCK_SIZE
        black_points = np.zeros((sub_height, sub_width), dtype=np.int64)
        for y in range(sub_height):
            y_offset: int = y << HybridBinarizer.BLOCK_SIZE_POWER
            if y_offset > max_y_offset:
                y_offset = max_y_offset

            for x in range(sub_width):
                x_offset: int = x << HybridBinarizer.BLOCK_SIZE_POWER
                if x_offset > max_x_offset:
                    x_offset = max_x_offset

                total_sum = 0
                min_pixel = 0xFF
                max_pixel = 0

                yy = 0
                offset = y_offset * width + x_offset

                while yy < HybridBinarizer.BLOCK_SIZE:
                    xx = 0
                    while xx < HybridBinarizer.BLOCK_SIZE:
                        pixel : int  = luminances[offset + xx] & 0xFF
                        total_sum += pixel

                        # still looking for good contrast
                        if pixel < min_pixel:
                            min_pixel = pixel
                        if pixel > max_pixel:
                            max_pixel = pixel

                        xx += 1

                    # short-circuit min/max tests once dynamic range is met
                    if max_pixel - min_pixel >HybridBinarizer.MIN_DYNAMIC_RANGE:
                        yy += 1
                        offset += width
                        while yy < HybridBinarizer.BLOCK_SIZE:
                            xx2 = 0
                            while xx2 < HybridBinarizer.BLOCK_SIZE:
                                total_sum += luminances[offset + xx2] & 0xFF
                                xx2 += 1
                            yy += 1
                            offset += width
                        break  # Thoát khỏi vòng lặp ngoài nếu dynamic range đủ lớn

                    yy += 1
                    offset += width

                # Tính trung bình giá trị pixel trong block
                average: int  = total_sum >> (HybridBinarizer.BLOCK_SIZE_POWER * 2)

                if max_pixel - min_pixel <= HybridBinarizer.MIN_DYNAMIC_RANGE:
                    average = min_pixel // 2

                    if y > 0 and x > 0:
                        average_neighbor_black_point: int = (
                            black_points[y - 1][x]
                            + (2 * black_points[y][x - 1])
                            + black_points[y - 1][x - 1]
                        ) // 4
                        if min_pixel < average_neighbor_black_point:
                            average = average_neighbor_black_point

                black_points[y][x] = average
        return black_points