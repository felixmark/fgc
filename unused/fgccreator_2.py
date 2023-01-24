from ..fgc_tools.fgcdrawer import FGCDrawer
from bitarray import bitarray
from .hamming_2 import *
from ..fgc_tools.libs.binarytools import *


class FGCCreator:
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    # FG Code constants
    VERSION_BITS = 4
    VERSION = 1

    @staticmethod
    def create_fgc(data, output_file, color_inner, color_outer, color_background, write_data_as_text) -> None:
        """Creates an fgc according to the given parameters."""

        print("=" * 80)
        print("Version: %i" % FGCCreator.VERSION)
        print("Data:    %s" % data)

        encoded_version = encode_version(FGCCreator.VERSION)
        encoded_data = encode_data(data)

        decoded_version = decode_version(encoded_version)
        decoded_data = decode_data(encoded_data)

        sanity_check = (decoded_data == data and decoded_version == FGCCreator.VERSION)
        print(f"Sanity:  {'PASSED' if sanity_check else 'FAILED! PLEASE CHECK INPUT AND HAMMING CODE.'}.")

        full_encoded_data = bitarray(encoded_version) + bitarray(encoded_data)

        # Draw the actual simple vector graphic (svg)
        FGCDrawer.draw_fgc(
            data, 
            full_encoded_data, 
            output_file, 
            color_inner=color_inner, 
            color_outer=color_outer,
            color_background=color_background,
            write_data_as_text=write_data_as_text
        )
