from .fgcdrawer import FGCDrawer
from bitarray import bitarray
from .libs.hamming import *
from .libs.binarytools import *


class FGCCreator:
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    # FG Code constants
    VERSION_BITS = 4
    VERSION = 1

    @staticmethod
    def create_fgc(data, output_file, color_inner, color_outer, color_background, write_data_as_text) -> None:
        """Creates an fgc according to the given parameters."""
        all_data: bitarray = bitarray()

        print("=" * 80)
        print("Version: %i" % FGCCreator.VERSION)
        print("Data:    %s" % data)

        # Convert version and data to bitarray
        version_bits = byte_to_bitarray(FGCCreator.VERSION, FGCCreator.VERSION_BITS)
        all_data.extend(version_bits)
        data_bits = string_to_bitarray(data)
        all_data.extend(data_bits)

        print("=" * 80)
        print("Raw data:")
        print_bitarray(all_data)

        # Add Hamming error correction bits
        str_data = all_data.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_encoded = bitarray(hamming_code(str_data))

        print("Hamming encoded data:")
        print_bitarray(all_data_encoded)

        str_data = all_data_encoded.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_decoded = bitarray(hamming_decode(str_data))

        print("Hamming decoded data (check):")
        print_bitarray(all_data_decoded)

        print("=" * 80)
        print("Error correction bits added (final data):")
        print_bitarray(all_data_encoded)
        print("=" * 80)

        # Draw the actual simple vector graphic (svg)
        FGCDrawer.draw_fgc(
            data, 
            all_data_encoded, 
            output_file, 
            color_inner=color_inner, 
            color_outer=color_outer,
            color_background=color_background,
            write_data_as_text=write_data_as_text
        )
