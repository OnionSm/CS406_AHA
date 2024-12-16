import math
import ResultPoint


class FinderPattern(ResultPoint):
    def __init__(self, pos_x, pos_y, estimated_module_size, count=1):
        super().__init__(pos_x, pos_y)
        self.estimated_module_size = estimated_module_size
        self.count = count

    def get_estimated_module_size(self):
        return self.estimated_module_size

    def get_count(self):
        return self.count

    def about_equals(self, module_size, i, j):
        if abs(i - self.y) <= module_size and abs(j - self.x) <= module_size:
            module_size_diff = abs(module_size - self.estimated_module_size)
            return module_size_diff <= 1.0 or module_size_diff <= self.estimated_module_size
        return False

    def combine_estimate(self, i, j, new_module_size):
        combined_count = self.count + 1
        combined_x = (self.count * self.x + j) / combined_count
        combined_y = (self.count * self.y + i) / combined_count
        combined_module_size = (self.count * self.estimated_module_size + new_module_size) / combined_count
        return FinderPattern(combined_x, combined_y, combined_module_size, combined_count)
    
