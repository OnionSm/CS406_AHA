from abc import ABC, abstractmethod

class LuminanceSource(ABC):
    """
    Lớp cơ sở nhằm trừu tượng hóa các triển khai bitmap khác nhau trên các nền tảng.
    Cung cấp giao diện chuẩn để yêu cầu các giá trị độ chói xám (luminance).
    Giao diện này chỉ cung cấp các phương thức bất biến, vì vậy việc cắt (crop)
    và xoay tạo ra các bản sao mới để đảm bảo rằng một Reader không làm thay đổi
    trạng thái gốc của nguồn độ chói.
    """

    def __init__(self, width, height):
        """
        Khởi tạo lớp với chiều rộng và chiều cao của bitmap.

        :param width: Chiều rộng của bitmap.
        :param height: Chiều cao của bitmap.
        """
        self.width = width
        self.height = height

    @abstractmethod
    def get_row(self, y, row=None):
        """
        Lấy một hàng dữ liệu độ chói từ bitmap.

        :param y: Chỉ số hàng, phải nằm trong [0, get_height()).
        :param row: Mảng được cấp phát trước (tùy chọn). Nếu không có hoặc quá nhỏ, sẽ bị bỏ qua.
        :return: Mảng chứa dữ liệu độ chói.
        """
        pass

    @abstractmethod
    def get_matrix(self):
        """
        Lấy dữ liệu độ chói của toàn bộ bitmap theo thứ tự dòng-chính (row-major).

        :return: Mảng chứa dữ liệu độ chói theo thứ tự dòng-chính.
        """
        pass

    def get_width(self):
        """
        Trả về chiều rộng của bitmap.
        """
        return self.width


    def get_height(self):
        """
        Trả về chiều cao của bitmap.
        """
        return self.height

    def is_crop_supported(self):
        """
        Kiểm tra xem lớp con có hỗ trợ cắt (crop) hay không.

        :return: False theo mặc định.
        """
        return False

    def crop(self, left, top, width, height):
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh đã cắt.
        Chỉ khả dụng nếu `is_crop_supported()` trả về True.

        :param left: Tọa độ trái, phải nằm trong [0, get_width()).
        :param top: Tọa độ trên, phải nằm trong [0, get_height()).
        :param width: Chiều rộng của vùng cần cắt.
        :param height: Chiều cao của vùng cần cắt.
        :return: Đối tượng mới chứa dữ liệu hình ảnh đã cắt.
        :raises: NotImplementedError nếu không được hỗ trợ.
        """
        raise NotImplementedError("Nguồn độ chói này không hỗ trợ cắt.")

    def is_rotate_supported(self):
        """
        Kiểm tra xem lớp con có hỗ trợ xoay ngược chiều kim đồng hồ hay không.

        :return: False theo mặc định.
        """
        return False

    def invert(self):
        """
        Trả về một đối tượng bao bọc (`wrapper`) của nguồn độ chói này, trong đó các giá trị độ chói bị đảo ngược
        (đen trở thành trắng và ngược lại).

        :return: Đối tượng đã được đảo ngược.
        """
        return InvertedLuminanceSource(self)

    def rotate_counter_clockwise(self):
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh xoay 90 độ ngược chiều kim đồng hồ.
        Chỉ khả dụng nếu `is_rotate_supported()` trả về True.

        :return: Đối tượng mới chứa dữ liệu hình ảnh đã xoay.
        :raises: NotImplementedError nếu không được hỗ trợ.
        """
        raise NotImplementedError("Nguồn độ chói này không hỗ trợ xoay 90 độ.")

    def rotate_counter_clockwise_45(self):
        """
        Trả về một đối tượng mới với dữ liệu hình ảnh xoay 45 độ ngược chiều kim đồng hồ.
        Chỉ khả dụng nếu `is_rotate_supported()` trả về True.

        :return: Đối tượng mới chứa dữ liệu hình ảnh đã xoay.
        :raises: NotImplementedError nếu không được hỗ trợ.
        """
        raise NotImplementedError("Nguồn độ chói này không hỗ trợ xoay 45 độ.")

    def __str__(self):
        """
        Trả về chuỗi đại diện cho dữ liệu độ chói dưới dạng các ký tự:
        - `#` cho các giá trị rất tối.
        - `+` cho các giá trị trung bình.
        - `.` cho các giá trị sáng hơn.
        - ` ` cho các giá trị rất sáng.

        :return: Chuỗi đại diện cho dữ liệu độ chói.
        """
        result = []
        for y in range(self.height):
            row = self.get_row(y)
            line = []
            for x in range(self.width):
                luminance = row[x] & 0xFF
                if luminance < 0x40:
                    line.append('#')
                elif luminance < 0x80:
                    line.append('+')
                elif luminance < 0xC0:
                    line.append('.')
                else:
                    line.append(' ')
            result.append(''.join(line))
        return '\n'.join(result)

class InvertedLuminanceSource(LuminanceSource):
    """
    Lớp bao bọc (`wrapper`) để đảo ngược giá trị độ chói từ nguồn gốc.
    """

    def __init__(self, source):
        """
        Khởi tạo lớp với nguồn độ chói ban đầu.

        :param source: Đối tượng LuminanceSource ban đầu.
        """
        super().__init__(source.width, source.height)
        self._source = source

    def get_row(self, y, row=None):
        """
        Lấy một hàng dữ liệu độ chói đã đảo ngược.

        :param y: Chỉ số hàng, phải nằm trong [0, get_height()).
        :param row: Mảng được cấp phát trước (tùy chọn).
        :return: Mảng chứa dữ liệu độ chói đã đảo ngược.
        """
        original_row = self._source.get_row(y, row)
        return [255 - value for value in original_row]

    def get_matrix(self):
        """
        Lấy toàn bộ dữ liệu độ chói đã đảo ngược theo thứ tự dòng-chính.

        :return: Mảng chứa dữ liệu độ chói đã đảo ngược.
        """
        original_matrix = self._source.get_matrix()
        return [255 - value for value in original_matrix]
