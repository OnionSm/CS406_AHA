import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

class PerspectiveTransform:
    def __init__(self, a11, a21, a31, a12, a22, a32, a13, a23, a33):
        self.a11 = a11
        self.a12 = a12
        self.a13 = a13
        self.a21 = a21
        self.a22 = a22
        self.a23 = a23
        self.a31 = a31
        self.a32 = a32
        self.a33 = a33

    @staticmethod
    def quadrilateral_to_quadrilateral(x0, y0, x1, y1, x2, y2, x3, y3, x0p, y0p, x1p, y1p, x2p, y2p, x3p, y3p):
        q_to_s = PerspectiveTransform.quadrilateral_to_square(x0, y0, x1, y1, x2, y2, x3, y3)
        s_to_q = PerspectiveTransform.square_to_quadrilateral(x0p, y0p, x1p, y1p, x2p, y2p, x3p, y3p)
        return s_to_q.times(q_to_s)

    def transform_points(self, points):
        max_i = len(points) - 1  # points must have an even length
        for i in range(0, max_i, 2):
            x = points[i]
            y = points[i + 1]
            denominator = self.a13 * x + self.a23 * y + self.a33
            points[i] = (self.a11 * x + self.a21 * y + self.a31) / denominator
            points[i + 1] = (self.a12 * x + self.a22 * y + self.a32) / denominator

    def transform_points_separate(self, x_values, y_values):
        n = len(x_values)
        for i in range(n):
            x = x_values[i]
            y = y_values[i]
            denominator = self.a13 * x + self.a23 * y + self.a33
            x_values[i] = (self.a11 * x + self.a21 * y + self.a31) / denominator
            y_values[i] = (self.a12 * x + self.a22 * y + self.a32) / denominator

    @staticmethod
    def square_to_quadrilateral(x0, y0, x1, y1, x2, y2, x3, y3):
        dx3 = x0 - x1 + x2 - x3
        dy3 = y0 - y1 + y2 - y3
        if dx3 == 0.0 and dy3 == 0.0:
            return PerspectiveTransform(
                x1 - x0, x2 - x1, x0,
                y1 - y0, y2 - y1, y0,
                0.0, 0.0, 1.0
            )
        else:
            dx1 = x1 - x2
            dx2 = x3 - x2
            dy1 = y1 - y2
            dy2 = y3 - y2
            denominator = dx1 * dy2 - dx2 * dy1
            a13 = (dx3 * dy2 - dx2 * dy3) / denominator
            a23 = (dx1 * dy3 - dx3 * dy1) / denominator 
            return PerspectiveTransform(
                x1 - x0 + a13 * x1, x3 - x0 + a23 * x3, x0,
                y1 - y0 + a13 * y1, y3 - y0 + a23 * y3, y0,
                a13, a23, 1.0
            )

    @staticmethod
    def quadrilateral_to_square(x0, y0, x1, y1, x2, y2, x3, y3):
        return PerspectiveTransform.square_to_quadrilateral(x0, y0, x1, y1, x2, y2, x3, y3).build_adjoint()

    def build_adjoint(self):
        return PerspectiveTransform(
            self.a22 * self.a33 - self.a23 * self.a32,
            self.a23 * self.a31 - self.a21 * self.a33,
            self.a21 * self.a32 - self.a22 * self.a31,
            self.a13 * self.a32 - self.a12 * self.a33,
            self.a11 * self.a33 - self.a13 * self.a31,
            self.a12 * self.a31 - self.a11 * self.a32,
            self.a12 * self.a23 - self.a13 * self.a22,
            self.a13 * self.a21 - self.a11 * self.a23,
            self.a11 * self.a22 - self.a12 * self.a21
        )

    def times(self, other):
        return PerspectiveTransform(
            self.a11 * other.a11 + self.a21 * other.a12 + self.a31 * other.a13,
            self.a11 * other.a21 + self.a21 * other.a22 + self.a31 * other.a23,
            self.a11 * other.a31 + self.a21 * other.a32 + self.a31 * other.a33,
            self.a12 * other.a11 + self.a22 * other.a12 + self.a32 * other.a13,
            self.a12 * other.a21 + self.a22 * other.a22 + self.a32 * other.a23,
            self.a12 * other.a31 + self.a22 * other.a32 + self.a32 * other.a33,
            self.a13 * other.a11 + self.a23 * other.a12 + self.a33 * other.a13,
            self.a13 * other.a21 + self.a23 * other.a22 + self.a33 * other.a23,
            self.a13 * other.a31 + self.a23 * other.a32 + self.a33 * other.a33
        )
