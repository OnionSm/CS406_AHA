import sys 
import os


from qrcode import BitMatrix

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import math
from .FinderPattern import FinderPattern
from .ResultPoint import ResultPoint
from .FinderPatternInfo import FinderPatternInfo
from enums import DecodeHintType
from typing import List

class FinderPatternNotFoundException(Exception):
    """
    Custom exception to handle cases where finder patterns are not found.
    Inherits from Python's built-in Exception class.
    """

    def __init__(self, message="Finder patterns not found."):
        """
        Initializes the exception with an optional custom message.

        Args:
            message (str): A custom error message. Defaults to a generic message.
        """
        super().__init__(message)

class EstimatedModuleComparator:
    """
    Orders by FinderPattern.get_estimated_module_size()
    """
    @staticmethod
    def compare(center1, center2):
        return (center1.get_estimated_module_size() > center2.get_estimated_module_size()) - \
               (center1.get_estimated_module_size() < center2.get_estimated_module_size())



class FinderPatternFinder:
    
    

    def __init__(self, image, result_point_callback=None):
        """
        Creates a finder that will search the image for three finder patterns.

        :param image: The BitMatrix image to search.
        :param result_point_callback: Callback for result points (optional).
        """
        self.image: BitMatrix = image
        self.possible_centers: List[FinderPattern] = []
        self.cross_check_state_count: List = [0] * 5
        self.result_point_callback = result_point_callback
        self.has_skipped: bool = False
        self.CENTER_QUORUM: int  = 2
        self.MIN_SKIP: int = 3  # 1 pixel/module times 3 modules/center
        self.MAX_MODULES: int = 97  # support up to version 20 for mobile clients
        self.module_comparator = EstimatedModuleComparator()


    def get_image(self):
        """
        Returns the image being searched.
        :return: The BitMatrix image.
        """
        return self.image

    def get_possible_centers(self):
        """
        Returns the list of possible finder pattern centers.
        :return: List of possible centers.
        """
        return self.possible_centers

    def find(self, hints):
        try_harder = hints is not None and DecodeHintType.TRY_HARDER in hints
        max_i = self.image.get_height()
        max_j = self.image.get_width()

        # Tính toán bước nhảy ban đầu
        i_skip = (3 * max_i) // (4 * self.MAX_MODULES)
        if i_skip < self.MIN_SKIP or try_harder:
            i_skip = self.MIN_SKIP

        done = False
        state_count = [0] * 5
        i = i_skip - 1

        while i < max_i and not done:
            # Xóa trạng thái đếm
            FinderPatternFinder.do_clear_counts(state_count)
            current_state = 0

            j = 0
            while j < max_j:
                if self.image.get(j, i):  # Black pixel
                    if (current_state & 1) == 1:  # Đang đếm pixel trắng
                        current_state += 1
                    state_count[current_state] += 1
                else:  # White pixel
                    if (current_state & 1) == 0:  # Đang đếm pixel đen
                        if current_state == 4:  # Một mẫu hợp lệ?
                            if self.found_pattern_cross(state_count):  # Đúng
                                confirmed = self.handle_possible_center(state_count, i, j)
                                if confirmed:
                                    # Xem xét từng dòng khác
                                    i_skip = 2
                                    if self.has_skipped:
                                        done = self.have_multiply_confirmed_centers()
                                    else:
                                        row_skip = self.find_row_skip()
                                        if row_skip > state_count[2]:
                                            # Bỏ qua các dòng một cách thận trọng
                                            i += row_skip - state_count[2] - i_skip
                                            j = max_j - 1
                                else:
                                    FinderPatternFinder.do_shift_counts2(state_count)
                                    current_state = 3
                                    continue

                                # Xóa trạng thái để bắt đầu tìm kiếm lại
                                current_state = 0
                                FinderPatternFinder.do_clear_counts(state_count)
                            else:  # Không hợp lệ, lùi lại hai bước
                                FinderPatternFinder.do_shift_counts2(state_count)
                                current_state = 3
                        else:
                            current_state += 1
                            state_count[current_state] += 1
                    else:  # Đang đếm pixel trắng
                        state_count[current_state] += 1

                j += 1

            if self.found_pattern_cross(state_count):
                confirmed = self.handle_possible_center(state_count, i, max_j)
                if confirmed:
                    i_skip = state_count[0]
                    if self.has_skipped:
                        done = self.have_multiply_confirmed_centers()

            i += i_skip

        pattern_info = self.select_best_patterns()
        if pattern_info is None:
            return None

        ResultPoint.order_best_patterns(pattern_info)
        return FinderPatternInfo(pattern_info)

    @staticmethod
    # each part of finder pattern only have below 50% variance
    def found_pattern_cross(state_count):
        total_module_size = 0
        for i in range(0,5):
            count = state_count[i]
            if count == 0:
                return False
            total_module_size += count
        if total_module_size < 7:
            return False
        module_size = total_module_size / 7.0
        max_variance = module_size / 2.0 
        return (
        abs(module_size - state_count[0]) < max_variance and
        abs(module_size - state_count[1]) < max_variance and
        abs(3.0 * module_size - state_count[2]) < 3 * max_variance and
        abs(module_size - state_count[3]) < max_variance and
        abs(module_size - state_count[4]) < max_variance
        )

    @staticmethod
    # calculate the width center of finder pattern
    def center_from_end(state_count, end):
        return (end - state_count[4] - state_count[3]) - state_count[2] / 2.0

    def cross_check_vertical(self, start_y, center_x, max_count, original_state_count_total):
        image = self.image
        height = image.height
        state_count = [0] * 5

        # Start counting up from the center
        y = start_y
        while y >= 0 and image.get(center_x, y):
            state_count[2] += 1
            y -= 1
        if y < 0:
            return float('nan')

        while y >= 0 and not image.get(center_x, y) and state_count[1] <= max_count:
            state_count[1] += 1
            y -= 1
        if y < 0 or state_count[1] > max_count:
            return float('nan')

        while y >= 0 and image.get(center_x, y) and state_count[0] <= max_count:
            state_count[0] += 1
            y -= 1
        if state_count[0] > max_count:
            return float('nan')

        # Start counting down from the center
        y = start_y + 1
        while y < height and image.get(center_x, y):
            state_count[2] += 1
            y += 1
        if y == height:
            return float('nan')

        while y < height and not image.get(center_x, y) and state_count[3] < max_count:
            state_count[3] += 1
            y += 1
        if y == height or state_count[3] >= max_count:
            return float('nan')

        while y < height and image.get(center_x, y) and state_count[4] < max_count:
            state_count[4] += 1
            y += 1
        if state_count[4] >= max_count:
            return float('nan')

        # Validate the state counts
        state_count_total = sum(state_count)
        if 5 * abs(state_count_total - original_state_count_total) >= 2 * original_state_count_total:
            return float('nan')

        # Check for a valid finder pattern
        return FinderPatternFinder.center_from_end(state_count, y) if self.found_pattern_cross(state_count) else float('nan')

    def cross_check_horizontal(self,center_x, center_y, max_count, original_state_count_total):
        width = self.image.get_width()
        state_count = [0] * 5
        x = int(center_x)
        center_y = int(center_y)

        # start count left from center_x in center_y row 
        while x >= 0 and self.image.get(x,center_y): # count black
            state_count[2] += 1
            x -= 1
        if x < 0:
            return float('nan')
        while x >= 0 and not self.image.get(x,center_y) and state_count[1] <= max_count: # count white
            state_count[1] += 1
            x -= 1
        if x < 0 or state_count[1] > max_count:
            return float('nan')
        while x >= 0 and self.image.get(x,center_y) and state_count[0] <= max_count: # count black
            state_count[0] += 1
            x -= 1
        if state_count[0] > max_count:
            return float('nan')
        
        # start count right from center_y + 1 in center_y row
        x = center_x + 1
        while x < width and self.image.get(x,center_y): # count black
            state_count[2] += 1
            x += 1
        if x == width:
            return float('nan')
        while x < width and not self.image.get(x,center_y) and state_count[3] < max_count: # count white
            state_count[3] += 1
            x += 1
        if x == width or state_count[3] >= max_count:
            return float('nan')
        while x < width and self.image.get(x,center_y) and state_count[4] < max_count: # count black
            state_count[4] += 1
            x += 1
        if state_count[4] >= max_count:
            return float('nan')
        
          # If the total state count differs by more than 40%, it's a false positive
        state_count_total = sum(state_count)
        if 5 * abs(state_count_total - original_state_count_total) >= 2 * original_state_count_total:
            return float('nan')

        # Check if it matches a finder pattern
        return FinderPatternFinder.center_from_end(state_count, x) if self.found_pattern_cross(state_count) else float('nan')


    def cross_check_diagonal(self, center_y, center_x):
        state_count = [0] * 5
        
        # Start counting up, left from center 
        i = 0 
        while center_y >= i and center_x >= i and self.image.get(center_x - i,center_y - i): # count black
            state_count[2] += 1
            i += 1
        if state_count[2] == 0:
            return False
        while center_y >= i and center_x >= i and not self.image.get(center_x - i,center_y - i): # count white
            state_count[1] += 1
            i += 1
        if state_count[1] == 0:
            return False
        while center_y >= i and center_x >= i and self.image.get(center_x - i,center_y - i): # count black
            state_count[0] += 1
            i += 1
        if state_count[0] == 0:
            return False

        # Count down, right from center
        width = self.image.get_width()
        height = self.image.get_height()
        i = 1
        while center_y + i < height and center_x + i < width and self.image.get(center_x + i, center_y + i): # count black
            state_count[2] += 1
            i += 1
        while center_y + i < height and center_x + i < width and not self.image.get(center_x + i, center_y + i): # count white
            state_count[3] += 1
            i += 1
        if state_count[3] == 0:
            return False
        while center_y + i < height and center_x + i < width and self.image.get(center_x + i, center_y + i): # count black
            state_count[4] += 1
            i += 1
        if state_count[4] == 0:
            return False
         
        return FinderPatternFinder.found_pattern_diagonal(state_count)
    
    @staticmethod
    def found_pattern_diagonal(state_count):
        total_module_size = 0

        # Calculate total module size and validate each count
        for count in state_count:
            if count == 0:
                return False
            total_module_size += count

        if total_module_size < 7:
            return False

        module_size = total_module_size / 7.0
        max_variance = module_size / 1.333

        # Allow less than 75% variance from 1-1-3-1-1 proportions
        return (
            abs(module_size - state_count[0]) < max_variance and
            abs(module_size - state_count[1]) < max_variance and
            abs(3.0 * module_size - state_count[2]) < 3 * max_variance and
            abs(module_size - state_count[3]) < max_variance and
            abs(module_size - state_count[4]) < max_variance
        )

    

    def handle_possible_center(self, state_count,i,j):
        state_count_total = sum(state_count)
        center_width = FinderPatternFinder.center_from_end(state_count, j)
        center_height = self.cross_check_vertical(i, int(center_width), state_count[2], state_count_total)
        if not math.isnan(center_height):
            # re-cross check 
            center_width = self.cross_check_horizontal(int(center_width), int(center_height), state_count[2], state_count_total)
            if not math.isnan(center_width):
                if self.cross_check_diagonal(int(center_height), int(center_width)):
                    estimated_module_size = state_count_total / 7.0
                    found = False


                    for i in range(0, len(self.possible_centers)):
                        center = self.possible_centers[i]

                        #Look for about the same center and module size:
                        if center.about_equals(estimated_module_size, center_height, center_width):
                            self.possible_centers[i] = center.combine_estimate(center_height, center_width, estimated_module_size)
                            found = True
                            break
                    if not found:
                    
                        point = FinderPattern(center_width, center_height, estimated_module_size)
                        self.possible_centers.append(point)

                        # CALL BACK WILL BE IMPLEMENTED HERE
                    return True
                for i in range(0, len(self.possible_centers)):
                    center = self.possible_centers[i]
            return False
        
    def have_multiply_confirmed_centers(self):
        confirmed_count = 0
        total_module_size = 0.0
        _max = len(self.possible_centers)
        # Count confirmed centers and calculate total module size
        for pattern in self.possible_centers:
            if pattern.get_count() >= self.CENTER_QUORUM:
                confirmed_count += 1
                total_module_size += pattern.get_estimated_module_size()

        # If less than 3 confirmed centers, return False
        if confirmed_count < 3:
            return False

        # Calculate the average module size
        average = total_module_size / _max

        # Calculate the total deviation from the average
        total_deviation = sum(
            abs(pattern.get_estimated_module_size() - average) for pattern in self.possible_centers
        )

        # Check if the total deviation is within 5% of the total module size
        return total_deviation <= 0.05 * total_module_size
    
    def find_row_skip(self):
        _max:int  = len(self.possible_centers)
        if _max <= 1:
            return 0
        first_confirmed_center = None
        for center in self.possible_centers:
            if center.get_count() >= self.CENTER_QUORUM:
                if first_confirmed_center is None:
                    first_confirmed_center = center
                else:
                    # We have two confirmed centers
                    # Calculate how far down to skip based on the difference in coordinates
                    # This assumes the worst case where the top left is found last.
                    self.has_skipped = True
                    return int((
                        abs(first_confirmed_center.get_x() - center.get_x()) -
                        abs(first_confirmed_center.get_y() - center.get_y())
                    ) / 2)
        return 0

    @staticmethod
    def squared_distance(a, b):
        x = a.get_x() - b.get_x()
        y = a.get_y() - b.get_y()
        return x * x + y * y

    def select_best_patterns(self):
        start_size = len(self.possible_centers)
        if start_size < 3:
            # raise FinderPatternNotFoundException("Not enough finder patterns found.")
            print("Not enough finder patterns found.")
            return None
        # Remove patterns that don't meet the count threshold
        # Lọc các FinderPattern có `get_count()` >= CENTER_QUORUM
        self.possible_centers = [fp for fp in self.possible_centers if fp.get_count() >= self.CENTER_QUORUM]

        # # In ra danh sách các FinderPattern trước khi sắp xếp, với các thuộc tính `count` và `estimated_module_size`
        # print("Before:")
        # for fp in self.possible_centers:
        #     print(f"FinderPattern(count={fp.get_count()}, estimated_module_size={fp.get_estimated_module_size()})")

        # Sắp xếp theo `estimated_module_size`
        self.possible_centers.sort(key=lambda x: x.get_estimated_module_size())

        # In ra danh sách các FinderPattern sau khi sắp xếp
        # print("After:")
        # for fp in self.possible_centers:
        #     print(f"FinderPattern(count={fp.get_count()}, estimated_module_size={fp.get_estimated_module_size()})")
        distortion = float('inf')
        best_patterns = [None, None, None]

        for i in range(len(self.possible_centers) - 2):
            fpi = self.possible_centers[i]
            min_module_size = fpi.get_estimated_module_size()

            for j in range(i + 1, len(self.possible_centers) - 1):
                fpj = self.possible_centers[j]
                squares0 = FinderPatternFinder.squared_distance(fpi, fpj)

                for k in range(j + 1, len(self.possible_centers)):
                    fpk = self.possible_centers[k]
                    max_module_size = fpk.get_estimated_module_size()
                    if max_module_size > min_module_size * 1.4:
                        # Module size is not similar
                        continue

                    a = squares0
                    b = FinderPatternFinder.squared_distance(fpj, fpk)
                    c = FinderPatternFinder.squared_distance(fpi, fpk)

                    # Sort values a, b, c
                    if a > b:
                        a, b = b, a
                    if b > c:
                        b, c = c, b
                    if a > b:
                        a, b = b, a

                    # Check isosceles right triangle
                    d = abs(c - 2 * b) + abs(c - 2 * a)
                    if d < distortion:
                        distortion = d
                        best_patterns = [fpi, fpj, fpk]

        if distortion == float('inf'):
            # raise FinderPatternNotFoundException("No suitable patterns found.")
            print("No suitable patterns found")
            return None
        return best_patterns

    @staticmethod
    def do_clear_counts(counts):
        counts[:] = [0] * len(counts)

    @staticmethod
    def do_shift_counts2(state_count):
        state_count[0] = state_count[2]
        state_count[1] = state_count[3]
        state_count[2] = state_count[4]
        state_count[3] = 1
        state_count[4] = 0






        





        


        
        
        
        
    
    

    


