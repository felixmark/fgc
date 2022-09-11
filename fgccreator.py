import math
from fgcdrawer import FGCDrawer
from bitarray import bitarray
from bitarray.util import serialize, deserialize
from enum import Enum
from libs.hamming import *
from libs.binarytools import print_bitarray


class FGCCreator():
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    # Code constants
    VERSION_BITS = 4
    VERSION = 1

    def __init__(self):
        self.color = None

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
    def int_from_bytes(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, 'big')

    def string_to_binary_list(self, string):
        bit_array:bitarray = bitarray()
        for c in string:
            bit_array.extend(self.byte_to_binary_list(c, 8))
        return bit_array

    def byte_to_binary_list(self, data, lenght_in_bits):
        bit_array:bitarray = bitarray()
        if type(data) == str:
            data = ord(data)
        for i in range(lenght_in_bits):
            bit_array.append((bool) ((data >> i) & 1))
        return bit_array[::-1]

    def create_fgc(self, data, output_file, color_start="#008060", color_end="#006080"):

        all_data:bitarray = bitarray()

        print("="*80)
        print("Version: %i" % self.VERSION)
        print("Data:    %s" % data)

        version_bits = self.byte_to_binary_list(self.VERSION, self.VERSION_BITS)
        all_data.extend(version_bits)
        data_bits = self.string_to_binary_list(data)
        all_data.extend(data_bits)
        
        print("="*80)
        print("Raw data:")
        print_bitarray(all_data)

        # Apply Error Correction
        while len(all_data) % 16 != 0:
            all_data.append(0)
        print("Original data extended to have a multiple of 16 bits:")
        print_bitarray(all_data)
        
        str_data = all_data.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_encoded = bitarray(hamming_code(str_data))

        print("Hamming encoded data:")
        print_bitarray(all_data_encoded)

        # All data should be the encoded data
        all_data = all_data_encoded

        str_data = all_data_encoded.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_decoded = bitarray(hamming_decode(str_data))

        print("Hamming decoded data (check):")
        print_bitarray(all_data_decoded)

        print("="*80)
        print("Error correction bits added (final data):")
        print_bitarray(all_data)
        print("="*80)

        fgc_drawer = FGCDrawer()
        fgc_drawer.draw_fgc(
            data, 
            all_data, 
            output_file, 
            color_start=color_start,
            color_end=color_end
        )
