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
    output_file_name: str = "fgc.svg"
    color_start: str = "#009060"
    color_end: str = "#006090"
    background_color: str = None

    # Store arguments into variables
    argument_count: int = len(sys.argv)
    if argument_count > 1:
        data = sys.argv[1]
        data = data.replace("\\n", "\n")
    if argument_count > 2:
        output_file_name = sys.argv[2]
    if argument_count > 4:
        color_start = sys.argv[3]
        color_end = sys.argv[4]
    if argument_count > 5:
        background_color = sys.argv[5]
    

    print("Fancy Galaxy Code (FGC) creator")
    FGCCreator.create_fgc(
        color_start=color_start, 
        color_end=color_end,
        data=data, 
        output_file=output_file_name,
        background_color=background_color
    )


if __name__ == "__main__":
    main()
