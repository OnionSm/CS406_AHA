import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import math
from .DetectorResult import DetectorResult
from .FinderPatternFinder import FinderPatternFinder
from interfaces import ResultPointCallback
from .ResultPoint import ResultPoint
from qrcode import Version, BitMatrix
from .AlignmentPattern import AlignmentPattern
from .AlignmentPatternFinder import AlignmentPatternFinder
from exceptions import FormatException, NotFoundException
from .FinderPatternInfo import FinderPatternInfo
from .FinderPattern import FinderPattern
from common.PerspectiveTransform import PerspectiveTransform
from common.GridSampler import GridSampler
from common.DefaultGridSampler import DefaultGridSampler
from enums import DecodeHintType


    


class Detector:
    def __init__(self, image):
        """
        Property: 
        - image : BitMatrix
        - result_point_call_back : ResultPointCallBack
        """
        self.image: BitMatrix = image
        self.result_point_callback = None
    
 
    def detect(self, hints=None): # hint Map<DecodeHintType,?> hints
        """
        Detects a QR Code in an image.

        :param hints: Optional hints for the detection process (default is None).
        :return: DetectorResult containing the detection results.
        :raises NotFoundException: If a QR Code cannot be found.
        :raises FormatException: If a QR Code cannot be decoded.
        """
        if hints is None:
            self.result_point_callback = None 
        else:
            self.result_point_callback = hints.get(DecodeHintType.NEED_RESULT_POINT_CALLBACK, None)

        finder: FinderPatternFinder = FinderPatternFinder(self.image, self.result_point_callback)
        info: FinderPatternInfo = finder.find(hints)
        return self.process_finder_pattern_info(info)
    
    
    def process_finder_pattern_info(self, info): # info (FinderPatternInfo)
        top_left: FinderPattern = info.get_top_left()
        top_right: FinderPattern = info.get_top_right()
        bottom_left: FinderPattern = info.get_bottom_left()
        module_size = self.calculate_module_size(top_left, top_right, bottom_left)
        if module_size < 1.0:
            # raise NotFoundException("Module size less than 1")
            return None
        dimension: int = self.compute_dimension(top_left, top_right, bottom_left, module_size)
        provisional_version = Version.VersionManager.get_provisional_version_for_dimension(dimension)
        if provisional_version is None:
            return None
        module_between_fp_centers = provisional_version.get_dimension_for_version() - 7
        
        alignment_pattern = None 
        if len(provisional_version.get_alignment_pattern_centers()) > 0:
            bottom_right_x = top_right.get_x() - top_left.get_x() + bottom_left.get_x()
            bottom_right_y = top_right.get_y() - top_left.get_y() + bottom_left.get_y()

            correction_to_top_left = 1.0 - 3.0 / module_between_fp_centers
            estimate_alignment_x = int(top_left.get_x() + correction_to_top_left * (bottom_right_x - top_left.get_x()))
            estimate_alignment_y = int(top_left.get_y() + correction_to_top_left * (bottom_right_y - top_left.get_y()))

            i = 4
            while i <= 16:
                try:
                    alignment_pattern = self.find_alignment_in_region(module_size, 
                                                                 estimate_alignment_x, 
                                                                estimate_alignment_y, 
                                                                i)
                    break
                except NotFoundException:
                    i <<= 1  
        transform: PerspectiveTransform = Detector.create_transform(top_left, top_right, bottom_left, alignment_pattern, dimension)
        if transform is None:
            return None
        bits: BitMatrix = Detector.sample_grid(self.image, transform, dimension)
        if alignment_pattern is None:
            points = [bottom_left, top_left, top_right]
        else:
            points = [bottom_left, top_left, top_right, alignment_pattern]

        return DetectorResult(bits, points) 


    @staticmethod
    def create_transform(top_left, top_right, bottom_left, alignment_pattern, dimension):
        """ 
        Input:
        - top_left: ResultPoint
        - top_right: ResultPoint 
        - bottom_left: ResultPoint
        - alignment_pattern: ResultPoint 
        - dimension: int
        """             
        dim_minus_three = dimension - 3.5
        bottom_right_x = 0
        bottom_right_y = 0
        source_bottom_right_x = 0
        source_bottom_right_y = 0 
        if alignment_pattern is not None:
            bottom_right_x =  alignment_pattern.get_x()
            bottom_right_y = alignment_pattern.get_y()
            source_bottom_right_x = dim_minus_three - 3.0
            source_bottom_right_y = source_bottom_right_x
        else:
            # Don't have an alignment pattern, just make up the bottom-right point
            bottom_right_x = (top_right.get_x() - top_left.get_x()) + bottom_left.get_x()
            bottom_right_y = (top_right.get_y() - top_left.get_y()) + bottom_left.get_y()
            source_bottom_right_x = dim_minus_three
            source_bottom_right_y = dim_minus_three
        return PerspectiveTransform.quadrilateral_to_quadrilateral(
            3.5,
            3.5,
            dim_minus_three,
            3.5,
            source_bottom_right_x,
            source_bottom_right_y,
            3.5,
            dim_minus_three,
            
            top_left.get_x(),
            top_left.get_y(),
            top_right.get_x(),
            top_right.get_y(),
            bottom_right_x,
            bottom_right_y,
            bottom_left.get_x(),
            bottom_left.get_y()
        )
    
    
    @staticmethod
    def sample_grid(image, transform, dimension):
        """
        Input: 
        - image: BitMatrix 
        - transform: PerpectiveTransform 
        - dimension: int
        Output:
        - BitMatrix
        """
        try:
            # sampler = GridSampler.get_instance()
            # sampler = DefaultGridSampler()
            # print(type(sampler))
            print("Transform", transform)
            return DefaultGridSampler.sample_grid(image, dimension, dimension, transform)
        except Exception as e:
            # raise NotFoundException("Sample grid failed") from e
            return None

    @staticmethod
    def compute_dimension(top_left, top_right, bottom_left, module_size):
        """
        Input: 
        - top_left, top_right, bottom_left : ResultPoint
        - module_size : float
        Output: 
        - dimension : float
        Hàm này tính khoảng cách của finder pattern top_left với top_right
        và top_left với bottom_left sau đó lấy trung bình 2 khoảng cách và cộng thêm 7
        để ra số module của QR code
        """
        # Tính khoảng cách giữa các điểm và chia cho kích thước module
        tltr_centers_dimension = round(ResultPoint.distance(top_left, top_right) / module_size)
        tlbl_centers_dimension = round(ResultPoint.distance(top_left, bottom_left) / module_size)

        
        # Tính toán dimension
        dimension = ((tltr_centers_dimension + tlbl_centers_dimension) // 2) + 7
        # Áp dụng mod 4 và điều chỉnh dimension
        if dimension % 4 == 0:
            dimension += 1
        elif dimension % 4 == 2:
            dimension -= 1
        elif dimension % 4 == 3:
            raise NotFoundException()
        
        return dimension



    def calculate_module_size(self, top_left, top_right, bottom_left):
        """
        Calculate the module size by averaging the sizes calculated
        in two directions: topLeft -> topRight and topLeft -> bottomLeft.
        
        Args:
            top_left (ResultPoint): The top-left point.
            top_right (ResultPoint): The top-right point.
            bottom_left (ResultPoint): The bottom-left point.

        Returns:
            float: The average module size.
        """
        return (self.calculate_module_size_one_way(top_left, top_right) +
                self.calculate_module_size_one_way(top_left, bottom_left)) / 2.0


    def calculate_module_size_one_way(self, pattern: ResultPoint, other_pattern: ResultPoint): 
        """
        Đầu vào:
            pattern (ResultPoint): Một điểm đại diện cho vị trí đầu tiên trên hình ảnh hoặc mã vạch.
            other_pattern (ResultPoint): Một điểm đại diện cho vị trí thứ hai trên hình ảnh hoặc mã vạch.

        Đầu ra:
            float: Kích thước ước lượng của một module trong mã vạch hoặc mẫu. Kết quả được tính dựa trên trung bình 
                  của hai ước lượng kích thước module, một ước lượng theo mỗi hướng (từ `pattern` đến `other_pattern` 
                  và ngược lại). Giá trị này được điều chỉnh bằng cách chia cho 14, vì đoạn được xem xét bao gồm 3 
                  module đen, 1 module trắng và 1 module đen ở mỗi đầu.

        Mô tả:
            Hàm này ước lượng kích thước của một module trong mã vạch hoặc mẫu hình ảnh bằng cách sử dụng hai 
            ước tính về kích thước đoạn "black-white-black", mỗi ước tính theo một hướng khác nhau. Hàm sử dụng 
            chức năng `size_of_black_white_black_run_both_ways` để tính toán các ước lượng kích thước. Nếu một trong 
            các ước tính không hợp lệ (NaN), ước tính còn lại sẽ được sử dụng để trả về kết quả. Kết quả cuối cùng là 
            trung bình của hai ước tính, chia cho 14, để phù hợp với cấu trúc của mẫu gồm nhiều module đen và trắng. 
            Phương pháp này giúp cải thiện độ chính xác trong việc tính toán kích thước module khi xem xét các góc độ khác nhau.
        """
        module_size_est_1 = self.size_of_black_white_black_run_both_ways(
            int(pattern.get_x()), int(pattern.get_y()), int(other_pattern.get_x()), int(other_pattern.get_y()))
        module_size_est_2 = self.size_of_black_white_black_run_both_ways(
            int(other_pattern.get_x()), int(other_pattern.get_y()), int(pattern.get_x()), int(pattern.get_y()))
        if math.isnan(module_size_est_1):
            return module_size_est_2 / 7.0
        if math.isnan(module_size_est_2):
            return module_size_est_1 / 7.0
        return (module_size_est_1 + module_size_est_2) / 14.0
    

    def size_of_black_white_black_run_both_ways(self, from_x, from_y, to_x, to_y):
        """
        Tính toán các đoạn black-white-black theo 2 chiều
        Tính từ (from_x, form_y) đến (to_x, to_y)
        Sau đó tính điểm (other_x, other_y) và cũng tính toán black-white-blackblack
        Kết quả trả về là tổng độ dài của 2 đoạn thẳng 
        Việc tính toán 2 hướng bao gồm thuận và đối xứng này giúp thuật toán tính toán chính xác hơn,
        nhất là trong trường hợp các điểm vượt ra ngoài rìa của ảnh hoặc khi đoạn đường 
        có thể đi qua các pixel biên của ảnh.
        """
        result = self.size_of_black_white_black_run(from_x, from_y, to_x, to_y)
        scale = 1.0 
        # Tính điểm other_to_x, bằng cách lấy đối xứng với to_x thông qua from_x
        # Other_to_x sẽ được giới hạn trong khoảng width
        other_to_x = from_x - (to_x - from_x)
        if other_to_x < 0:
            scale = from_x / float(from_x - other_to_x)
            other_to_x = 0
        elif other_to_x >= self.image.get_width():
            scale = (self.image.get_width() - 1 - from_x) / float(other_to_x - from_x)
            other_to_x = self.image.get_width() - 1

        other_to_y = int(from_y - (to_y - from_y) * scale)

        scale = 1.0
        if other_to_y < 0:
            scale = from_y / float(from_y - other_to_y)
            other_to_y = 0
        elif other_to_y >= self.image.get_height():
            scale = (self.image.get_height() - 1 - from_y) / float(other_to_y - from_y)
            other_to_y = self.image.get_height() - 1
        other_to_x = int( from_x + (other_to_x - from_x) * scale)

        result += self.size_of_black_white_black_run(from_x, from_y, other_to_x, other_to_y)
        return result - 1.0 # trừ 1 vì pixel trung tâm được tính 2 lần
    


    def size_of_black_white_black_run(self, from_x, from_y, to_x, to_y):
        """
        Hàm này được sử dụng để trả về khoảng cách của 2 điểm (from_x, from_y) và (to_x, to_y)
        nếu như tìm thấy đoạn black-white-black
        """
        # Biến thể nhẹ của thuật toán Bresenham
        steep = abs(to_y - from_y) > abs(to_x - from_x)
        if steep:
            from_x, from_y, to_x, to_y = from_y, from_x, to_y, to_x
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        error = -dx // 2
        xstep = 1 if from_x < to_x else -1
        ystep = 1 if from_y < to_y else -1

        state = 0
        x, y = from_x, from_y

        while x != to_x + xstep:
            real_x = y if steep else x
            real_y = x if steep else y

            # Kiểm tra nếu pixel hiện tại có thay đổi màu sắc (từ đen sang trắng hoặc ngược lại)
            if (state == 1) == self.image.get(real_x, real_y):
                if state == 2:
                    return math.dist((x, y), (from_x, from_y))
                state += 1
            error += dy
            if error > 0:
                if y == to_y:
                    break
                y += ystep
                error -= dx
            x += xstep
        # Nếu tìm thấy đoạn black-white-black, trả về khoảng cách đến điểm cuối
        if state == 2:
            return math.dist((to_x + xstep, to_y), (from_x, from_y))
        # Nếu không tìm thấy đoạn black-white-black, trả về NaN
        return float('nan')
        
    def find_alignment_in_region(self, overall_est_module_size, est_alignment_x, est_alignment_y, allowance_factor):
        """
        Tìm kiếm một mẫu căn chỉnh (alignment pattern) trong một vùng xác định của hình ảnh.

        :param overall_est_module_size: Kích thước module ước tính.
        :param est_alignment_x: Tọa độ x ước tính của mẫu căn chỉnh.
        :param est_alignment_y: Tọa độ y ước tính của mẫu căn chỉnh.
        :param allowance_factor: Hệ số để tính toán phạm vi tìm kiếm.
        :return: Đối tượng AlignmentPattern.
        :raises NotFoundException: Nếu không thể tìm thấy mẫu căn chỉnh trong vùng xác định.

        """
        allowance = int(allowance_factor * overall_est_module_size)
        alignment_area_left_x = max(0, est_alignment_x - allowance)
        alignment_area_right_x = min(self.image.get_width() - 1, est_alignment_x + allowance)
        
        if alignment_area_right_x - alignment_area_left_x < overall_est_module_size * 3:
            raise NotFoundException()

        alignment_area_top_y = max(0, est_alignment_y - allowance)
        alignment_area_bottom_y = min(self.image.get_height() - 1, est_alignment_y + allowance)
        
        if alignment_area_bottom_y - alignment_area_top_y < overall_est_module_size * 3:
            raise NotFoundException()
        alignment_finder = AlignmentPatternFinder(
            self.image,
            alignment_area_left_x,
            alignment_area_top_y,
            alignment_area_right_x - alignment_area_left_x,
            alignment_area_bottom_y - alignment_area_top_y,
            overall_est_module_size,
            self.result_point_callback
        )
        return alignment_finder.find()
    
  
