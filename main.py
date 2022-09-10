"""Fancy Galaxy Code (FGC) entrypoint.
"""

import sys
from fgccreator import FGCCreator


def main():
    """Entry Point for creating an FGC."""
    data = ""
    argument_count = len(sys.argv)
    
    if argument_count > 1:
        data = sys.argv[1]

    print("Fancy Galaxy Code creator")
    fgc_creator = FGCCreator()
    fgc_creator.create_fgc(
        color="#008070",
        data=data,
        output_file="fgc.svg"
    )

if __name__ == '__main__':
    main()