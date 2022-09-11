import math
from fgcdrawer import FGCDrawer
from bitarray import bitarray
from bitarray.util import serialize, deserialize
from enum import Enum
from libs.hamming import *
from libs.binarytools import *


class FGCCreator():
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    # Code constants
    VERSION_BITS = 4
    VERSION = 1


    @staticmethod
    def create_fgc(data, output_file, color_start="#008060", color_end="#006080"):

        all_data:bitarray = bitarray()

        print("="*80)
        print("Version: %i" % FGCCreator.VERSION)
        print("Data:    %s" % data)

        version_bits = byte_to_bitarray(FGCCreator.VERSION, FGCCreator.VERSION_BITS)
        all_data.extend(version_bits)
        data_bits = string_to_bitarray(data)
        all_data.extend(data_bits)
        
        print("="*80)
        print("Raw data:")
        print_bitarray(all_data)

        # Apply Error Correction
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

        FGCDrawer.draw_fgc(
            data, 
            all_data, 
            output_file, 
            color_start=color_start,
            color_end=color_end
        )
