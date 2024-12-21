import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .GenericGFPoly import GenericGFPoly
from .GenericGF import GenericGF

class ReedSolomonException(Exception):
    """
    Ngoại lệ tùy chỉnh cho Reed-Solomon Decoder.
    """
    def __init__(self, message):
        super().__init__(message)

class ReedSolomonDecoder:
    """
    Lớp ReedSolomonDecoder thực hiện giải mã Reed-Solomon, giúp phát hiện và sửa lỗi trong dữ liệu.
    """

    def __init__(self, field):
        """
        Khởi tạo đối tượng ReedSolomonDecoder.

        Input:
        - field: GenericGF, trường Galois được sử dụng cho các phép toán.

        Hàm này thiết lập trường Galois cần thiết để thực hiện các phép toán giải mã.
        """
        self.field = field

    def decode(self, received, two_s):
        """
        Giải mã tập hợp các mã nhận được, bao gồm cả dữ liệu và mã sửa lỗi.

        Input:
        - received: danh sách số nguyên, các mã nhận được.
        - two_s: số nguyên, số lượng mã sửa lỗi có sẵn.

        Công việc:
        Hàm sử dụng phương pháp Reed-Solomon để phát hiện và sửa lỗi trong danh sách `received`.
        """
        self.decode_with_ec_count(received, two_s)

    def decode_with_ec_count(self, received, two_s):
        """
        Giải mã dữ liệu, phát hiện và sửa lỗi trong danh sách mã nhận được.

        Input:
        - received: danh sách số nguyên, dữ liệu nhận được (gồm cả dữ liệu và mã sửa lỗi).
        - two_s: số nguyên, số lượng mã sửa lỗi có sẵn.

        Output:
        - Trả về số lượng lỗi đã được sửa.

        Công việc:
        - Xây dựng đa thức từ dữ liệu nhận được.
        - Tính toán các hội chứng để phát hiện lỗi.
        - Nếu không có lỗi, kết thúc sớm.
        - Nếu có lỗi, sử dụng thuật toán Euclid để tìm các vị trí và độ lớn của lỗi.
        - Sửa lỗi trong dữ liệu nhận được.
        """
        poly = GenericGFPoly(self.field, received)
        syndrome_coefficients = [0] * two_s
        no_error = True
        for i in range(two_s):
            eval = poly.evaluate_at(self.field.exp(i + self.field.get_generator_base()))
            syndrome_coefficients[two_s - 1 - i] = eval
            if eval != 0:
                no_error = False

        if no_error:
            return 0

        syndrome = GenericGFPoly(self.field, syndrome_coefficients)
        sigma_omega = self.run_euclidean_algorithm(self.field.build_monomial(two_s, 1), syndrome, two_s)
        sigma = sigma_omega[0]
        omega = sigma_omega[1]

        error_locations = self.find_error_locations(sigma)
        error_magnitudes = self.find_error_magnitudes(omega, error_locations)

        for i in range(len(error_locations)):
            position = len(received) - 1 - self.field.log(error_locations[i])
            if position < 0:
                raise ReedSolomonException("Vị trí lỗi không hợp lệ")
            received[position] = GenericGF.add_or_subtract(received[position], error_magnitudes[i])

        return len(error_locations)

    def run_euclidean_algorithm(self, a, b, R):
        """
        Thực hiện thuật toán Euclid để tìm đa thức locator và evaluator.

        Input:
        - a: GenericGFPoly, đa thức đầu tiên.
        - b: GenericGFPoly, đa thức thứ hai.
        - R: số nguyên, độ dài của đa thức sửa lỗi.

        Output:
        - Trả về một cặp đa thức [sigma, omega]:
          + sigma: đa thức locator lỗi.
          + omega: đa thức evaluator lỗi.

        Công việc:
        - Thực hiện chia đa thức theo thuật toán Euclid.
        - Dừng lại khi bậc của đa thức còn lại nhỏ hơn R/2.
        """
        if a.get_degree() < b.get_degree():
            a, b = b, a

        r_last = a
        r = b
        t_last = self.field.get_zero()
        t = self.field.get_one()

        while 2 * r.get_degree() >= R:
            r_last_last = r_last
            t_last_last = t_last
            r_last = r
            t_last = t

            if r_last.is_zero():
                raise ReedSolomonException("r_{i-1} bằng 0")

            r = r_last_last
            q = self.field.get_zero()
            denominator_leading_term = r_last.get_coefficient(r_last.get_degree())
            dlt_inverse = self.field.inverse(denominator_leading_term)

            while r.get_degree() >= r_last.get_degree() and not r.is_zero():
                degree_diff = r.get_degree() - r_last.get_degree()
                scale = self.field.multiply(r.get_coefficient(r.get_degree()), dlt_inverse)
                q = q.add_or_subtract(self.field.build_monomial(degree_diff, scale))
                r = r.add_or_subtract(r_last.multiply_by_monomial(degree_diff, scale))

            t = q.multiply(t_last).add_or_subtract(t_last_last)

            if r.get_degree() >= r_last.get_degree():
                raise RuntimeError("Thuật toán chia thất bại")

        sigma_tilde_at_zero = t.get_coefficient(0)
        if sigma_tilde_at_zero == 0:
            raise ReedSolomonException("sigmaTilde(0) bằng 0")

        inverse = self.field.inverse(sigma_tilde_at_zero)
        sigma = t.multiply(inverse)
        omega = r.multiply(inverse)
        return [sigma, omega]

    def find_error_locations(self, error_locator):
        """
        Tìm vị trí các lỗi trong dữ liệu.

        Input:
        - error_locator: GenericGFPoly, đa thức locator lỗi.

        Output:
        - Trả về danh sách vị trí lỗi (dạng số nguyên).

        Công việc:
        - Sử dụng tìm kiếm Chien để xác định các gốc của đa thức locator.
        """
        num_errors = error_locator.get_degree()
        if num_errors == 1:
            return [error_locator.get_coefficient(1)]

        result = []
        for i in range(1, self.field.get_size()):
            if error_locator.evaluate_at(i) == 0:
                result.append(self.field.inverse(i))
        if len(result) != num_errors:
            raise ReedSolomonException("Bậc của locator không khớp với số lượng lỗi")
        return result

    def find_error_magnitudes(self, error_evaluator, error_locations):
        """
        Tìm độ lớn của các lỗi đã phát hiện.

        Input:
        - error_evaluator: GenericGFPoly, đa thức evaluator lỗi.
        - error_locations: danh sách số nguyên, vị trí lỗi.

        Output:
        - Trả về danh sách độ lớn lỗi (dạng số nguyên).

        Công việc:
        - Áp dụng công thức của Forney để tính độ lớn lỗi.
        """
        s = len(error_locations)
        result = [0] * s
        for i in range(s):
            xi_inverse = self.field.inverse(error_locations[i])
            denominator = 1
            for j in range(s):
                if i != j:
                    term = self.field.multiply(error_locations[j], xi_inverse)
                    term_plus_1 = (term | 1) if (term & 1) == 0 else (term & ~1)
                    denominator = self.field.multiply(denominator, term_plus_1)
            result[i] = self.field.multiply(
                error_evaluator.evaluate_at(xi_inverse),
                self.field.inverse(denominator)
            )
            if self.field.get_generator_base() != 0:
                result[i] = self.field.multiply(result[i], xi_inverse)
        return result
