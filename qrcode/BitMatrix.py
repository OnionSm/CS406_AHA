import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import numpy as np
from .BitArray import BitArray

class BitMatrix:
    """
    Property:
    - width: int 
    - height: int
    - row_size: int
    - bit: int []
    """
    def __init__(self, *args, **kwargs):
        """
        - *args == 1 : dimension : int 
        - *args == 2 : width, height: int 
        - *args == 4 : width, height, row_size, bit 

        Hàm này nhận vào số lượng đối số không dự đoán trước 
        Sử dụng tương tự như overloading ở trong Java
        """
        if len(args) == 1:
            # Nếu chỉ có 1 tham số, gán cả width và height
            self.width = self.height = args[0]
            self.row_size = (self.width + 31) // 32
            self.bits = np.zeros((self.height, self.width), dtype=int)
        
        elif len(args) == 2:
            # Nếu có 2 tham số, gán width và height
            self.width, self.height = args
            self.row_size = (self.width + 31) // 32
            self.bits = np.zeros((self.height, self.width), dtype=int)
        
        elif len(args) == 4:
            # Nếu có 4 tham số, gán width, height, row_size và bits
            self.width, self.height, self.row_size, bit = args
            if self.row_size < 1 or self.width < 1 or self.height < 1:
                raise ValueError("All dimensions and row_size must be greater than 0")
            self.bits = np.full((self.height, self.width), bit, dtype=int)
        
        elif "width" in kwargs and "height" in kwargs:
            # Nếu chiều rộng và chiều cao được truyền qua từ khóa
            self.width = kwargs["width"]
            self.height = kwargs["height"]
            self.row_size = (self.width + 31) // 32
            self.bits = np.zeros((self.height, self.width), dtype=int)
        
        else:
            raise ValueError("Invalid arguments for BitMatrix initialization")

        # Kiểm tra nếu chiều rộng hoặc chiều cao nhỏ hơn 1
        if self.width < 1 or self.height < 1:
            raise ValueError("Both dimensions must be greater than 0")


    @staticmethod
    def parse(image):
        """
        Hàm này nhận vào đối số là một ảnh numpy array 
        Sau đó khởi tạo một BitMatrix với các thuộc tính width, height, bitsbits
        """
        if not isinstance(image, np.ndarray):
            raise ValueError("Expected image to be a NumPy array")

        height, width = image.shape
        bit_matrix = BitMatrix(width, height)
        bit_matrix.bits = (image > 0).astype(int)  # Convert non-zero to 1
        return bit_matrix

    @staticmethod
    def from_string_to_bitmatrix(bit_string, on_value, off_value):
        """
        Chuyển đổi một chuỗi biểu diễn ma trận nhị phân thành một đối tượng ma trận.

        Hàm này chuyển chuỗi ký tự vào thành ma trận nhị phân, trong đó mỗi ký tự trong chuỗi 
        tương ứng với một giá trị `True` (1) hoặc `False` (0) trong ma trận. Các dòng trong 
        chuỗi được phân tách bằng ký tự phân cách dòng (`\n` hoặc `\r`).

        Parameters:
        bit_string (str): Chuỗi ký tự mô tả ma trận nhị phân, với các giá trị '1' (True) 
                        và '0' (False). Các dòng được phân tách bằng ký tự newline (`\n`) 
                        hoặc carriage return (`\r`).
        on_value (str): Chuỗi ký tự đại diện cho giá trị "bật" trong ma trận (thường là '1').
        off_value (str): Chuỗi ký tự đại diện cho giá trị "tắt" trong ma trận (thường là '0').

        Returns:
        Matrix: Một đối tượng ma trận chứa các giá trị `True` và `False` được tạo ra từ 
                chuỗi `bit_string`.
        """
        if bit_string is None:
            raise ValueError("bit_string cannot be None")

        # Sử dụng numpy array để lưu trữ các giá trị bit (True/False)
        bits = np.array([], dtype=bool)
        current_bit_position = 0
        row_start = 0
        row_length = -1
        row_count = 0
        index = 0

        while index < len(bit_string):
            if bit_string[index] in ['\n', '\r']:
                if current_bit_position > row_start:
                    if row_length == -1:
                        row_length = current_bit_position - row_start
                    elif current_bit_position - row_start != row_length:
                        raise ValueError("Row lengths do not match")
                    row_start = current_bit_position
                    row_count += 1
                index += 1
            elif bit_string.startswith(on_value, index):
                index += len(on_value)
                bits = np.append(bits, True)  # Thêm giá trị True vào numpy array
                current_bit_position += 1
            elif bit_string.startswith(off_value, index):
                index += len(off_value)
                bits = np.append(bits, False)  # Thêm giá trị False vào numpy array
                current_bit_position += 1
            else:
                raise ValueError(f"Illegal character encountered: {bit_string[index:]}")

        if current_bit_position > row_start:
            if row_length == -1:
                row_length = current_bit_position - row_start
            elif current_bit_position - row_start != row_length:
                raise ValueError("Row lengths do not match")
            row_count += 1

        # Tạo đối tượng ma trận từ numpy array
        result_matrix = BitMatrix(row_length, row_count)
        for i in range(current_bit_position):
            if bits[i]:
                result_matrix.set_value(i % row_length, i // row_length)

        return result_matrix
    
    def get(self, x, y):
        """
        Trả về giá trị bit tại vị trí (x, y) trong ma trận.
        """
        return self.bits[y, x]

    def set(self, x, y):
        """
        Đặt bit tại vị trí (x, y) thành true (1).
        """
        self.bits[y, x] = 1

    def unset(self, x, y):
        """
        Đặt bit tại vị trí (x, y) thành false (0).
        """
        self.bits[y, x] = 0

    def flip(self, x, y):
        """
        Đảo ngược giá trị bit tại vị trí (x, y).
        """
        # Sử dụng toán tử XOR để đảo ngược bit tại vị trí (x, y)
        self.bits[y, x] ^= 1  # XOR với 1 để đảo ngược bit (0 -> 1, 1 -> 0)

    def flip_all(self):
        """
        Đảo ngược mọi bit trong ma trận.
        """
        # Đảo ngược tất cả các bit trong ma trận
        self.bits = np.bitwise_not(self.bits)  # Dùng toán tử ~ để đảo ngược các bit

    def xor(self, mask):
        """
        Thực hiện phép XOR giữa ma trận này và một ma trận khác.
        """
        # Kiểm tra kích thước ma trận có khớp không
        if self.width != mask.width or self.height != mask.height or self.row_size != mask.row_size:
            raise ValueError("input matrix dimensions do not match")

        # Thực hiện phép XOR giữa từng phần tử trong ma trận
        self.bits ^= mask.bits
        
    def clear(self):
        """
        Xóa tất cả các bit (đặt tất cả các bit thành false).
        """
        for i in range(len(self.bits)):
            self.bits[i] = 0

    def set_region(self, left, top, width, height):
        """
        Thiết lập một vùng trong ma trận (đặt tất cả các bit trong vùng này thành 1).
        
        Parameters:
        - left: vị trí cột bắt đầu.
        - top: vị trí dòng bắt đầu.
        - width: chiều rộng của vùng.
        - height: chiều cao của vùng.
        """
        if top < 0 or left < 0:
            raise ValueError("Left and top must be nonnegative")
        if height < 1 or width < 1:
            raise ValueError("Height and width must be at least 1")

        right = left + width
        bottom = top + height
        if bottom > self.height or right > self.width:
            raise ValueError("The region must fit inside the matrix")

        for y in range(top, bottom):
            offset = y * self.row_size
            for x in range(left, right):
                self.bits[offset + (x // 32)] |= 1 << (x & 0x1f)
    def get_row(self, y, row):
        """
        Input: 
        - y : int
        - row : BitArray
        """
        if row is None or row.get_size() < self.width:
            row = BitArray(self.width)
        else:
            row.clear()
        
        offset = y * self.row_size
        for x in range(self.row_size):
            row.set_bulk(x * 32, self.bit[offset + x])
        
        return row


    def set_row(self, y, row):
        """
        Hàm này sao chép nội dung của `row` vào `self.bits` tại vị trí offset tương ứng với `y`.

        :param y: chỉ số hàng cần thiết lập
        :param row: đối tượng BitArray chứa giá trị cần sao chép
        """
        self.bits[y * self.row_size : (y + 1) * self.row_size] = row.get_bit_array()
            
    def rotate(self, degrees):
        """
        Xoay ma trận bit theo góc được chỉ định.

        Tham số đầu vào:
        - degrees (int): Góc xoay của ma trận. Nó phải là bội số của 90 (0, 90, 180 hoặc 270).

        Hành vi:
        - Nếu góc là 0, ma trận không thay đổi.
        - Nếu góc là 90, ma trận sẽ được xoay 90 độ theo chiều kim đồng hồ.
        - Nếu góc là 180, ma trận sẽ được xoay 180 độ.
        - Nếu góc là 270, ma trận sẽ được xoay 270 độ (tương đương với việc xoay 90 độ ba lần).
        
        Ngoại lệ:
        - ValueError: Nếu góc không phải là bội số của 90.
        """
        degrees = degrees % 360
        if degrees == 0:
            return
        elif degrees == 90:
            self.rotate90()
        elif degrees == 180:
            self.rotate180()
        elif degrees == 270:
            self.rotate90()
            self.rotate180()
        else:
            raise ValueError("degrees must be a multiple of 0, 90, 180, or 270")

    def rotate180(self):
        """"
        Xoay ma trận bit 180 độ.

        Tham số đầu vào:
        - Không có tham số đầu vào.

        Hành vi:
        - Ma trận sẽ bị đảo ngược theo chiều hàng, và mỗi hàng sẽ bị đảo ngược trong chính nó.

        Thay đổi:
        - Ma trận hiện tại sẽ được thay đổi để đại diện cho ma trận bit xoay 180 độ.
        """
        top_row = [0] * self.width
        bottom_row = [0] * self.width
        max_height = (self.height + 1) // 2

        for i in range(max_height):
            top_row = self.get_row(i, top_row)
            bottom_row_index = self.height - 1 - i
            bottom_row = self.get_row(bottom_row_index, bottom_row)

            # Reverse the rows
            top_row.reverse()
            bottom_row.reverse()

            self.set_row(i, bottom_row)
            self.set_row(bottom_row_index, top_row)

    def rotate90(self):
        """
        Xoay ma trận bit 90 độ theo chiều ngược kim đồng hồ.
        """
        # Sử dụng numpy để xoay ma trận 90 độ
        self.bits = np.rot90(self.bits, k=1)  # k=1 xoay 90 độ ngược kim đồng hồ

        # Cập nhật chiều cao và chiều rộng sau khi xoay
        self.height, self.width = self.bits.shape

    def get_enclosing_rectangle(self):
        """
        Tìm và trả về hình chữ nhật bao quanh ma trận bit, được xác định bởi các điểm 
        có bit '1'. Nếu ma trận là trắng (chỉ chứa bit '0'), trả về None.

        Trả về:
        - list[int]: [left, top, width, height] đại diện cho hình chữ nhật bao quanh,
        hoặc None nếu không tìm thấy bit '1'.
        """
        # Tìm các vị trí (y, x) của bit '1' trong ma trận
        positions = np.argwhere(self.bits == 1)

        # Nếu không tìm thấy bất kỳ bit '1' nào, trả về None
        if positions.size == 0:
            return None

        # Xác định tọa độ bao quanh
        top = np.min(positions[:, 0])    # Dòng trên cùng
        bottom = np.max(positions[:, 0])  # Dòng dưới cùng
        left = np.min(positions[:, 1])   # Cột bên trái
        right = np.max(positions[:, 1])  # Cột bên phải

        # Tính chiều rộng và chiều cao
        width = right - left + 1
        height = bottom - top + 1

        return [left, top, width, height]
    
    
    def get_top_left_on_bit(self):
        """
        Tìm và trả về tọa độ x, y của bit '1' ở góc trên bên trái của ma trận. 
        Nếu không có bit '1', trả về None.

        Trả về:
        - list[int] : [x, y] đại diện cho tọa độ của bit '1' đầu tiên ở góc trên bên trái,
          hoặc None nếu ma trận không có bit '1'.
        """
        bits_offset = 0
        while bits_offset < len(self.bits) and self.bits[bits_offset] == 0:
            bits_offset += 1
        if bits_offset == len(self.bits):
            return None
        y = bits_offset // self.row_size
        x = (bits_offset % self.row_size) * 32

        the_bits = self.bits[bits_offset]
        bit = 0
        while (the_bits << (31 - bit)) == 0:
            bit += 1
        x += bit
        return [x, y]

    def get_bottom_right_on_bit(self):
        """
        Tìm và trả về tọa độ x, y của bit '1' ở góc dưới bên phải của ma trận. 
        Nếu không có bit '1', trả về None.

        Trả về:
        - list[int] : [x, y] đại diện cho tọa độ của bit '1' đầu tiên ở góc dưới bên phải,
          hoặc None nếu ma trận không có bit '1'.
        """
        bits_offset = len(self.bits) - 1
        while bits_offset >= 0 and self.bits[bits_offset] == 0:
            bits_offset -= 1
        if bits_offset < 0:
            return None

        y = bits_offset // self.row_size
        x = (bits_offset % self.row_size) * 32

        the_bits = self.bits[bits_offset]
        bit = 31
        while (the_bits >> bit) == 0:
            bit -= 1
        x += bit

        return [x, y]
    def get_width(self):
        """
        Trả về chiều rộng của ma trận.
        
        Trả về:
        - int: chiều rộng của ma trận.
        """
        return self.width

    def get_height(self):
        """
        Trả về chiều cao của ma trận.
        
        Trả về:
        - int: chiều cao của ma trận.
        """
        return self.height

    def get_row_size(self):
        """
        Trả về kích thước mỗi hàng trong ma trận (số lượng số nguyên trong mỗi hàng).
        
        Trả về:
        - int: kích thước của mỗi hàng.
        """
        return self.row_size

    def __eq__(self, other):
        """
        Kiểm tra xem hai ma trận có bằng nhau hay không.
        
        Trả về:
        - bool: True nếu hai ma trận có cùng kích thước và giá trị bits, False nếu không.
        """
        if not isinstance(other, BitMatrix):
            return False
        return (self.width == other.width and
                self.height == other.height and
                self.row_size == other.row_size and
                self.bits == other.bits)

    def __hash__(self):
        """
        Trả về mã băm của ma trận, được sử dụng cho việc so sánh và lưu trữ.
        
        Trả về:
        - int: mã băm của ma trận.
        """
        hash_value = self.width
        hash_value = 31 * hash_value + self.width
        hash_value = 31 * hash_value + self.height
        hash_value = 31 * hash_value + self.row_size
        hash_value = 31 * hash_value + hash(self.bits)
        return hash_value

    def __str__(self):
        """
        Trả về chuỗi đại diện của ma trận sử dụng "X" cho các bit đã đặt và " " cho các bit chưa đặt.
        
        Trả về:
        - str: chuỗi đại diện của ma trận.
        """
        return self.to_string("X ", "  ")

    def to_string(self, set_string, unset_string):
        """
        Trả về chuỗi đại diện của ma trận với các ký tự đại diện cho bit đã đặt và chưa đặt.
        
        Trả về:
        - str: chuỗi đại diện của ma trận.
        """
        return self.build_to_string(set_string, unset_string, "\n")

    def build_to_string(self, set_string, unset_string, line_separator):
        """
        Xây dựng chuỗi đại diện của ma trận với các ký tự đại diện cho bit đã đặt và chưa đặt, 
        và ngắt dòng theo separator đã cho.
        
        Trả về:
        - str: chuỗi đại diện của ma trận.
        """
        result = []
        for y in range(self.height):
            for x in range(self.width):
                result.append(set_string if self.get(x, y) else unset_string)
            result.append(line_separator)
        return ''.join(result)

    def clone(self):
        """
        Tạo một bản sao của ma trận hiện tại.
        
        Trả về:
        - BitMatrix: một bản sao của ma trận hiện tại.
        """
        return BitMatrix(self.width, self.height, self.row_size, self.bits[:])

