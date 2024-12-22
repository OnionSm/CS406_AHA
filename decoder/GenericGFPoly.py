import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
class GenericGFPoly:
    def __init__(self, field, coefficients):
        """
        Khởi tạo đối tượng polynomial với các hệ số là phần tử của trường GF.

        Input:
        - field (GenericGF): Trường GF để thực hiện các phép tính.
        - coefficients (list[int]): Danh sách hệ số, từ bậc cao nhất đến thấp nhất.

        Output:
        - Tạo đối tượng GenericGFPoly.
        """
        if not coefficients:
            raise ValueError("Coefficients must not be empty")

        self.field = field
        if len(coefficients) > 1 and coefficients[0] == 0:
            # Loại bỏ các hệ số 0 đầu tiên nếu không phải đa thức hằng số "0"
            first_non_zero = next((i for i, c in enumerate(coefficients) if c != 0), len(coefficients))
            self.coefficients = coefficients[first_non_zero:] if first_non_zero < len(coefficients) else [0]
        else:
            self.coefficients = coefficients

    def get_coefficients(self):
        """
        Lấy danh sách hệ số của đa thức.

        Output:
        - List[int]: Danh sách hệ số.
        """
        return self.coefficients

    def get_degree(self):
        """
        Lấy bậc của đa thức.

        Output:
        - int: Bậc của đa thức.
        """
        return len(self.coefficients) - 1

    def is_zero(self):
        """
        Kiểm tra xem đa thức có phải là "0" hay không.

        Output:
        - bool: True nếu là đa thức "0", ngược lại False.
        """
        return self.coefficients[0] == 0

    def get_coefficient(self, degree):
        """
        Lấy hệ số của hạng tử x^degree.

        Input:
        - degree (int): Bậc của hạng tử.

        Output:
        - int: Hệ số của hạng tử x^degree.
        """
        return self.coefficients[-1 - degree]

    def evaluate_at(self, a):
        """
        Tính giá trị của đa thức tại điểm a.

        Input:
        - a (int): Giá trị tại điểm cần tính toán.

        Output:
        - int: Giá trị của đa thức tại a.
        """
        if a == 0:
            return self.get_coefficient(0)
        if a == 1:
            return sum(self.field.add_or_subtract(c, 0) for c in self.coefficients)

        result = self.coefficients[0]
        for coeff in self.coefficients[1:]:
            result = self.field.add_or_subtract(self.field.multiply(a, result), coeff)
        return result

    def add_or_subtract(self, other):
        """
        Cộng hoặc trừ hai đa thức.

        Input:
        - other (GenericGFPoly): Đa thức khác để cộng hoặc trừ.

        Output:
        - GenericGFPoly: Kết quả sau khi cộng hoặc trừ.
        """
        if self.field != other.field:
            raise ValueError("Polynomials are from different fields")

        if self.is_zero():
            return other
        if other.is_zero():
            return self

        smaller_coeffs = self.coefficients
        larger_coeffs = other.coefficients
        if len(smaller_coeffs) > len(larger_coeffs):
            smaller_coeffs, larger_coeffs = larger_coeffs, smaller_coeffs

        length_diff = len(larger_coeffs) - len(smaller_coeffs)
        sum_diff = larger_coeffs[:length_diff] + [
            self.field.add_or_subtract(smaller_coeffs[i], larger_coeffs[i + length_diff])
            for i in range(len(smaller_coeffs))
        ]

        return GenericGFPoly(self.field, sum_diff)

    def multiply(self, other):
        """
        Nhân hai đa thức.

        Input:
        - other (GenericGFPoly): Đa thức khác để nhân.

        Output:
        - GenericGFPoly: Kết quả sau khi nhân.
        """
        if self.field != other.field:
            raise ValueError("Polynomials are from different fields")
        if self.is_zero() or other.is_zero():
            return self.field.get_zero()

        a_coeffs = self.coefficients
        b_coeffs = other.coefficients
        product = [0] * (len(a_coeffs) + len(b_coeffs) - 1)

        for i, a in enumerate(a_coeffs):
            for j, b in enumerate(b_coeffs):
                product[i + j] = self.field.add_or_subtract(
                    product[i + j], self.field.multiply(a, b)
                )

        return GenericGFPoly(self.field, product)

    def multiply_by_monomial(self, degree, coefficient):
        """
        Nhân đa thức với một đơn thức.

        Input:
        - degree (int): Bậc của đơn thức.
        - coefficient (int): Hệ số của đơn thức.

        Output:
        - GenericGFPoly: Kết quả sau khi nhân.
        """
        if degree < 0:
            raise ValueError("Degree must be non-negative")
        if coefficient == 0:
            return self.field.get_zero()

        product = [0] * (len(self.coefficients) + degree)
        for i, c in enumerate(self.coefficients):
            product[i] = self.field.multiply(c, coefficient)

        return GenericGFPoly(self.field, product)

    def divide(self, other):
        """
        Chia hai đa thức, trả về thương và dư.

        Input:
        - other (GenericGFPoly): Đa thức chia.

        Output:
        - tuple(GenericGFPoly, GenericGFPoly): (thương, dư).
        """
        if self.field != other.field:
            raise ValueError("Polynomials are from different fields")
        if other.is_zero():
            raise ValueError("Cannot divide by zero polynomial")

        quotient = self.field.get_zero()
        remainder = self

        denominator_leading_term = other.get_coefficient(other.get_degree())
        inverse_denominator_leading_term = self.field.inverse(denominator_leading_term)

        while remainder.get_degree() >= other.get_degree() and not remainder.is_zero():
            degree_diff = remainder.get_degree() - other.get_degree()
            scale = self.field.multiply(
                remainder.get_coefficient(remainder.get_degree()),
                inverse_denominator_leading_term,
            )
            term = other.multiply_by_monomial(degree_diff, scale)
            iteration_quotient = self.field.build_monomial(degree_diff, scale)
            quotient = quotient.add_or_subtract(iteration_quotient)
            remainder = remainder.add_or_subtract(term)

        return quotient, remainder

    def __str__(self):
        """
        Chuyển đổi đa thức thành chuỗi biểu diễn.

        Output:
        - str: Biểu diễn chuỗi của đa thức.
        """
        if self.is_zero():
            return "0"

        result = []
        for degree in range(self.get_degree(), -1, -1):
            coefficient = self.get_coefficient(degree)
            if coefficient != 0:
                if coefficient < 0:
                    result.append(" - " if result else "-")
                    coefficient = -coefficient
                elif result:
                    result.append(" + ")

                if degree == 0 or coefficient != 1:
                    alpha_power = self.field.log(coefficient)
                    if alpha_power == 0:
                        result.append("1")
                    elif alpha_power == 1:
                        result.append("a")
                    else:
                        result.append(f"a^{alpha_power}")

                if degree > 0:
                    result.append("x")
                    if degree > 1:
                        result.append(f"^{degree}")

        return "".join(result)
