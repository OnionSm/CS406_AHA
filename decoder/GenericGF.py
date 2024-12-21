import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .GenericGFPoly import GenericGFPoly

class GenericGF:
    AZTEC_DATA_12 = None  # Được định nghĩa sau
    AZTEC_DATA_10 = None  # Được định nghĩa sau
    AZTEC_DATA_6 = None  # Được định nghĩa sau
    AZTEC_PARAM = None  # Được định nghĩa sau
    QR_CODE_FIELD_256 = None  # Được định nghĩa sau
    DATA_MATRIX_FIELD_256 = None  # Được định nghĩa sau
    AZTEC_DATA_8 = None  # Được định nghĩa sau
    MAXICODE_FIELD_64 = None  # Được định nghĩa sau

    def __init__(self, primitive, size, b):
        """Khởi tạo một trường Galois GF(size) sử dụng đa thức nguyên thủy đã cho.
        
        Input:
        - primitive: đa thức nguyên thủy (kiểu int) dùng cho các phép toán trong trường Galois.
        - size: kích thước của trường (kiểu int), thông thường là một lũy thừa của 2.
        - b: hằng số trong đa thức sinh, có thể là 0 hoặc 1 (kiểu int).

        Mô tả: Khởi tạo các bảng log và exp, các phép toán trong trường Galois, và các đối tượng đa thức zero và one.
        Output: None
        """
        self.primitive = primitive
        self.size = size
        self.generatorBase = b

        self.expTable = [0] * size
        self.logTable = [0] * size
        x = 1
        for i in range(size):
            self.expTable[i] = x
            x *= 2  # 2 (đại diện cho đa thức x) là phần tử nguyên thủy
            if x >= size:
                x ^= primitive
                x &= size - 1
        for i in range(size - 1):
            self.logTable[self.expTable[i]] = i
        self.zero = GenericGFPoly(self, [0])
        self.one = GenericGFPoly(self, [1])

    def get_zero(self):
        """Trả về đa thức zero (0).
        
        Input: Không có.
        Mô tả: Trả về đối tượng đa thức zero (đại diện cho giá trị 0 trong trường Galois).
        Output: Một đối tượng GenericGFPoly đại diện cho zero.
        """
        return self.zero

    def get_one(self):
        """Trả về đa thức one (1).
        
        Input: Không có.
        Mô tả: Trả về đối tượng đa thức one (đại diện cho giá trị 1 trong trường Galois).
        Output: Một đối tượng GenericGFPoly đại diện cho one.
        """
        return self.one

    def build_monomial(self, degree, coefficient):
        """Tạo đa thức monomial có dạng coefficient * x^degree.

        Input:
        - degree: bậc của biến x trong đa thức (kiểu int).
        - coefficient: hệ số của đa thức (kiểu int).
        
        Mô tả: Tạo một đa thức có hệ số là coefficient và bậc là degree. Nếu hệ số là 0, trả về đa thức zero.
        Output: Trả về đối tượng GenericGFPoly đại diện cho đa thức đã tạo.
        """
        if degree < 0:
            raise ValueError("Degree phải lớn hơn hoặc bằng 0.")
        if coefficient == 0:
            return self.zero
        coefficients = [0] * (degree + 1)
        coefficients[0] = coefficient
        return GenericGFPoly(self, coefficients)

    @staticmethod
    def add_or_subtract(a, b):
        """Thực hiện phép cộng hoặc phép trừ trong trường Galois (cộng và trừ là giống nhau).

        Input:
        - a: số nguyên thứ nhất (kiểu int).
        - b: số nguyên thứ hai (kiểu int).
        
        Mô tả: Phép cộng và trừ trong trường Galois là phép XOR giữa hai số.
        Output: Trả về kết quả phép cộng hoặc phép trừ giữa a và b.
        """
        return a ^ b

    def exp(self, a):
        """Tính lũy thừa của a trong trường Galois.

        Input:
        - a: số cần tính lũy thừa (kiểu int).
        
        Mô tả: Trả về 2^a trong trường Galois GF(size).
        Output: Trả về giá trị 2^a trong trường Galois.
        """
        return self.expTable[a]

    def log(self, a):
        """Tính log cơ số 2 của a trong trường Galois.

        Input:
        - a: số cần tính log (kiểu int).
        
        Mô tả: Trả về log của a trong trường Galois GF(size).
        Output: Trả về giá trị log cơ số 2 của a.
        """
        if a == 0:
            raise ValueError("Không thể tính log của 0.")
        return self.logTable[a]

    def inverse(self, a):
        """Tính nghịch đảo của a trong trường Galois.

        Input:
        - a: số cần tính nghịch đảo (kiểu int).
        
        Mô tả: Tính nghịch đảo của a trong trường Galois GF(size).
        Output: Trả về nghịch đảo của a trong trường Galois.
        """
        if a == 0:
            raise ArithmeticError("Không thể tính nghịch đảo của 0.")
        return self.expTable[self.size - self.logTable[a] - 1]

    def multiply(self, a, b):
        """Nhân hai số trong trường Galois.

        Input:
        - a: số nguyên thứ nhất (kiểu int).
        - b: số nguyên thứ hai (kiểu int).
        
        Mô tả: Nhân hai số a và b trong trường Galois GF(size).
        Output: Trả về tích của a và b trong trường Galois.
        """
        if a == 0 or b == 0:
            return 0
        return self.expTable[(self.logTable[a] + self.logTable[b]) % (self.size - 1)]

    def get_size(self):
        """Lấy kích thước của trường Galois.

        Input: Không có.
        Mô tả: Trả về kích thước của trường Galois.
        Output: Trả về kích thước của trường.
        """
        return self.size

    def get_generator_base(self):
        """Lấy giá trị cơ sở của đa thức sinh.

        Input: Không có.
        Mô tả: Trả về giá trị cơ sở của đa thức sinh trong trường Galois.
        Output: Trả về giá trị cơ sở của đa thức sinh.
        """
        return self.generatorBase

    def __str__(self):
        """Trả về chuỗi biểu diễn của trường Galois.

        Input: Không có.
        Mô tả: Trả về một chuỗi mô tả trường Galois với đa thức nguyên thủy và kích thước.
        Output: Chuỗi mô tả trường Galois.
        """
        return f"GF(0x{self.primitive:x},{self.size})"
