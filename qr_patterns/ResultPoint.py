import math
import struct

class ResultPoint:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def __eq__(self, other):
        if isinstance(other, ResultPoint):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return 31 * float_to_int_bits(self.x) + float_to_int_bits(self.y)

    def __str__(self):
        return f"({self.x},{self.y})"

    @staticmethod
    def order_best_patterns(patterns):
        # Find distances between pattern centers
        zero_one_distance = ResultPoint.distance(patterns[0], patterns[1])
        one_two_distance = ResultPoint.distance(patterns[1], patterns[2])
        zero_two_distance = ResultPoint.distance(patterns[0], patterns[2])

        # Assume one closest to other two is B; A and C will just be guesses at first
        if one_two_distance >= zero_one_distance and one_two_distance >= zero_two_distance:
            pointB, pointA, pointC = patterns[0], patterns[1], patterns[2]
        elif zero_two_distance >= one_two_distance and zero_two_distance >= zero_one_distance:
            pointB, pointA, pointC = patterns[1], patterns[0], patterns[2]
        else:
            pointB, pointA, pointC = patterns[2], patterns[0], patterns[1]

        # Use cross product to figure out whether A and C are correct or flipped
        if ResultPoint.cross_product_z(pointA, pointB, pointC) < 0.0:
            pointA, pointC = pointC, pointA

        patterns[0], patterns[1], patterns[2] = pointA, pointB, pointC

    @staticmethod
    def distance(pattern1, pattern2):
        return math.sqrt((pattern1.x - pattern2.x) ** 2 + (pattern1.y - pattern2.y) ** 2)

    @staticmethod
    def cross_product_z(pointA, pointB, pointC):
        bX = pointB.x
        bY = pointB.y
        return (pointC.x - bX) * (pointA.y - bY) - (pointC.y - bY) * (pointA.x - bX)

def float_to_int_bits(f):
    # Convert float to its binary representation (mimicking Java's Float.floatToIntBits)
    return int.from_bytes(struct.pack('>f', f), byteorder='big')
