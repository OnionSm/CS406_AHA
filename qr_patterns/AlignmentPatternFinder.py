import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .AlignmentPattern import AlignmentPattern
from qrcode import BitMatrix
class AlignmentPatternFinder:
    def __init__(self, image, start_x, start_y, width, height, module_size, result_point_callback=None):
        """
        Creates a finder that will look in a portion of the whole image.
        :param image: 2D list or similar structure representing the binary image.
        :param start_x: left column from which to start searching.
        :param start_y: top row from which to start searching.
        :param width: width of region to search.
        :param height: height of region to search.
        :param module_size: estimated module size so far.
        :param result_point_callback: optional callback when a point is found.
        """
        self.image: BitMatrix = image
        self.possibleCenters = []
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.moduleSize = module_size
        self.crossCheckStateCount = [0, 0, 0]
        self.resultPointCallback = result_point_callback

    def find(self):
        start_x = self.start_x
        height = self.height
        max_j = start_x + self.width
        middle_i = self.start_y + (height // 2)
        state_count = [0, 0, 0]
        print("start x:", start_x)

        for iGen in range(height):
            i = middle_i + ((iGen & 0x01) == 0 and (iGen + 1) // 2 or -((iGen + 1) // 2))
            state_count = [0, 0, 0]
            j = start_x

            # Skip leading white pixels
            while j < max_j and not self.image.get(j,i):
                j += 1

            current_state = 0
            while j < max_j:
                if self.image.get(j,i): # black pixel
                    if current_state == 1:
                        state_count[1] += 1
                    else:
                        if current_state == 2: # have full state
                            if self.found_pattern_cross(state_count):
                                print("Aligment Found")
                                confirmed = self.handle_possible_center(state_count, i, j)
                                if confirmed is not None:
                                    return confirmed
                            state_count[0], state_count[1] = state_count[2], 1
                            state_count[2] = 0
                            current_state = 1
                        else:
                            current_state += 1
                            state_count[current_state] += 1
                else:
                    if current_state == 1:
                        current_state += 1
                    state_count[current_state] += 1
                j += 1

            if self.found_pattern_cross(state_count):
                confirmed = self.handle_possible_center(state_count, i, max_j)
                if confirmed:
                    return confirmed
        print("State", state_count)
        if len(self.possibleCenters) > 0:
            return self.possibleCenters[0]
        raise ValueError("Not Found")

    @staticmethod
    def center_from_end(state_count, end):
        return (end - state_count[2]) - state_count[1] / 2.0

    def found_pattern_cross(self, state_count):
        module_size = self.moduleSize
        max_variance = module_size / 2.0
        return all(abs(module_size - count) < max_variance for count in state_count)

    def cross_check_vertical(self, start_i, center_j, max_count, original_state_count_total):
        max_i = self.image.get_height()
        state_count = [0, 0, 0]
        i = start_i

        while i >= 0 and self.image.get(center_j, i) and state_count[1] <= max_count:
            state_count[1] += 1
            i -= 1

        if i < 0 or state_count[1] > max_count:
            return float('nan')

        while i >= 0 and not self.image.get(center_j, i) and state_count[0] <= max_count:
            state_count[0] += 1
            i -= 1

        if state_count[0] > max_count:
            return float('nan')

        i = start_i + 1
        while i < max_i and self.image.get(center_j, i) and state_count[1] <= max_count:
            state_count[1] += 1
            i += 1

        if i == max_i or state_count[1] > max_count:
            return float('nan')

        while i < max_i and not self.image.get(center_j, i) and state_count[2] <= max_count:
            state_count[2] += 1
            i += 1

        if state_count[2] > max_count:
            return float('nan')

        state_count_total = sum(state_count)
        if 5 * abs(state_count_total - original_state_count_total) >= 2 * original_state_count_total:
            return float('nan')

        return self.center_from_end(state_count, i) if self.found_pattern_cross(state_count) else float('nan')

    def handle_possible_center(self, state_count, i, j):
        state_count_total = sum(state_count)
        center_j = self.center_from_end(state_count, j)
        center_i = self.cross_check_vertical(i, int(center_j), 2 * state_count[1], state_count_total)
        if not (center_i != float('nan')):
            return None

        estimated_module_size = sum(state_count) / 3.0
        for center in self.possibleCenters:
            if center.aboutEquals(estimated_module_size, center_i, center_j):
                return center.combineEstimate(center_i, center_j, estimated_module_size)
        print("Aligment point", center_j, center_i, estimated_module_size)
        point = AlignmentPattern(center_j, center_i, estimated_module_size)
        self.possibleCenters.append(point)
        if self.resultPointCallback:
            self.resultPointCallback(point)
        return point
