import math
from typing import Tuple
import svgwrite
import os
from .libs.binarytools import print_bitarray
from colour import Color


class FGCDrawer:

    # Constants for drawing
    CIRCLE_DISTANCE = 3
    STROKE_WIDTH = 2
    DIRNAME = os.path.dirname(__file__)
    CSS_FILE = os.path.join(DIRNAME, "css/style.css")

    def draw_data_as_ring(drawing, groups, ring_number, data) -> list:
        """Draws a single ring of data bits. The unprocessed bits will be returned."""

        # Calculate radius of the ring and some more properties
        vector_length = (
            FGCDrawer.CIRCLE_DISTANCE * 2 + ring_number * FGCDrawer.CIRCLE_DISTANCE
        )
        degree_per_bit = max(4, max(1, 20 / max(1, ring_number / 2)))
        number_of_bits_in_ring = (360 // int(degree_per_bit)) - 1
        my_data = data[0:number_of_bits_in_ring]
        unprocessed_data = data[number_of_bits_in_ring:]
        my_data.insert(0, False)  # Insert 0 at the beginning of every ring (important for decoding)
        skip_bits = 0

        # Add a new group, where bits will be drawn
        groups.append(drawing.g(id=str(ring_number)))

        # Check if this one is the last ring and add the orientation bit. (Hopefully will be deprecated when decoding works either way)
        if len(unprocessed_data) == 0 and len(my_data) + 3 < number_of_bits_in_ring:
            # If orientation dot fits into outer ring, put it there
            groups[0].add(
                drawing.circle(
                    center=(0, -(vector_length)), r=FGCDrawer.STROKE_WIDTH / 2
                )
            )
            my_data.insert(0, False)  # Insert 0 at the beginning which will get skipped
            skip_bits = 1
        elif len(unprocessed_data) == 0:
            # If orientation dot does not fit into out ring put it in extra layer
            groups[0].add(
                drawing.circle(
                    center=(0, -(vector_length + FGCDrawer.CIRCLE_DISTANCE)),
                    r=FGCDrawer.STROKE_WIDTH / 2,
                )
            )

        print("-" * 80)
        print("Ring #%i" % ring_number)
        print("-" * 80)
        print("Data:")
        print_bitarray(my_data)
        print("Degrees per bit:  %i" % degree_per_bit)

        # Draw all data bits in ring
        for i in range(0, len(my_data)):
            if skip_bits > 0:
                skip_bits -= 1
                continue
            current_angle = degree_per_bit * i
            if (i < len(my_data) - 1 and my_data[i] == my_data[i + 1]) or (
                i == len(my_data) - 1 and my_data[i] == my_data[0]
            ):
                # Draw arc
                next_angle = current_angle + degree_per_bit
                FGCDrawer.add_arc(
                    drawing=drawing,
                    shape=groups[ring_number],
                    radius=vector_length,
                    angle_a=current_angle,
                    angle_b=next_angle,
                )
            else:
                # Draw dot
                x_pos, y_pos = FGCDrawer.polar_to_cartesian(
                    0, 0, radius=vector_length, angleInDegrees=current_angle
                )
                groups[ring_number].add(
                    drawing.circle(center=(x_pos, y_pos), r=FGCDrawer.STROKE_WIDTH / 2)
                )

        print("Bit capacity:     %i" % number_of_bits_in_ring)
        print("Processed bits:   %i" % len(my_data))
        print("Unprocessed bits: %i" % len(unprocessed_data))

        # Return all the unprocessed data
        return unprocessed_data

    def polar_to_cartesian(centerX, centerY, radius, angleInDegrees) -> Tuple:
        """Convert polar coordinates to cartesian coordinates."""
        angleInRadians = (angleInDegrees - 90) * math.pi / 180.0
        return (
            centerX + (radius * math.cos(angleInRadians)),
            centerY + (radius * math.sin(angleInRadians)),
        )

    def add_arc(drawing, shape, radius, angle_a=0, angle_b=0, center_x=0, center_y=0) -> None:
        """Adds an Arc to the svg"""
        start_x, start_y = FGCDrawer.polar_to_cartesian(
            center_x, center_y, radius, angle_b
        )
        end_x, end_y = FGCDrawer.polar_to_cartesian(center_x, center_y, radius, angle_a)

        largeArcFlag = "0"
        if angle_b - angle_a > 180:
            largeArcFlag = "1"

        d = " ".join(
            [
                "M",
                str(start_x),
                str(start_y),
                "A",
                str(radius),
                str(radius),
                "0",
                largeArcFlag,
                "0",
                str(end_x),
                str(end_y),
            ]
        )
        shape.add(
            drawing.path(
                d=d,
                fill="none",
                stroke_width=FGCDrawer.STROKE_WIDTH,
                stroke_linecap="round",
            )
        )

    def draw_fgc(data, all_data, output_file, color_start, color_end, background_color) -> None:
        """Draws the given data bits as a fancy galaxy code svg."""
        color_start = Color(color_start)
        color_end = Color(color_end)

        # Determine size by amount of data that has to be processed
        width = 50 + (len(all_data) / 4)
        height = 50 + (len(all_data) / 4)
        drawing = svgwrite.Drawing(
            filename=output_file,
            viewBox=(
                str(-width / 2)
                + ","
                + str(-height / 2)
                + ","
                + str(width)
                + ","
                + str(height)
            ),
            debug=True,
        )

        # Append css to svg for style (especially included font)
        with open(FGCDrawer.CSS_FILE, "r") as file:
            css = file.read()
        drawing.defs.add(drawing.style(css))

        # Add background if wanted 
        if background_color is not None:
            drawing.add(
                drawing.rect(
                    insert=(-width / 2, -width / 2),
                    size=(width, height),
                    rx=None,
                    ry=None,
                    fill=background_color,
                )
            )

        # Groups of shapes which get colored afterwards
        groups = [drawing.g(id="basic-shapes")]

        # Create the actual rings of data
        unprocessed_data: list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = FGCDrawer.draw_data_as_ring(
                drawing=drawing,
                groups=groups,
                ring_number=ring_number,
                data=unprocessed_data,
            )
            ring_number += 1

        # Draw inner circles for distance measurement and orientation
        # Center
        groups[0].add(drawing.circle(center=(0, 0), r=FGCDrawer.STROKE_WIDTH * 2))
        # Orientation
        groups[0].add(
            drawing.circle(
                center=(0, -FGCDrawer.CIRCLE_DISTANCE * 2), r=FGCDrawer.STROKE_WIDTH / 2
            )
        )
        # First arc for further distance measurement and center targetability
        FGCDrawer.add_arc(
            drawing=drawing,
            shape=groups[0],
            radius=FGCDrawer.CIRCLE_DISTANCE * 2,
            angle_a=30,
            angle_b=330,
        )
        # Draw data as text
        current_line = 0
        for line in data.split("\n"):
            groups[0].add(
                drawing.text(
                    line,
                    insert=(
                        0,
                        ring_number * FGCDrawer.CIRCLE_DISTANCE
                        + FGCDrawer.CIRCLE_DISTANCE * 4
                        + current_line * 5,
                    ),
                    style="font-size:5px; font-weight: bold; text-anchor: middle;",
                )
            )
            current_line += 1

        # Apply color to the groups (rings) 
        colors = list(color_start.range_to(color_end, len(groups) - 1))
        print("=" * 80)
        print("Color start: %s" % color_start)
        print("Color end:   %s" % color_end)
        for i, group in enumerate(groups):
            if i == 0:
                color = "black"
            else:
                color = colors[i - 1]
            for element in group.elements:
                attributes = {}
                if type(element) == svgwrite.shapes.Circle:
                    attributes["fill"] = color
                elif type(element) == svgwrite.path.Path:
                    attributes["stroke"] = color
                element.update(attributes)
            # Add all shapes to drawing
            drawing.add(group)

        # Save drawing to svg file
        print("=" * 80)
        print("Saving svg file...")
        drawing.save()
        print("Done.")
