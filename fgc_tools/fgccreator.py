from .fgcdrawer import FGCDrawer
from bitarray import bitarray
from .libs.hamming import *
from .libs.binarytools import *
from .libs.commonfunctions import CommonFunctions


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

        CommonFunctions.print_seperation_line("=")
        print("Version:  %i" % FGCCreator.VERSION)
        print("Data:     %s" % data)

        # Convert version and data to bitarray
        version_bits = byte_to_bitarray(FGCCreator.VERSION, FGCCreator.VERSION_BITS)
        all_data.extend(version_bits)
        data_bits2 = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
        data_bits = bitarray(data_bits2)
        all_data.extend(data_bits)

        print("Binary:   ", end="")
        print_bitarray(all_data)

        # Add Hamming error correction bits
        str_data = all_data.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_encoded = bitarray(hamming_code(str_data))

        print("Hamming:  ", end="")
        print_bitarray(all_data_encoded)

        str_data = all_data_encoded.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_decoded = bitarray(hamming_decode(str_data))

        sanity_check = (all_data_decoded == all_data)
        print(f"Sanity:   {'PASSED' if sanity_check else 'FAILED! PLEASE CHECK INPUT AND HAMMING CODE.'}.")

        CommonFunctions.print_seperation_line("=")

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
