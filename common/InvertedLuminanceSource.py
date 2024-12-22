from .LuminanceSource import LuminanceSource
class InvertedLuminanceSource(LuminanceSource):
    """
    Đây là một lớp wrapper cho lớp `LuminanceSource`, giúp đảo ngược độ sáng (luminance) 
    mà nó trả về. Màu đen sẽ trở thành trắng và ngược lại, giá trị độ sáng sẽ được tính 
    là (255 - giá trị).
    """

    def __init__(self, delegate):
        """
        Khởi tạo lớp InvertedLuminanceSource với đối tượng delegate, 
        là một thể hiện của LuminanceSource.
        
        :param delegate: Đối tượng LuminanceSource mà InvertedLuminanceSource sẽ bao bọc.
        """
        super().__init__(delegate.get_width(), delegate.get_height())
        self.delegate = delegate

    def get_row(self, y, row=None):
        """
        Lấy một dòng (row) của ma trận độ sáng, sau đó đảo ngược tất cả các giá trị độ sáng.
        
        :param y: Chỉ số dòng.
        :param row: Dữ liệu dòng (row) sẽ được trả về, nếu không sẽ tạo mới.
        :return: Một mảng byte chứa giá trị độ sáng đảo ngược của dòng.
        """
        row = self.delegate.get_row(y, row)
        for i in range(self.width):
            row[i] = 255 - (row[i] & 0xFF)  # Đảo ngược giá trị độ sáng
        return row

    def get_matrix(self):
        """
        Lấy toàn bộ ma trận độ sáng và đảo ngược tất cả các giá trị trong ma trận.
        
        :return: Một mảng byte chứa toàn bộ ma trận độ sáng đảo ngược.
        """
        matrix = self.delegate.get_matrix()
        length = self.width * self.height
        inverted_matrix = bytearray(length)
        for i in range(length):
            inverted_matrix[i] = 255 - (matrix[i] & 0xFF)  # Đảo ngược giá trị độ sáng
        return inverted_matrix

    def is_crop_supported(self):
        """
        Kiểm tra xem tính năng cắt (crop) có được hỗ trợ hay không.
        
        :return: True nếu cắt được hỗ trợ, False nếu không.
        """
        return self.delegate.is_crop_supported()

    def crop(self, left, top, width, height):
        """
        Cắt ma trận độ sáng theo các thông số cho trước và trả về một thể hiện mới 
        của InvertedLuminanceSource đã cắt.
        
        :param left: Vị trí bắt đầu từ bên trái.
        :param top: Vị trí bắt đầu từ trên cùng.
        :param width: Chiều rộng sau khi cắt.
        :param height: Chiều cao sau khi cắt.
        :return: Một thể hiện mới của InvertedLuminanceSource với phần cắt.
        """
        return InvertedLuminanceSource(self.delegate.crop(left, top, width, height))

    def is_rotate_supported(self):
        """
        Kiểm tra xem tính năng xoay có được hỗ trợ hay không.
        
        :return: True nếu xoay được hỗ trợ, False nếu không.
        """
        return self.delegate.is_rotate_supported()

    def invert(self):
        """
        Đảo ngược lại quá trình đảo ngược. Trả về đối tượng `LuminanceSource` ban đầu 
        vì đảo ngược lại chính nó sẽ mang lại kết quả giống như ban đầu.
        
        :return: Đối tượng LuminanceSource ban đầu mà không có sự đảo ngược.
        """
        return self.delegate

    def rotate_counter_clockwise(self):
        """
        Xoay ma trận độ sáng ngược chiều kim đồng hồ và trả về một thể hiện mới 
        của InvertedLuminanceSource sau khi xoay.
        
        :return: Một thể hiện mới của InvertedLuminanceSource đã xoay.
        """
        return InvertedLuminanceSource(self.delegate.rotate_counter_clockwise())

    def rotate_counter_clockwise_45(self):
        """
        Xoay ma trận độ sáng 45 độ ngược chiều kim đồng hồ và trả về một thể hiện mới 
        của InvertedLuminanceSource sau khi xoay.
        
        :return: Một thể hiện mới của InvertedLuminanceSource đã xoay 45 độ.
        """
        return InvertedLuminanceSource(self.delegate.rotate_counter_clockwise_45())
