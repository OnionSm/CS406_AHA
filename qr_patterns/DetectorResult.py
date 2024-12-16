



class DetectorResult:
    def __init__(self, bits, points):
        """
        Input: bits (Image), points (ResultPoint [])
        """
        self._bits = bits
        self._points = points

    @property
    def bits(self):
        """
        Returns the bit matrix (similar to BitMatrix).
        :return: The bit matrix.
        """
        return self._bits  # Image numpy array

    @property
    def points(self):
        """
        Returns the result points (similar to ResultPoint[]).
        :return: The result points.
        """
        return self._points # ResultPoint
