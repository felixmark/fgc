from bitarray import bitarray


def print_bitarray(bit_array, end="\n"):
    current_bit = 0
    bits_per_line = 60
    for bit in bit_array:
        current_bit += 1
        print("%i" % (1 if bit else 0), end="")
        if current_bit % bits_per_line == 0:
            print()
        elif current_bit % 4 == 0:
            print("", end=" ")
    print("", end=end)

def version_to_bitarray(string):
    bit_array: bitarray = bitarray()
    for c in string:
        bit_array.extend(byte_to_bitarray(c, 4))
    return bit_array

def string_to_bitarray(string):
    bit_array: bitarray = bitarray()
    for c in string:
        print("CHARACTER:", c)
        length_in_bits = 8 * ((int(ord(c)) // 32766) + 1)
        bit_array.extend(byte_to_bitarray(c, length_in_bits))
    return bit_array

def byte_to_bitarray(data, lenght_in_bits):
    bit_array: bitarray = bitarray()
    if type(data) == str:
        data = ord(data)
    for i in range(lenght_in_bits):
        bit_array.append((bool)((data >> i) & 1))
    return bit_array[::-1]
