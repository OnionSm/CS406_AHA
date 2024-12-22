import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
__all__ = ["FormatExceeption"]

class FormatException(Exception):
    """
    Exception class used for QR Code format errors.
    This class is raised when there is an issue with the format or version of the QR code.
    """

    @staticmethod
    def get_format_instance():
        """
        Tạo và trả về một instance của FormatException.

        Input: Không có.
        Output: Trả về một instance của FormatException.
        """
        return FormatException("QR Code format error.")
