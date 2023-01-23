import math
from typing import Tuple
import svgwrite
import os
from .libs.binarytools import print_bitarray
from colour import Color
from .libs.commonfunctions import CommonFunctions


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
        degrees_per_bit = CommonFunctions.get_degrees_per_bit(ring_number)
        number_of_bits_in_ring = (360 // int(degrees_per_bit))
        my_data = data[0:number_of_bits_in_ring-1]
        unprocessed_data = data[number_of_bits_in_ring-1:]
        my_data.insert(0, False)  # Insert 0 at the beginning of every ring (important for decoding)

        # Add a new group, where bits will be drawn
        groups.append(drawing.g(id=str(ring_number)))

        print()
        print("Ring #%i" % ring_number)
        CommonFunctions.print_seperation_line("-")
        print("Data:             ", end="")
        print_bitarray(my_data)
        print("Degrees per bit:  %i" % degrees_per_bit)

        # Draw all data bits in ring
        for i in range(0, len(my_data)):
            current_angle = degrees_per_bit * i
            if (i < len(my_data) - 1 and my_data[i] == my_data[i + 1]) or (
                i == len(my_data) - 1 and my_data[i] == my_data[0] and len(my_data) == number_of_bits_in_ring
            ):
                # Draw arc
                next_angle = current_angle + degrees_per_bit
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
        print()

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
                "M", str(start_x), str(start_y),
                "A", str(radius), str(radius),
                "0", largeArcFlag,
                "0", str(end_x), str(end_y),
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

    def draw_fgc(data, all_data, output_file, color_inner, color_outer, color_background, write_data_as_text) -> None:
        """Draws the given data bits as a fancy galaxy code svg."""
        color_inner = Color(color_inner)
        color_outer = Color(color_outer)

        # Determine size by amount of data that has to be processed
        width = 50 + (len(all_data) / 4)
        height = 50 + (len(all_data) / 4)
        drawing = svgwrite.Drawing(
            filename=output_file,
            size=('200mm', '200mm'),
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
        groups[0].add(drawing.circle(center=(0, 0), r=FGCDrawer.STROKE_WIDTH * 2, stroke="none"))

        # Orientation
        groups[0].add(
            drawing.circle(
                center=(0, -FGCDrawer.CIRCLE_DISTANCE * 2), r=FGCDrawer.STROKE_WIDTH / 2, stroke="none",
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
        if write_data_as_text:
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

        # Append css to svg for style (especially included font)
        if write_data_as_text:
            with open(FGCDrawer.CSS_FILE, "r") as file:
                css = file.read()
            drawing.defs.add(drawing.style(css))

        # Add background if wanted 
        if color_background is not None:
            drawing.add(
                drawing.circle(
                    center=(0, 0), 
                    fill=color_background,
                    r=(FGCDrawer.STROKE_WIDTH * 3.5) + ((FGCDrawer.CIRCLE_DISTANCE) * ring_number)
                )
            )

        # Apply color to the groups (rings) 
        colors = list(color_inner.range_to(color_outer, len(groups) - 1))
        for i, group in enumerate(groups):
            if i == 0:
                color = "black"
            else:
                color = colors[i - 1]
            for element in group.elements:
                attributes = {}
                if type(element) == svgwrite.shapes.Circle:
                    attributes["fill"] = color
                    attributes["stroke"] = "none"
                elif type(element) == svgwrite.path.Path:
                    attributes["stroke"] = color
                element.update(attributes)
            # Add all shapes to drawing
            drawing.add(group)

        # Save drawing to svg file
        CommonFunctions.print_seperation_line("=")
        print("Saving svg file...")
        drawing.save()
        print("Done.")
