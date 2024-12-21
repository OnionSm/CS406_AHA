import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from abc import ABC, abstractmethod
from qrcode import BitMatrix


class DataMask(ABC):

    @abstractmethod
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn hay không.
        
        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).
        
        Mô tả: Hàm này sẽ kiểm tra điều kiện của từng kiểu mask cụ thể.
        
        Output:
        - (bool): True nếu bit tại (i, j) bị ẩn, False nếu không.
        """
        pass

    def unmask_bit_matrix(self, bits, dimension):
        """
        Đảo ngược quá trình ẩn dữ liệu trên một ma trận QR code.

        Input:
        - bits (BitMatrix): Ma trận QR code chứa các bit cần được giải mã.
        - dimension (int): Kích thước của ma trận QR code.

        Mô tả: Quá trình này sẽ kiểm tra mỗi vị trí trong ma trận, nếu vị trí đó bị ẩn
        theo quy định của mỗi kiểu Data Mask thì sẽ đảo trạng thái bit tại vị trí đó.

        Output:
        - Không có giá trị trả về, hàm này thay đổi trực tiếp ma trận `bits`.
        """
        for i in range(dimension):
            for j in range(dimension):
                if self.is_masked(i, j):
                    bits.flip(j, i)


class DataMask000(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện (x + y) mod 2 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu tổng của x và y chia cho 2 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return (i + j) % 2 == 0


class DataMask001(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện x mod 2 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu x chia cho 2 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return i % 2 == 0


class DataMask010(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện y mod 3 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu y chia cho 3 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return j % 3 == 0


class DataMask011(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện (x + y) mod 3 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu tổng của x và y chia cho 3 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return (i + j) % 3 == 0


class DataMask100(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện (x / 2 + y / 3) mod 2 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu (x/2 + y/3) chia cho 2 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return ((i // 2) + (j // 3)) % 2 == 0


class DataMask101(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện xy mod 2 + xy mod 3 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu xy chia cho 6 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return (i * j) % 6 == 0


class DataMask110(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện (xy mod 2 + xy mod 3) mod 2 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu (xy mod 6) nhỏ hơn 3 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return (i * j) % 6 < 3


class DataMask111(DataMask):
    def is_masked(self, i, j):
        """
        Kiểm tra xem bit tại vị trí (i, j) có bị ẩn theo điều kiện ((x + y) mod 2 + xy mod 3) mod 2 == 0.

        Input:
        - i (int): Vị trí hàng (row).
        - j (int): Vị trí cột (column).

        Mô tả: Kiểm tra nếu (x + y + (xy mod 3)) chia cho 2 dư 0 thì bit bị ẩn.

        Output:
        - (bool): True nếu bit bị ẩn, False nếu không.
        """
        return ((i + j + ((i * j) % 3)) % 2) == 0
