import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
class QRCodeDecoderMetaData:
    """
    Lớp chứa thông tin meta-data cho việc giải mã QR Code. Các thể hiện của lớp này có thể được sử dụng 
    để truyền tải thông tin trở lại caller khi giải mã. Các caller cần xử lý thông tin này.
    """

    def __init__(self, mirrored: bool):
        """
        Khởi tạo một thể hiện của QRCodeDecoderMetaData.

        :param mirrored: bool - Trạng thái cho biết liệu QR code có bị lật gương hay không.
        """
        self.mirrored = mirrored

    def is_mirrored(self) -> bool:
        """
        Kiểm tra xem QR code có bị lật gương hay không.

        :return: bool - Trả về True nếu QR code bị lật gương, ngược lại trả về False.
        """
        return self.mirrored

    def apply_mirrored_correction(self, points: list) -> None:
        """
        Áp dụng chỉnh sửa thứ tự các điểm kết quả do lật gương.

        :param points: list - Mảng các điểm (ResultPoint) cần chỉnh sửa.
        :return: None - Hàm này sửa đổi mảng points trực tiếp nếu QR code bị lật gương.
        """
        if not self.mirrored or points is None or len(points) < 3:
            return
        
        # Hoán đổi điểm dưới bên trái và điểm trên bên phải
        bottom_left = points[0]
        points[0] = points[2]
        points[2] = bottom_left
        # Không cần phải chỉnh sửa điểm trên bên trái và điểm mẫu căn chỉnh.
