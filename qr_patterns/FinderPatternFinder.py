import functools
import FinderPattern
import ResultPoint
import FinderPatternInfo
from enums import DecodeHintType

class EstimatedModuleComparator:
    """
    So sánh hai FinderPattern dựa trên giá trị `estimatedModuleSize`.
    """

    def __call__(self, center1, center2):
        """
        Phương thức gọi lại để so sánh hai FinderPattern.
        
        :param center1: FinderPattern thứ nhất.
        :param center2: FinderPattern thứ hai.
        :return: Giá trị so sánh giữa `estimatedModuleSize` của hai FinderPattern.
        """
        return (center1.get_estimated_module_size() > center2.get_estimated_module_size()) - (center1.get_estimated_module_size() < center2.get_estimated_module_size())


class DecodeHintType:
    TRY_HARDER = "TRY_HARDER"


class FinderPatternFinder:
    
    

    def __init__(self, image, result_point_callback=None):
        """
        Creates a finder that will search the image for three finder patterns.

        :param image: The BitMatrix image to search.
        :param result_point_callback: Callback for result points (optional).
        """
        self.image = image
        self.possible_centers = []
        self.cross_check_state_count = [0] * 5
        self.result_point_callback = result_point_callback
        self.has_skipped = False
        self.CENTER_QUORUM = 2
        self.MIN_SKIP = 3  # 1 pixel/module times 3 modules/center
        self.MAX_MODULES = 97  # support up to version 20 for mobile clients
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
        height = self.image.shape[0]  
        width = self.image.shape[1]

        # Chúng ta đang tìm kiếm các mô-đun black/white/black/white/black trong tỷ lệ 1:1:3:1:1
        # Điều này theo dõi số lượng các mô-đun này đã thấy cho đến nay.

        # Giả sử rằng phiên bản QR Code tối đa mà chúng ta hỗ trợ chiếm 1/4 chiều cao của
        # hình ảnh, và sau đó tính đến việc trung tâm có kích thước 3 mô-đun. Điều này cung cấp
        # số pixel nhỏ nhất mà trung tâm có thể có, vì vậy thường xuyên bỏ qua điều này.
        # Khi cố gắng tìm kiếm cẩn thận hơn, tìm kiếm tất cả các phiên bản QR bất kể chúng dày như thế nào.

        # I IS THE ROW (Y)
        # J IS THE COLUMN (X)
        # numpy array [y][x] height width
        i_skip = (3 * height) // (4 * self.MAX_MODULES)
        if i_skip < self.MIN_SKIP or try_harder:
            i_skip = self.MIN_SKIP
        done = False
        state_count = [0 for i in range(5)]
        i = i_skip -1 
        while i < height and not done:
            current_state = 0
            for j in range(0, width):
                if self.image[i][j] == 0: # black pixel
                    if current_state % 2 == 1: # current state is white
                        current_state += 1
                    state_count[current_state] += 1
                else: # white pixel
                    if current_state % 2 == 0: # current is black state
                        if current_state == 4: # current state is the last state
                            if self.found_pattern_cross(state_count): # maybe finder pattern
                                confirmed = self.handle_possible_center(state_count,i,j)
                                if confirmed: # is finder pattern
                                    i_skip = 2
                                    if self.has_skipped: # can skip row
                                        done = self.have_multiply_confirmed_centers()
                                    else:
                                        row_skip = self.find_row_skip()
                                        if row_skip > state_count[2]:
                                            i += (row_skip - state_count[2] - i_skip)
                                            j = width - 1
                                else: # is not finder pattern 
                                    state_count = self.do_shift_count(state_count)
                                    current_state = 3
                                    continue

                                current_state = 0
                                state_count = [0 for i in range[5]]
                            
                            else:
                                state_count = self.do_shift_count(state_count)
                                current_state = 3

                        else:  # current is not the last state
                            current_state += 1
                            state_count[current_state] += 1
                    else: # current is white state 
                        state_count[current_state] += 1
            if self.found_pattern_cross(state_count):
                confirmed = self.handle_possible_center(state_count, i, width)
                if confirmed:
                    i_skip = state_count[0]
                    if self.has_skipped:
                        done = self.have_multiply_confirmed_centers()
            i += i_skip
        
        pattern_info = self.select_best_pattern()
        ResultPoint.order_best_patterns(pattern_info)

        return FinderPatternInfo(pattern_info)

        
            

    # each part of finder pattern only have below 50% variance
    def found_pattern_cross(self, state_count):
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
        # Allow less than 50% variance from 1-1-3-1-1 proportions
        return (
        abs(module_size - state_count[0]) < max_variance and
        abs(module_size - state_count[1]) < max_variance and
        abs(3.0 * module_size - state_count[2]) < 3 * max_variance and
        abs(module_size - state_count[3]) < max_variance and
        abs(module_size - state_count[4]) < max_variance
        )
    
    # calculate the width center of finder pattern
    def center_from_end(self, state_count, end):
        return (end - state_count[4] - state_count[3]) - state_count[2] / 2.0
    
    def cross_check_vertical(self,start_y, center_x, max_count, original_state_count_total):
        height = self.image.shape[0]
        state_count = [0 for i in range(5)]
        y = start_y

        # start count up from start_y in center_x column 
        while y >= 0 and self.image[y][center_x] == 0: # count black
            state_count[2] += 1
            y -= 1
        if y < 0:
            return float('nan')
        while y >= 0 and self.image[y][center_x] == 1 and state_count[1] <= max_count: # count white
            state_count[1] += 1
            y -= 1
        if y < 0 or state_count[1] > max_count:
            return float('nan')
        while y >= 0 and self.image[y][center_x] == 0 and state_count[0] <= max_count:  # count black
            state_count[0] += 1
            y -= 1
        if state_count[0] > max_count:
            return float('nan')
        
        # start count down from start_y + 1 in center_x column
        y = start_y + 1
        while y < height and self.image[y][center_x] == 0: # count black
            state_count[2] += 1
            y += 1
        if y == height:
            return float('nan')
        while y < height and not self.image[y][center_x] == 1 and state_count[3] < max_count: # count white
            state_count[3] += 1
            y += 1
        if y == height or state_count[3] >= max_count:
            return float('nan')
        while y < height and self.image[y][center_x] == 0 and state_count[4] < max_count: # count black
            state_count[4] += 1
            y += 1
        if state_count[4] >= max_count:
            return float('nan')
        
         # If the total state count differs by more than 40%, it's a false positive
        state_count_total = sum(state_count)
        if 5 * abs(state_count_total - original_state_count_total) >= 2 * original_state_count_total:
            return float('nan')

        # Check if it matches a finder pattern
        return self.center_from_end(state_count, y) if self.found_pattern_cross(state_count) else float('nan')


    def cross_check_horizontal(self,center_x, center_y, max_count, original_state_count_total):
        width = self.image.shape[1]
        state_count = [0 for i in range(5)]
        x = center_x

        # start count left from center_x in center_y row 
        while x >= 0 and self.image[center_y][x] == 0: # count black
            state_count[2] += 1
            x -= 1
        if x < 0:
            return float('nan')
        while x >= 0 and self.image[center_y][x] == 1 and state_count[1] <= max_count: # count white
            state_count[1] += 1
            x -= 1
        if x < 0 or state_count[1] > max_count:
            return float('nan')
        while x >= 0 and self.image[center_y][x] == 0 and state_count[0] <= max_count: # count black
            state_count[0] += 1
            x -= 1
        if state_count[0] > max_count:
            return float('nan')
        
        # start count right from center_y + 1 in center_y row
        x = center_x + 1
        while x < width and self.image[center_y][x] == 0: # count black
            state_count[2] += 1
            x += 1
        if x == width:
            return float('nan')
        while x < width and self.image[center_y][x] == 1 and state_count[3] < max_count: # count white
            state_count[3] += 1
            x += 1
        if x == width or state_count[3] >= max_count:
            return float('nan')
        while x < width and self.image[center_y][x] == 0 and state_count[4] < max_count: # count black
            state_count[4] += 1
            x += 1
        if state_count[4] >= max_count:
            return float('nan')
        
          # If the total state count differs by more than 40%, it's a false positive
        state_count_total = sum(state_count)
        if 5 * abs(state_count_total - original_state_count_total) >= 2 * original_state_count_total:
            return float('nan')

        # Check if it matches a finder pattern
        return self.center_from_end(state_count, x) if self.found_pattern_cross(state_count) else float('nan')


    def cross_check_diagonal(self, center_y, center_x):
        state_count = [0 for i in range(5)]
        
        # Start counting up, left from center 
        i = 0 
        while center_y >= i and center_x >= i and self.image[center_y - i][center_x - i] == 0: # count black
            state_count[2] += 1
            i += 1
        if state_count[2] == 0:
            return False
        while center_y >= i and center_x >= i and self.image[center_y - i][center_x - i] == 1: # count white
            state_count[1] += 1
            i += 1
        if state_count[1] == 0:
            return False
        while center_y >= i and center_x >= i and self.image[center_y - i][center_x - 1] == 0: # count black
            state_count[0] += 1
            i += 1
        if state_count[0] == 0:
            return False

        # Count down, right from center
        width = self.image.shape[1]
        height = self.image.shape[0]
        i = 1
        while center_y + i < height and center_x + i < width and self.image[center_y + i][center_x + i] == 0: # count black
            state_count[2] += 1
            i += 1
        while center_y + i < height and center_x + i < width and self.image[center_y + i][center_x + i] == 1: # count white
            state_count[3] += 1
            i += 1
        if state_count[3] == 0:
            return False
        while center_y + i < height and center_x + i < width and self.image[center_y + i][center_x + i] == 0: # count black
            state_count[4] += 1
            i += 1
        if state_count[4] == 0:
            return False
         
        return self.found_pattern_diagonal(state_count)
    

    def found_pattern_diagonal(self, state_count):
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
        center_width = self.center_from_end(state_count, j)
        center_height = self.cross_check_vertical(i, center_width, state_count[2], state_count_total)
        if center_height != float('nan'):
            # re-cross check 
            center_width = self.cross_check_horizontal(center_width, center_height, state_count[2], state_count_total)
            if center_width != float('nan'):
                if self.cross_check_diagonal(center_height, center_width):
                    estimated_module_size = state_count_total / 7.0
                    found = False
                    finder_pattern_count = len(self.possible_centers)

                    for i in range(0, finder_pattern_count):
                        center = self.possible_centers[i]
                        #Look for about the same center and module size:
                        if center.about_equals(estimated_module_size, center_height, center_width):
                            self.possible_centers[i] = center.combine_estimate(center_width, center_height, estimated_module_size)
                            found = True
                            break
                    
                    if found == False:
                        point = FinderPattern(center_width, center_height, estimated_module_size)
                        self.possible_centers.append(point)
                        # CALL BACK WILL BE IMPLEMENTED HERE
                    return True
            return False
        
    def have_multiply_confirmed_centers(self, possible_centers):
        confirmed_count = 0
        total_module_size = 0.0
        max = len(self.possible_centers)
        # Count confirmed centers and calculate total module size
        for pattern in possible_centers:
            if pattern.get_count() >= self.CENTER_QUORUM:
                confirmed_count += 1
                total_module_size += pattern.get_estimated_module_size()

        # If less than 3 confirmed centers, return False
        if confirmed_count < 3:
            return False

        # Calculate the average module size
        average = total_module_size / max

        # Calculate the total deviation from the average
        total_deviation = sum(
            abs(pattern.get_estimated_module_size() - average) for pattern in possible_centers
        )

        # Check if the total deviation is within 5% of the total module size
        return total_deviation <= 0.05 * total_module_size
    
    def find_row_skip(self):
        max = len(self.possible_centers)
        if max <= 1:
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
    
    def do_shift_count(self, state_count):
        state_count[0] = state_count[2]
        state_count[1] = state_count[3]
        state_count[2] = state_count[4]
        state_count[3] = 1
        state_count[4] = 0
        return state_count
    
    def squared_distance(self, a, b):
        x = a.get_x() - b.get_x()
        y = a.get_y() - b.get_y()
        return x * x + y * y
    
    def select_best_pattern(self):
        start_size = len(self.possible_centers)
        if start_size < 3:
            raise ValueError("Not enough finder patterns found")
        
        for it in self.possible_centers[:]:
            if it.get_count() < self.CENTER_QUORUM:
                self.possible_centers.remove(it)

        self.possible_centers.sort(key=self.module_comparator)

        distortion = float('inf')
        best_patterns = [None, None, None]


        for i in range(0, len(self.possible_centers) - 2):
            fpi = self.possible_centers[i]
            min_module_size = fpi.get_estimated_module_size()

            for j in range(i+1, j < len(self.possible_centers)):
                fpj = self.possible_centers[j]
                squares0 = self.squared_distance(fpi, fpj)

                for k in range(j+1, len(self.possible_centers)):
                    fpk = self.possible_centers[k]
                    max_module = fpk.get_estimated_module_size()
                    if max_module > max_module * 1.4:
                        continue

                    a = squares0
                    b = self.squared_distance(fpj, fpk)
                    c = self.squared_distance(fpi, fpk)

                    if a < b:
                        if b > c:
                            if a < c:
                                b, c = c, b
                            else:
                                a, b, c = c, b, a
                    else:
                        if b < c:
                            if a < c:
                                a, b = b, a
                            else:
                                a, b, c = b, c, a
                        else:
                            a, c = c, a
                    
                    d = abs(c - 2 * b) + abs(c - 2 * a)
                    if d < distortion:
                        distortion = d 
                        best_patterns[0] = fpi
                        best_patterns[1] = fpj
                        best_patterns[2] = fpk
        
        if distortion == float('inf'):
            raise ValueError("Not enough finder patterns found")
        
        return best_patterns

                    





        





        


        
        
        
        
    
    

    


