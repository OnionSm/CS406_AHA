import sys 
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
class BitArray:
    EMPTY_BITS = np.array([], dtype=int)
    LOAD_FACTOR: float = 0.75

    def __init__(self, size=0):
        self.size: int = size
        self.bits: np.array = BitArray.make_array(size)

    def get_size(self):
        return self.size

    def get_size_in_bytes(self):
        return (self.size + 7) // 8

    def ensure_capacity(self, new_size):
        # Kiểm tra nếu new_size vượt quá dung lượng hiện tại
        if new_size > len(self.bits) * 32:
            new_bits_size = int(np.ceil(new_size / self.LOAD_FACTOR))
            new_bits = self.make_array(new_bits_size)
            # Sao chép các giá trị từ mảng cũ sang mảng mới
            np.copyto(new_bits, self.bits)
            self.bits = new_bits

    def get(self, i):
        # Kiểm tra bit tại vị trí i
        return (self.bits[i // 32] & (1 << (i & 0x1F))) != 0

    def set(self, i):
        # Đặt bit tại vị trí i
        self.bits[i // 32] |= 1 << (i & 0x1F)

    def flip(self, i):
        # Đảo bit tại vị trí i
        self.bits[i // 32] ^= 1 << (i & 0x1F)

    def get_next_set(self, from_index):
        if from_index >= self.size:
            return self.size

        bits_offset = from_index // 32
        current_bits = self.bits[bits_offset]

        # Mask off lesser bits first
        current_bits &= -(1 << (from_index & 0x1F))

        while current_bits == 0:
            bits_offset += 1
            if bits_offset == len(self.bits):
                return self.size
            current_bits = self.bits[bits_offset]

        result = (bits_offset * 32) + self.number_of_trailing_zeros(current_bits)
        return min(result, self.size)

    @staticmethod
    def number_of_trailing_zeros(x):
        # Sử dụng Python's built-in bit_length để tìm số lượng bit 0 phía sau
        return (x & -x).bit_length() - 1 if x != 0 else 32

    def get_next_unset(self, from_index):
        if from_index >= self.size:
            return self.size

        bits_offset = from_index // 32
        current_bits = ~self.bits[bits_offset]

        # Mask off lesser bits first
        current_bits &= -(1 << (from_index & 0x1F))

        while current_bits == 0:
            bits_offset += 1
            if bits_offset == len(self.bits):
                return self.size
            current_bits = ~self.bits[bits_offset]

        result = (bits_offset * 32) + self.number_of_trailing_zeros(current_bits)
        return min(result, self.size)

    def set_bulk(self, i, new_bits):
        self.bits[i // 32] = new_bits


    def set_range(self, start, end):
        if end < start or start < 0 or end > self.size:
            raise ValueError("Invalid range")
        if end == start:
            return
        end -= 1  # Treat the end as inclusive
        first_int = start // 32
        last_int = end // 32
        for i in range(first_int, last_int + 1):
            first_bit = 0 if i > first_int else start & 0x1F
            last_bit = 31 if i < last_int else end & 0x1F
            # Create mask from first_bit to last_bit (inclusive)
            mask = (2 << last_bit) - (1 << first_bit)
            self.bits[i] |= mask

    def clear(self):
        self.bits.fill(0)

    def is_range(self, start, end, value):
        if end < start or start < 0 or end > self.size:
            raise ValueError("Invalid range")
        if end == start:
            return True  # empty range matches
        end -= 1  # Treat as last bit inclusively
        first_int = start // 32
        last_int = end // 32
        for i in range(first_int, last_int + 1):
            first_bit = 0 if i > first_int else start & 0x1F
            last_bit = 31 if i < last_int else end & 0x1F
            # Mask from first_bit to last_bit
            mask = (2 << last_bit) - (1 << first_bit)
            # Check if the masked portion matches the value we're looking for
            if (self.bits[i] & mask) != (mask if value else 0):
                return False
        return True

    def append_bit(self, bit):
        # Đảm bảo đủ dung lượng
        self.ensure_capacity(self.size + 1)
        # Thêm bit vào mảng
        if bit:
            self.bits[self.size // 32] |= 1 << (self.size & 0x1F)
        # Tăng kích thước (số bit đã thêm)
        self.size += 1

    def append_bits(self, value, num_bits):
        # Kiểm tra số lượng bit hợp lệ
        if num_bits < 0 or num_bits > 32:
            raise ValueError("Num bits must be between 0 and 32")
        # Tính kích thước mới sau khi thêm bits
        next_size = self.size
        self.ensure_capacity(next_size + num_bits)
        # Thêm bits vào mảng từ bit cao nhất đến thấp nhất
        for num_bits_left in range(num_bits - 1, -1, -1):
            if (value & (1 << num_bits_left)) != 0:
                self.bits[next_size // 32] |= 1 << (next_size & 0x1F)
            next_size += 1
        # Cập nhật lại kích thước mảng
        self.size = next_size

    def append_bit_array(self, other):
        # Thêm mảng bit từ 'other' vào mảng hiện tại
        other_size = other.size
        self.ensure_capacity(self.size + other_size)
        for i in range(other_size):
            self.append_bit(other.get(i))

    def xor(self, other):
        if self.size != other.size:
            raise ValueError("Sizes don't match")
        for i in range(len(self.bits)):
            self.bits[i] ^= other.bits[i]


    def to_bytes(self, bit_offset, array, offset, num_bytes):
        for i in range(num_bytes):
            the_byte = 0
            for j in range(8):
                if self.get(bit_offset):
                    the_byte |= 1 << (7 - j)
                bit_offset += 1
            array[offset + i] = the_byte & 0xFF  # Ensuring byte value is within byte range

    def get_bit_array(self):
        return self.bits

    def reverse(self):
        new_bits = np.zeros_like(self.bits)  # Tạo mảng mới có cùng kích thước
        len_bits = (self.size - 1) // 32
        old_bits_len = len_bits + 1

        # Đảo ngược tất cả các int trước
        for i in range(old_bits_len):
            new_bits[len_bits - i] = np.uint32(~self.bits[i])  # Reverse bits trong từng int

        # Sửa các int nếu kích thước bit không phải là bội số của 32
        if self.size != old_bits_len * 32:
            left_offset = old_bits_len * 32 - self.size
            current_int = new_bits[0] >> left_offset
            for i in range(1, old_bits_len):
                next_int = new_bits[i]
                current_int |= next_int << (32 - left_offset)
                new_bits[i - 1] = current_int
                current_int = next_int >> left_offset
            new_bits[old_bits_len - 1] = current_int

        self.bits = new_bits

    @staticmethod
    def make_array(size):
        return np.zeros((size + 31) // 32, dtype=np.uint32)

    def __eq__(self, other):
        if not isinstance(other, BitArray):
            return False
        return self.size == other.size and np.array_equal(self.bits, other.bits)

    def __hash__(self):
        return 31 * self.size + hash(tuple(self.bits))

    def __str__(self):
        result = []
        for i in range(self.size):
            if i % 8 == 0:
                result.append(' ')
            result.append('X' if self.get(i) else '.')
        return ''.join(result)

    def clone(self):
        new_clone = BitArray(self.size)
        new_clone.bits = np.copy(self.bits)
        return new_clone
