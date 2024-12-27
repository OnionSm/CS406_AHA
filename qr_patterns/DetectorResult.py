import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from qrcode import BitMatrix


class DetectorResult:
    """
    Encapsulates the result of detecting a barcode in an image. This includes the raw
    matrix of black/white pixels corresponding to the barcode, and possibly points of interest
    in the image, like the location of finder patterns or corners of the barcode in the image.
    """

    def __init__(self, bits, points):
        """
        :param bits: BitMatrix, representing the barcode image matrix.
        :param points: List[ResultPoint], points of interest in the image.
        """
        self.bits:BitMatrix  = bits
        self.points = points

    def get_bits(self):
        """
        Returns the BitMatrix containing the barcode.
        """
        return self.bits

    def get_points(self):
        """
        Returns the points of interest (e.g., corners or finder patterns).
        """
        return self.points
