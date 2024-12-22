import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .ResultPoint import ResultPoint


class AlignmentPattern(ResultPoint):
    """Represents an alignment pattern in a QR Code."""
    def __init__(self, pos_x: float, pos_y: float, estimated_module_size: float):
        super().__init__(pos_x, pos_y)
        self.estimated_module_size = estimated_module_size

    def about_equals(self, module_size: float, i: float, j: float) -> bool:
        """
        Determines if this alignment pattern is approximately equal to another
        based on position and module size.
        """
        if abs(i - self.y) <= module_size and abs(j - self.x) <= module_size:
            module_size_diff = abs(module_size - self.estimated_module_size)
            return module_size_diff <= 1.0 or module_size_diff <= self.estimated_module_size
        return False

    def combine_estimate(self, i: float, j: float, new_module_size: float):
        """
        Combines this pattern's position and module size with a new estimate
        and returns a new AlignmentPattern instance.
        """
        combined_x = (self.x + j) / 2.0
        combined_y = (self.y + i) / 2.0
        combined_module_size = (self.estimated_module_size + new_module_size) / 2.0
        return AlignmentPattern(combined_x, combined_y, combined_module_size)


# Example usage:
# pattern = AlignmentPattern(10.0, 20.0, 5.0)
# is_equal = pattern.about_equals(5.0, 21.0, 11.0)
# new_pattern = pattern.combine_estimate(21.0, 11.0, 6.0)
