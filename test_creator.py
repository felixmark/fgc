#!/usr/bin/env python3
"""Fancy Galaxy Code (FGC) entrypoint.

Before execution you have to install the requirements by executing:
pip install -r requirements.txt

Execution:
python3 test_creator.py 'Content of fgc' outputfile.svg
"""

import sys
from fgc_tools import FGCCreator


def main() -> None:
    """Entrypoint for creating an FGC."""
    data: str = ""
    output_file_name: str = "fgc.svg"
    color_inner: str = "#009060"
    color_outer: str = "#006090"
    background_color: str = "#ffffff"
    write_data_as_text = True

    # Store arguments into variables
    argument_count: int = len(sys.argv)
    if argument_count > 1:
        data = sys.argv[1]
        data = data.replace("\\n", "\n")
    if argument_count > 2:
        output_file_name = sys.argv[2]
    if argument_count > 4:
        color_inner = sys.argv[3]
        color_outer = sys.argv[4]
    if argument_count > 5:
        background_color = sys.argv[5]
    if argument_count > 6:
        write_data_as_text = (sys.argv[6].lower() == 'true')
    

    print("Fancy Galaxy Code (FGC) creator")
    FGCCreator.create_fgc(
        color_inner=color_inner, 
        color_outer=color_outer,
        data=data, 
        output_file=output_file_name,
        color_background=background_color,
        write_data_as_text=write_data_as_text
    )


if __name__ == "__main__":
    main()
