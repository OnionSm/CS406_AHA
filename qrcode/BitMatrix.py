import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import numpy as np
from .BitArray import BitArray

class BitMatrix():
    """
    Property:
    - width: int 
    - height: int
    - row_size: int
    - bit: int []
    """
    def __init__(self, *args):
        """
        - *args == 1: dimension : int
        - *args == 2: width, height : int
        - *args == 4: width, height, row_size, bit
        
        Hàm này nhận vào số lượng đối số không dự đoán trước, sử dụng như overloading trong Java
        """
        if len(args) == 1:
            # Nếu chỉ có 1 tham số, gán cả width và height
            self.width = self.height = args[0]
            self.row_size = (self.width + 31) // 32
            self.bits = np.zeros(self.row_size * self.height, dtype=np.uint32)
        
        elif len(args) == 2:
            # Nếu có 2 tham số, gán width và height
            self.width, self.height = args
            self.row_size = (self.width + 31) // 32
            self.bits = np.zeros(self.row_size * self.height, dtype=np.uint32)
        
        elif len(args) == 4:
            # Nếu có 4 tham số, gán width, height, row_size và bit
            self.width, self.height, self.row_size, bit = args
            if self.row_size < 1 or self.width < 1 or self.height < 1:
                raise ValueError("All dimensions and row_size must be greater than 0")
            self.bits = np.full(self.row_size * self.height, bit, dtype=np.uint32)
        else:
            raise ValueError("Invalid arguments for BitMatrix initialization")

        # Kiểm tra nếu chiều rộng hoặc chiều cao nhỏ hơn 1
        if self.width < 1 or self.height < 1:
            raise ValueError("Both dimensions must be greater than 0")
        

    @staticmethod
    def parse(image):
        """
        Phương thức này chuyển đổi một mảng ảnh 2D kiểu boolean (image) thành một đối tượng BitMatrix.
        
        - `image`: Mảng 2D kiểu boolean, mỗi phần tử trong mảng đại diện cho một pixel trong ảnh,
          với giá trị `True` tương ứng với màu sáng (bit 1) và `False` tương ứng với màu tối (bit 0).
        
        Quy trình thực hiện:
        - Tính toán chiều cao và chiều rộng của ảnh từ mảng `image`.
        - Tạo một đối tượng BitMatrix với kích thước chiều cao và chiều rộng của ảnh.
        - Duyệt qua từng pixel trong ảnh và nếu pixel có giá trị `True` (màu sáng), đặt bit tại vị trí tương ứng trong BitMatrix thành 1.
        
        Trả về:
        - Đối tượng `BitMatrix` đã được khởi tạo và các bit được thiết lập từ mảng ảnh.
        """
        height = len(image)
        width = len(image[0])
        bits = BitMatrix(width, height)
        
        for i in range(height):
            image_row = image[i]
            for j in range(width):
                if image_row[j]:
                    bits.set_bit(i, j, 1)  # Đặt bit 1 tại vị trí (i, j)
        
        return bits
    

    @staticmethod
    def parse_2(string_representation, set_string, unset_string):
        """
        Phương thức này chuyển đổi một chuỗi đại diện của ma trận thành một đối tượng BitMatrix.
        
        - `string_representation`: Chuỗi biểu diễn ma trận, trong đó các giá trị của ma trận được mã hóa
          dưới dạng các chuỗi con `set_string` (để đại diện cho giá trị bit 1) và `unset_string` (để đại diện
          cho giá trị bit 0). Mỗi giá trị trong ma trận được phân cách bởi ký tự xuống dòng (`\n` hoặc `\r`).
        - `set_string`: Chuỗi dùng để đại diện cho giá trị bit 1.
        - `unset_string`: Chuỗi dùng để đại diện cho giá trị bit 0.

        Quy trình thực hiện:
        - Duyệt qua chuỗi `string_representation` và xác định các giá trị bit (1 hoặc 0) dựa trên các chuỗi `set_string` và `unset_string`.
        - Kiểm tra chiều dài các dòng trong ma trận để đảm bảo tất cả các dòng có độ dài bằng nhau.
        - Tạo một đối tượng `BitMatrix` với kích thước dựa trên chiều dài các dòng và số lượng dòng trong chuỗi.
        - Thiết lập các bit trong đối tượng `BitMatrix` theo thứ tự các giá trị trong chuỗi.

        Trả về:
        - Đối tượng `BitMatrix` đã được khởi tạo và các bit được thiết lập theo chuỗi đầu vào.
        """
        if string_representation is None:
            raise ValueError("Chuỗi đầu vào không thể là None")
        
        bits = []
        row_start_pos = 0
        row_length = -1
        n_rows = 0
        pos = 0

        while pos < len(string_representation):
            if string_representation[pos] in ['\n', '\r']:  # Dòng mới
                if len(bits) > row_start_pos:
                    if row_length == -1:
                        row_length = len(bits) - row_start_pos
                    elif len(bits) - row_start_pos != row_length:
                        raise ValueError("Chiều dài các dòng không khớp")
                    row_start_pos = len(bits)
                    n_rows += 1
                pos += 1
            elif string_representation.startswith(set_string, pos):
                pos += len(set_string)
                bits.append(True)
            elif string_representation.startswith(unset_string, pos):
                pos += len(unset_string)
                bits.append(False)
            else:
                raise ValueError(f"Nhân diện ký tự không hợp lệ: {string_representation[pos:]}")
        
        # Kiểm tra nếu không có EOL ở cuối chuỗi
        if len(bits) > row_start_pos:
            if row_length == -1:
                row_length = len(bits) - row_start_pos
            elif len(bits) - row_start_pos != row_length:
                raise ValueError("Chiều dài các dòng không khớp")
            n_rows += 1

        # Tạo đối tượng BitMatrix và thiết lập các bit
        matrix = BitMatrix(row_length, n_rows)
        for i, bit in enumerate(bits):
            if bit:
                matrix.set_bit(i % row_length, i // row_length, True)
        
        return matrix

    
    def get(self, x, y):
        """
        Lấy giá trị bit tại vị trí (x, y) trong ma trận.
        
        - `x`: Cột (hàng ngang).
        - `y`: Dòng (hàng dọc).
        
        Trả về:
        - Giá trị của bit tại vị trí (x, y), True nếu là 1, False nếu là 0.
        """
        x = np.uint32(x)
        offset = int(y * self.row_size + (x // 32))
        return (self.bits[offset] >> (x & 0x1f)) & 1 != 0

    def set(self, x, y):
        """
        Đặt bit tại vị trí (x, y) thành 1 (true).
        
        - `x`: Cột (hàng ngang).
        - `y`: Dòng (hàng dọc).
        """
       
        offset = y * self.row_size + (x // 32)
        self.bits[offset] |= 1 << (x & 0x1f)
        
    def unset(self, x, y):
        """
        Đặt bit tại vị trí (x, y) thành 0 (false).
        
        - `x`: Cột (hàng ngang).
        - `y`: Dòng (hàng dọc).
        """
        offset = y * self.row_size + (x // 32)
        self.bits[offset] &= ~(1 << (x & 0x1f))

    def flip(self, x, y):
        """
        Lật (đảo ngược) giá trị bit tại vị trí (x, y).
        
        - `x`: Cột (hàng ngang).
        - `y`: Dòng (hàng dọc).
        """
        offset = y * self.row_size + (x // 32)
        self.bits[offset] ^= 1 << (x & 0x1f)


    def flip_all(self):
        """
        Lật (đảo ngược) mọi bit trong ma trận.
        """
        max_bits = len(self.bits)
        for i in range(max_bits):
            self.bits[i] = ~self.bits[i]

    def xor(self, mask):
        """
        Thực hiện phép XOR giữa ma trận hiện tại và một ma trận khác.
        
        - `mask`: Ma trận BitMatrix dùng làm mặt nạ XOR.
        
        Lưu ý: Kích thước của hai ma trận phải giống nhau.
        """
        if self.width != mask.width or self.height != mask.height or self.row_size != mask.row_size:
            raise ValueError("Kích thước của các ma trận không khớp")
        
        for y in range(self.height):
            offset = y * self.row_size
            for x in range(self.row_size):
                self.bits[offset + x] ^= mask.bits[offset + x]

    def clear(self):
        """
        Xóa tất cả các bit trong ma trận (đặt tất cả các bit về false).
        """
        self.bits.fill(0)


    def set_region(self, left, top, width, height):
        """
        Hàm này đặt giá trị của một vùng vuông trong ma trận bit thành true (1).
        
        - left: Vị trí ngang bắt đầu (bao gồm).
        - top: Vị trí dọc bắt đầu (bao gồm).
        - width: Chiều rộng của vùng.
        - height: Chiều cao của vùng.
        
        Các kiểm tra được thực hiện:
        - Vị trí left và top phải không âm.
        - Chiều rộng và chiều cao phải lớn hơn hoặc bằng 1.
        - Vùng phải nằm hoàn toàn trong ma trận.
        """
        if top < 0 or left < 0:
            raise ValueError("Left and top must be nonnegative")
        if height < 1 or width < 1:
            raise ValueError("Height and width must be at least 1")
        
        right = left + width
        bottom = top + height
        
        # Kiểm tra nếu vùng nằm trong giới hạn của ma trận
        if bottom > self.height or right > self.width:
            raise ValueError("The region must fit inside the matrix")
        
        # Đặt giá trị bit thành 1 cho mỗi ô trong vùng
        for y in range(top, bottom):
            offset = y * self.row_size
            for x in range(left, right):
                self.bits[offset + (x // 32)] |= 1 << (x & 0x1f)



    def get_row(self, y, row=None):
        """
        Phương thức nhanh để lấy một hàng dữ liệu từ ma trận dưới dạng một đối tượng BitArray.
        
        - y: Chỉ số hàng cần lấy.
        - row: Một đối tượng BitArray đã được cấp phát từ trước. Nếu tham số này là None hoặc quá nhỏ, 
            một BitArray mới sẽ được cấp phát.
        
        Trả về: Đối tượng BitArray chứa dữ liệu của hàng được lấy.
        """
        if row is None or len(row.bits) < self.width:
            row = BitArray(self.width)  # Tạo một BitArray mới nếu row không hợp lệ hoặc quá nhỏ
        else:
            row.clear()  # Xóa dữ liệu cũ nếu row đã được cung cấp

        offset = y * self.row_size
        for x in range(self.row_size):
            row.set_bulk(x * 32, self.bits[offset + x])

        return row


    def set_row(self, y, row):
        """
        Sao chép dữ liệu từ một đối tượng BitArray vào một hàng trong ma trận.

        - y: Chỉ số hàng cần thiết lập.
        - row: Đối tượng BitArray chứa dữ liệu cần sao chép vào hàng trong ma trận.
        """
        self.bits[y * self.row_size: (y + 1) * self.row_size] = row.bits[:self.row_size]

    def rotate(self, degrees):
        """
        Chỉnh sửa ma trận này sao cho nó quay một góc nhất định (0, 90, 180, 270 độ).

        - degrees: Số độ để quay ma trận theo chiều ngược kim đồng hồ (0, 90, 180, 270).
        """
        degrees = degrees % 360  # Đảm bảo góc quay là bội số của 90
        if degrees == 0:
            return
        elif degrees == 90:
            self.rotate_90()
        elif degrees == 180:
            self.rotate_180()
        elif degrees == 270:
            self.rotate_90()
            self.rotate_180()
        else:
            raise ValueError("degrees phải là một bội số của 0, 90, 180, hoặc 270")
        

    
    def rotate_180(self):
        """
        Chỉnh sửa ma trận này sao cho nó quay 180 độ.

        Hàm sẽ đảo ngược từng hàng, rồi hoán đổi vị trí các hàng đối diện nhau.
        """
        max_height = (self.height + 1) // 2
        for i in range(max_height):
            top_row = self.get_row(i)
            bottom_row_index = self.height - 1 - i
            bottom_row = self.get_row(bottom_row_index)
            
            # Đảo ngược các hàng
            top_row.reverse()
            bottom_row.reverse()

            # Đặt lại các hàng đã đảo ngược vào đúng vị trí
            self.set_row(i, bottom_row)
            self.set_row(bottom_row_index, top_row)

    def rotate_90(self):
        """
        Chỉnh sửa ma trận này sao cho nó quay 90 độ theo chiều ngược kim đồng hồ.

        Hàm tạo ra một ma trận mới với chiều rộng và chiều cao hoán đổi cho nhau.
        """
        new_width = self.height
        new_height = self.width
        new_row_size = (new_width + 31) // 32
        new_bits = [0] * (new_row_size * new_height)

        for y in range(self.height):
            for x in range(self.width):
                # Tính toán vị trí offset trong ma trận cũ
                offset = y * self.row_size + (x // 32)
                if (self.bits[offset] >> (x & 0x1f)) & 1:
                    # Tính toán vị trí mới trong ma trận quay 90 độ
                    new_offset = (new_height - 1 - x) * new_row_size + (y // 32)
                    new_bits[new_offset] |= 1 << (y & 0x1f)

        # Cập nhật lại kích thước và dữ liệu của ma trận
        self.width = new_width
        self.height = new_height
        self.row_size = new_row_size
        self.bits = new_bits


    def get_enclosing_rectangle(self):
        """
        Hàm này xác định hình chữ nhật bao quanh tất cả các bit có giá trị 1 trong ma trận.
        Nó hữu ích trong việc phát hiện hình chữ nhật bao quanh của mã vạch 'thuần túy'.

        Trả về một danh sách gồm các giá trị: [left, top, width, height], 
        trong đó 'left' là vị trí cột bên trái, 'top' là vị trí hàng trên cùng, 
        'width' là chiều rộng và 'height' là chiều cao của hình chữ nhật bao quanh.
        Trả về None nếu ma trận hoàn toàn trắng (không có bit 1).
        """
        left = self.width
        top = self.height
        right = -1
        bottom = -1

        # Duyệt qua tất cả các hàng và cột để tìm các bit có giá trị 1
        for y in range(self.height):
            for x32 in range(self.row_size):
                the_bits = self.bits[y * self.row_size + x32]
                if the_bits != 0:  # Nếu có bit 1 trong ô này
                    if y < top:
                        top = y
                    if y > bottom:
                        bottom = y

                    # Tìm giá trị 'left'
                    if x32 * 32 < left:
                        bit = 0
                        while (the_bits << (31 - bit)) == 0:
                            bit += 1
                        if (x32 * 32 + bit) < left:
                            left = x32 * 32 + bit

                    # Tìm giá trị 'right'
                    if x32 * 32 + 31 > right:
                        bit = 31
                        while (the_bits >> bit) == 0:
                            bit -= 1
                        if (x32 * 32 + bit) > right:
                            right = x32 * 32 + bit

        # Nếu không có bit 1 nào, trả về None
        if right < left or bottom < top:
            return None

        # Trả về hình chữ nhật bao quanh
        return [left, top, right - left + 1, bottom - top + 1]

    

    def get_top_left_on_bit(self):
        """
        Hàm này xác định tọa độ của bit 1 nằm ở góc trên bên trái của ma trận.
        Nó hữu ích trong việc phát hiện điểm bắt đầu của mã vạch 'thuần túy'.

        Trả về một danh sách gồm các giá trị [x, y], trong đó 'x' là vị trí cột 
        và 'y' là vị trí hàng của bit 1 đầu tiên. Nếu ma trận hoàn toàn trắng (không có bit 1),
        trả về None.
        """
        bits_offset = 0
        
        # Tìm kiếm vị trí đầu tiên có bit 1 trong mảng bits
        while bits_offset < len(self.bits) and self.bits[bits_offset] == 0:
            bits_offset += 1

        # Nếu không tìm thấy bit 1 nào, trả về None
        if bits_offset == len(self.bits):
            return None

        # Tính toán vị trí y (hàng) của bit đầu tiên
        y = bits_offset // self.row_size
        # Tính toán vị trí x (cột) của bit đầu tiên
        x = (bits_offset % self.row_size) * 32

        the_bits = self.bits[bits_offset]
        bit = 0
        
        # Tìm bit đầu tiên có giá trị 1 trong số các bit của số nguyên hiện tại
        while (the_bits << (31 - bit)) == 0:
            bit += 1

        # Cập nhật vị trí x để phản ánh vị trí chính xác của bit 1
        x += bit
        
        return [x, y]

    

    def get_bottom_right_on_bit(self):
        """
        Hàm này xác định tọa độ của bit 1 nằm ở góc dưới bên phải của ma trận.
        Nó hữu ích trong việc phát hiện điểm cuối của mã vạch 'thuần túy'.

        Trả về một danh sách gồm các giá trị [x, y], trong đó 'x' là vị trí cột 
        và 'y' là vị trí hàng của bit 1 cuối cùng. Nếu ma trận hoàn toàn trắng (không có bit 1),
        trả về None.
        """
        bits_offset = len(self.bits) - 1
        
        # Tìm kiếm vị trí cuối cùng có bit 1 trong mảng bits
        while bits_offset >= 0 and self.bits[bits_offset] == 0:
            bits_offset -= 1

        # Nếu không tìm thấy bit 1 nào, trả về None
        if bits_offset < 0:
            return None

        # Tính toán vị trí y (hàng) của bit cuối cùng
        y = bits_offset // self.row_size
        # Tính toán vị trí x (cột) của bit cuối cùng
        x = (bits_offset % self.row_size) * 32

        the_bits = self.bits[bits_offset]
        bit = 31
        
        # Tìm bit cuối cùng có giá trị 1 trong số các bit của số nguyên hiện tại
        while (the_bits >> bit) == 0:
            bit -= 1

        # Cập nhật vị trí x để phản ánh vị trí chính xác của bit 1
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

