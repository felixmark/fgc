"""Fancy Galaxy Code (FGC) entrypoint.
"""

import sys
from fgccreator import FGCCreator


def main():
    """Entry Point for creating an FGC."""
    data = ""
    file_name = "fgc.svg"
    argument_count = len(sys.argv)
    
    if argument_count > 1:
        data = sys.argv[1]
    if argument_count > 2:
        file_name = sys.argv[2]

    print("Fancy Galaxy Code creator")
    fgc_creator = FGCCreator()
    fgc_creator.create_fgc(
        color_start="#008060",
        color_end="#006080",
        data=data,
        output_file=file_name
    )

if __name__ == '__main__':
    main()