
from .GlobalHistogramBinarizer import GlobalHistogramBinarizer
from qrcode import BitMatrix
import numpy as np

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

        source = self.get_luminance_source()
        width = source.get_width()
        height = source.get_height()

        if width >= self.MINIMUM_DIMENSION and height >= self.MINIMUM_DIMENSION:
            luminances = source.get_matrix()
            sub_width = width >> self.BLOCK_SIZE_POWER
            if (width & self.BLOCK_SIZE_MASK) != 0:
                sub_width += 1
            sub_height = height >> self.BLOCK_SIZE_POWER
            if (height & self.BLOCK_SIZE_MASK) != 0:
                sub_height += 1

            black_points = self.calculate_black_points(luminances, sub_width, sub_height, width, height)

            new_matrix = BitMatrix(width, height)
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

    def calculate_threshold_for_block(self, luminances, sub_width, sub_height, width, height, black_points, matrix):
        """
        Tính toán ngưỡng cho mỗi block trong hình ảnh. Với mỗi block, nó tính toán điểm đen trung bình 
        dựa trên một lưới 5x5 các block xung quanh nó.
        """
        max_y_offset = height - self.BLOCK_SIZE
        max_x_offset = width - self.BLOCK_SIZE
        for y in range(sub_height):
            y_offset = y << self.BLOCK_SIZE_POWER
            if y_offset > max_y_offset:
                y_offset = max_y_offset
            top = self.cap(y, sub_height - 3)

            for x in range(sub_width):
                x_offset = x << self.BLOCK_SIZE_POWER
                if x_offset > max_x_offset:
                    x_offset = max_x_offset
                left = self.cap(x, sub_width - 3)

                sum_black_points = 0
                for z in range(-2, 3):
                    black_row = np.array(black_points[top + z], dtype=np.int32)  # Chuyển đổi kiểu dữ liệu
                    sum_black_points += black_row[left - 2:left + 3].sum()  # Tính tổng

                average = sum_black_points // 25
                self.threshold_block(luminances, x_offset, y_offset, average, width, matrix)

    def cap(self, value, max_value):
        """
        Giới hạn giá trị sao cho không nhỏ hơn 2 và không lớn hơn max_value.
        """
        return max(2, min(value, max_value))

    def threshold_block(self, luminances, x_offset, y_offset, threshold, stride, matrix):
        """
        Áp dụng ngưỡng cho một block các pixel.
        """
        for y in range(self.BLOCK_SIZE):
            offset = y_offset * stride + x_offset
            for x in range(self.BLOCK_SIZE):
                # Trực tiếp so sánh giá trị của pixel mà không cần sử dụng phép toán bit.
                if luminances[offset + x] >= threshold:
                    matrix.set(x_offset + x, y_offset + y)

    def calculate_black_points(self, luminances, sub_width, sub_height, width, height):
        """
        Tính toán điểm đen cho mỗi block pixel và lưu lại kết quả.

        Parameters:
        - luminances: danh sách hoặc mảng 1D chứa độ sáng của các pixel.
        - sub_width: số lượng block theo chiều ngang.
        - sub_height: số lượng block theo chiều dọc.
        - width: chiều rộng của ảnh (tính theo pixel).
        - height: chiều cao của ảnh (tính theo pixel).

        Returns:
        - black_points: danh sách 2D lưu giá trị trung bình của các block pixel.
        """
        max_y_offset = height - self.BLOCK_SIZE
        max_x_offset = width - self.BLOCK_SIZE
        black_points = [[0] * sub_width for _ in range(sub_height)]

        for y in range(sub_height):
            y_offset = y * self.BLOCK_SIZE
            if y_offset > max_y_offset:
                y_offset = max_y_offset
            for x in range(sub_width):
                x_offset = x * self.BLOCK_SIZE
                if x_offset > max_x_offset:
                    x_offset = max_x_offset

                sum_pixels = 0
                min_pixel = 255
                max_pixel = 0

                # Duyệt qua các pixel trong block
                for yy in range(self.BLOCK_SIZE):
                    row_start = (y_offset + yy) * width + x_offset
                    for xx in range(self.BLOCK_SIZE):
                        pixel = luminances[row_start + xx]
                        sum_pixels += pixel
                        min_pixel = min(min_pixel, pixel)
                        max_pixel = max(max_pixel, pixel)

                # Tính giá trị trung bình
                average = sum_pixels // (self.BLOCK_SIZE * self.BLOCK_SIZE)

                # Kiểm tra nếu dải động thấp
                if max_pixel - min_pixel <= self.MIN_DYNAMIC_RANGE:
                    average = min_pixel // 2

                    if y > 0 and x > 0:
                        # Trích xuất các điểm ảnh lân cận và chuyển sang kiểu float
                        top = float(black_points[y - 1][x])
                        left = float(black_points[y][x - 1])
                        top_left = float(black_points[y - 1][x - 1])

                        # Tính trung bình của các điểm ảnh lân cận
                        temp = (top + (2 * left) + top_left) / 4

                        # Giới hạn giá trị trong phạm vi [0, 255]
                        neighbor_avg_black_point = int(temp)
                        if min_pixel < neighbor_avg_black_point:
                            average = neighbor_avg_black_point
                black_points[y][x] = average

        return black_points
