import numpy as np
from .LuminanceSource import LuminanceSource
from qrcode import BitMatrix, BitArray
from exceptions import NotFoundException
from .Binarizer import Binarizer


class GlobalHistogramBinarizer(Binarizer):
    """
    Thuật toán nhị phân hóa dựa trên histogram toàn cục, phù hợp với các thiết bị có tài nguyên hạn chế.
    """
    LUMINANCE_BITS = 5
    LUMINANCE_SHIFT = 8 - LUMINANCE_BITS
    LUMINANCE_BUCKETS = 1 << LUMINANCE_BITS

    def __init__(self, source):
        super().__init__(source)
        self.luminances = np.array([], dtype=np.uint8)
        self.buckets = np.zeros(self.LUMINANCE_BUCKETS, dtype=int)

    def get_black_row(self, y: int , row: BitArray):
        """
        Trích xuất và nhị phân hóa một dòng trong ảnh.
        """
        source: LuminanceSource = self.get_luminance_source()
        width: int = source.get_width()

        if row is None or row.get_size() < width:
            row = BitArray(width)
        else:
            row.clear()

        self.init_arrays(width)
        local_luminances = source.get_row(y, self.luminances)
        local_buckets = self.buckets

        for x in range(width):
            local_buckets[(local_luminances[x] & 0xFF) >> self.LUMINANCE_SHIFT] += 1

        black_point = self.estimate_black_point(local_buckets)

        if width < 3:
            for x in range(width):
                if (local_luminances[x] & 0xFF) < black_point:
                    row.set(x)
        else:
            left = local_luminances[0] & 0xFF
            center = local_luminances[1] & 0xFF
            for x in range(1, width - 1):
                right = local_luminances[x + 1] & 0xFF
                if ((center * 4) - left - right) // 2 < black_point:
                    row.set(x)
                left = center
                center = right

        return row
    
    def create_binarizer(self, source):
        """
        Tạo một Binarizer mới dựa trên nguồn ánh sáng (LuminanceSource).

        Args:
            source (LuminanceSource): Nguồn ánh sáng được sử dụng.

        Returns:
            Binarizer: Một thể hiện của GlobalHistogramBinarizer.
        """
        return GlobalHistogramBinarizer(source)

    def get_black_matrix(self):
        """
        Trích xuất và nhị phân hóa toàn bộ ảnh dưới dạng ma trận bit.
        """
        source = self.get_luminance_source()
        width = source.get_width()
        height = source.get_height()
        matrix = BitMatrix(width, height)

        self.init_arrays(width)
        local_buckets = self.buckets

        for y in range(1, 5):
            row = height * y // 5
            local_luminances = source.get_row(row, self.luminances)
            right = (width * 4) // 5
            for x in range(width // 5, right):
                pixel = local_luminances[x] & 0xFF
                local_buckets[pixel >> self.LUMINANCE_SHIFT] += 1

        black_point = self.estimate_black_point(local_buckets)
        local_luminances = source.get_matrix()

        for y in range(height):
            offset = y * width
            for x in range(width):
                pixel = local_luminances[offset + x] & 0xFF
                if pixel < black_point:
                    matrix.set(x, y)

        return matrix

    def init_arrays(self, luminance_size):
        """
        Khởi tạo hoặc làm sạch các mảng dữ liệu.
        """
        if len(self.luminances) < luminance_size:
            self.luminances = np.zeros(luminance_size, dtype=np.uint8)
        self.buckets.fill(0)

    @staticmethod
    def estimate_black_point(buckets):
        """
        Ước tính điểm đen dựa trên histogram.
        """
        num_buckets = len(buckets)
        max_bucket_count = max(buckets)

        first_peak = 0
        first_peak_size = 0
        for x in range(num_buckets):
            if buckets[x] > first_peak_size:
                first_peak = x
                first_peak_size = buckets[x]

        second_peak = 0
        second_peak_score = 0
        for x in range(num_buckets):
            distance_to_biggest = x - first_peak
            score = buckets[x] * distance_to_biggest * distance_to_biggest
            if score > second_peak_score:
                second_peak = x
                second_peak_score = score

        if first_peak > second_peak:
            first_peak, second_peak = second_peak, first_peak

        if second_peak - first_peak <= num_buckets // 16:
            raise NotFoundException.get_not_found_instance()

        best_valley = second_peak - 1
        best_valley_score = -1
        for x in range(second_peak - 1, first_peak, -1):
            from_first = x - first_peak
            score = from_first * from_first * (second_peak - x) * (max_bucket_count - buckets[x])
            if score > best_valley_score:
                best_valley = x
                best_valley_score = score

        return best_valley << GlobalHistogramBinarizer.LUMINANCE_SHIFT
