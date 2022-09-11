#!/usr/bin/env python3
"""Fancy Galaxy Code (FGC) entrypoint.

Before execution you have to install the requirements by executing:
pip install -r requirements.txt

Execution:
python3 main.py 'Content of fgc' outputfile.svg
"""

import sys
from fgccreator import FGCCreator


def main() -> None:
    """Entrypoint for creating an FGC."""
    data: str = ""
    file_name: str = "fgc.svg"
    argument_count: int = len(sys.argv)

    # Store arguments into variables
    if argument_count > 1:
        data = sys.argv[1]
    if argument_count > 2:
        file_name = sys.argv[2]

    print("Fancy Galaxy Code (FGC) creator")
    fgc_creator = FGCCreator.create_fgc(
        color_start="#009060", color_end="#006090", data=data, output_file=file_name
    )


if __name__ == "__main__":
    main()
