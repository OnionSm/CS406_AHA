import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

class NotFoundException(Exception):
    """Lớp ngoại lệ khi không tìm thấy QR code trong ảnh.

    Thừa kế từ lớp `Exception`, lớp này được sử dụng để báo lỗi khi không tìm thấy QR code
    trong ảnh và cần thông báo lỗi cụ thể.

    Attributes:
        message (str): Thông điệp lỗi chi tiết.
    """
    
    def __init__(self, message="Không tìm thấy QR code trong ảnh"):
        # Khởi tạo thông điệp lỗi
        self.message = message
        super().__init__(self.message)


