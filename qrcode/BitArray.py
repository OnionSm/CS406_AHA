class BitArray:
    EMPTY_BITS = []
    LOAD_FACTOR = 0.75

    def __init__(self, size=0):
        self.size = size
        self.bits = self.make_array(size)

    @staticmethod
    def make_array(size):
        return [0] * ((size + 31) // 32)

    def get_size(self):
        return self.size

    def get_size_in_bytes(self):
        return (self.size + 7) // 8

    def ensure_capacity(self, new_size):
        if new_size > len(self.bits) * 32:
            new_bits = self.make_array(int((new_size + self.LOAD_FACTOR - 1) // self.LOAD_FACTOR))
            new_bits[:len(self.bits)] = self.bits
            self.bits = new_bits

    def get(self, i):
        return (self.bits[i // 32] & (1 << (i % 32))) != 0

    def set(self, i):
        self.bits[i // 32] |= 1 << (i % 32)

    def flip(self, i):
        self.bits[i // 32] ^= 1 << (i % 32)

    def get_next_set(self, from_idx):
        if from_idx >= self.size:
            return self.size
        bits_offset = from_idx // 32
        current_bits = self.bits[bits_offset]
        current_bits &= -(1 << (from_idx % 32))
        while current_bits == 0:
            if bits_offset == len(self.bits) - 1:
                return self.size
            bits_offset += 1
            current_bits = self.bits[bits_offset]
        return min(bits_offset * 32 + bin(current_bits).count('0'), self.size)

    def get_next_unset(self, from_idx):
        if from_idx >= self.size:
            return self.size
        bits_offset = from_idx // 32
        current_bits = ~self.bits[bits_offset]
        current_bits &= -(1 << (from_idx % 32))
        while current_bits == 0:
            if bits_offset == len(self.bits) - 1:
                return self.size
            bits_offset += 1
            current_bits = ~self.bits[bits_offset]
        return min(bits_offset * 32 + bin(current_bits).count('0'), self.size)

    def set_bulk(self, i, new_bits):
        self.bits[i // 32] = new_bits

    def set_range(self, start, end):
        if end < start or start < 0 or end > self.size:
            raise ValueError("Invalid range")
        if end == start:
            return
        end -= 1
        first_int = start // 32
        last_int = end // 32
        for i in range(first_int, last_int + 1):
            first_bit = 0 if i > first_int else start % 32
            last_bit = 31 if i < last_int else end % 32
            mask = (2 << last_bit) - (1 << first_bit)
            self.bits[i] |= mask

    def clear(self):
        self.bits = [0] * len(self.bits)

    def is_range(self, start, end, value):
        if end < start or start < 0 or end > self.size:
            raise ValueError("Invalid range")
        if end == start:
            return True
        end -= 1
        first_int = start // 32
        last_int = end // 32
        for i in range(first_int, last_int + 1):
            first_bit = 0 if i > first_int else start % 32
            last_bit = 31 if i < last_int else end % 32
            mask = (2 << last_bit) - (1 << first_bit)
            if (self.bits[i] & mask) != (mask if value else 0):
                return False
        return True

    def append_bit(self, bit):
        self.ensure_capacity(self.size + 1)
        if bit:
            self.bits[self.size // 32] |= 1 << (self.size % 32)
        self.size += 1

    def append_bits(self, value, num_bits):
        if not (0 <= num_bits <= 32):
            raise ValueError("Num bits must be between 0 and 32")
        next_size = self.size
        self.ensure_capacity(next_size + num_bits)
        for num_bits_left in range(num_bits - 1, -1, -1):
            if value & (1 << num_bits_left):
                self.bits[next_size // 32] |= 1 << (next_size % 32)
            next_size += 1
        self.size = next_size

    def append_bit_array(self, other):
        self.ensure_capacity(self.size + other.size)
        for i in range(other.size):
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
            array[offset + i] = the_byte

    def get_bit_array(self):
        return self.bits

    def reverse(self):
        new_bits = [0] * len(self.bits)
        len_bits = (self.size - 1) // 32
        old_bits_len = len_bits + 1
        for i in range(old_bits_len):
            new_bits[len_bits - i] = bin(self.bits[i])[::-1]
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

    def __eq__(self, other):
        if not isinstance(other, BitArray):
            return False
        return self.size == other.size and self.bits == other.bits

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
        return BitArray(self.size).from_array(self.bits)

    def from_array(self, bits):
        self.bits = bits
        return self
