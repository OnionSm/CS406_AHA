import math
import DetectorResult
import FinderPatternFinder
from interfaces import ResultPointCallback


from enums import DecodeHintType


class NotFoundException(Exception):
    """Raised when a QR Code cannot be found in the image."""
    
    def __init__(self, message="QR Code cannot be found in the image", details=None):
        """
        Initializes the exception with a message and optional details.
        
        :param message: The error message describing the exception (default is a general message).
        :param details: Additional details about the exception, if any.
        """
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        """
        Returns a string representation of the exception, including details if provided.
        """
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message
    
class FormatException(Exception):
    """Raised when a QR Code cannot be decoded correctly."""
    
    def __init__(self, message="QR Code cannot be decoded correctly", error_code=None):
        """
        Initializes the exception with a message and optional error code.
        
        :param message: The error message describing the exception (default is a general message).
        :param error_code: A code representing the specific format error, if any.
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        """
        Returns a string representation of the exception, including the error code if provided.
        """
        if self.error_code:
            return f"{self.message}. Error Code: {self.error_code}"
        return self.message



class Detector():
    def __init__(self, image):
        self.image = image

    # def detect(self, hints=None): # hint Map<DecodeHintType,?> hints
    #     """
    #     Detects a QR Code in an image.

    #     :param hints: Optional hints for the detection process (default is None).
    #     :return: DetectorResult containing the detection results.
    #     :raises NotFoundException: If a QR Code cannot be found.
    #     :raises FormatException: If a QR Code cannot be decoded.
    #     """
    #     if hints is None:
    #         result_point_callback = None 
    #     else:
    #         result_point_callback = hints.get(DecodeHintType.NEED_RESULT_POINT_CALLBACK, None)
    #         finder = FinderPatternFinder(self.image, result_point_callback)
    #         info = finder.find(hints)
    #         return self.processFinderPatternInfo(info)

    #     # Default detection logic when no hints are provided
    #     return self.detect_with_default()

    # def detect_with_default(self):
    #     """Handle the default detection logic."""
    #     raise NotFoundException("No QR Code found with default parameters.")


    def detect(self, hints=None): # hint Map<DecodeHintType,?> hints
        """
        Detects a QR Code in an image.

        :param hints: Optional hints for the detection process (default is None).
        :return: DetectorResult containing the detection results.
        :raises NotFoundException: If a QR Code cannot be found.
        :raises FormatException: If a QR Code cannot be decoded.
        """
        if hints is None:
            result_point_callback = None 
        else:
            result_point_callback = hints.get(DecodeHintType.NEED_RESULT_POINT_CALLBACK, None)

        finder = FinderPatternFinder(self.image, result_point_callback)
        info = finder.find(hints)
        return self.process_finder_pattern_info(info)
    
    def process_finder_pattern_info(self, info): # info (FinderPatternInfo)
        top_left = info.get_top_left()
        top_right = info.get_top_right()
        bottom_left = info.get_bottom_left()

        module_size = self.calculate_module_size(top_left, top_right, bottom_left)

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
        return (calculate_module_size_one_way(top_left, top_right) +
                calculate_module_size_one_way(top_left, bottom_left)) / 2.0


    def calculate_module_size_one_way(self, pattern, other_pattern): 
        """
        Input: pattern (ResultPoint), other_pattern 

        """
        module_size_est_1 = self.size_of_black_white_black_run_both_ways(
            int(pattern.get_x()), int(pattern.get_y()), int(other_pattern.get_x()), int(other_pattern.get_y()))
        module_size_est_2 = self.size_of_black_white_black_run_both_ways(
            int(other_pattern.get_x()), int(other_pattern.get_y()), int(pattern.get_x()), int(pattern.get_y()))
        if module_size_est_1 == float("nan"):
            return module_size_est_2 / 7.0
        if module_size_est_2 == float("nan"):
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
        width = self.image.shape[1]
        height = self.image.shape[0]
        result = self.size_of_black_white_black_run(from_x, from_y, to_x, to_y)
        scale = 1.0 
        # Tính điểm other_to_x, bằng cách lấy đối xứng với to_x thông qua from_x
        # Other_to_x sẽ được giới hạn trong khoảng width
        other_to_x = from_x - (to_x - from_x)
        if other_to_x < 0:
            scale = from_x / float(from_x - other_to_x)
            other_to_x = 0
        elif other_to_x >= width:
            scale = (width - 1 - from_x) / float(other_to_x - from_x)
            other_to_x = width - 1

        other_to_y = int(from_y - (to_y - from_y) * scale)

        scale = 1.0
        if other_to_y < 0:
            scale = from_y / float(from_y - other_to_y)
            other_to_y = 0
        elif other_to_y >= height:
            scale = (height - 1 - from_y) / float(other_to_y - from_y)
            other_to_y = height - 1
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

         # Trong các pixel đen, tìm kiếm pixel trắng lần đầu hoặc lần thứ hai
        state = 0
        x_limit = to_x + xstep

        for x, y in zip(range(from_x, x_limit, xstep), range(from_y, ystep)):
            real_x = y if steep else x
            real_y = x if steep else y

            # Kiểm tra nếu pixel hiện tại có thay đổi màu sắc (từ đen sang trắng hoặc ngược lại)
            if (state == 1) == self.image[real_y][real_x]:
                if state == 2:
                    return math.dist((x, y), (from_x, from_y))
                state += 1

            error += dy
            if error > 0:
                if y == to_y:
                    break
                y += ystep
                error -= dx

        # Nếu tìm thấy đoạn black-white-black, trả về khoảng cách đến điểm cuối
        if state == 2:
            return math.dist((to_x + xstep, to_y), (from_x, from_y))

        # Nếu không tìm thấy đoạn black-white-black, trả về NaN
        return float('nan')
        

  
