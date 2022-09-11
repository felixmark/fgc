import math
import svgwrite
import base64
from libs.binarytools import print_bitarray
from colour import Color


class FGCDrawer:

    CIRCLE_DISTANCE = 3
    STROKE_WIDTH = 2
    CSS_FILE = "static/style.css"

    def draw_data_as_ring(drawing, shapes, ring_number, data):
        vector_length = (
            FGCDrawer.CIRCLE_DISTANCE * 2 + ring_number * FGCDrawer.CIRCLE_DISTANCE
        )
        degree_per_bit = max(5, max(1, 20 / max(1, ring_number / 2)))
        number_of_bits_in_ring = (360 // int(degree_per_bit)) - 1
        my_data = data[0:number_of_bits_in_ring]
        unprocessed_data = data[number_of_bits_in_ring:]
        my_data.insert(0, False)  # Insert 0 at the beginning of every ring
        skip_bits = 0

        shapes.append(drawing.g(id=str(ring_number)))

        if len(unprocessed_data) == 0 and len(my_data) + 3 < number_of_bits_in_ring:
            # If orientation dot fits into outer ring, put it there
            shapes[0].add(
                drawing.circle(
                    center=(0, -(vector_length)), r=FGCDrawer.STROKE_WIDTH / 2
                )
            )
            my_data.insert(0, False)  # Insert 0 at the beginning which will get skipped
            skip_bits = 1
        elif len(unprocessed_data) == 0:
            # If orientation dot does not fit into out ring put it in extra layer
            shapes[0].add(
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
                FGCDrawer.addArc(
                    drawing=drawing,
                    shape=shapes[ring_number],
                    radius=vector_length,
                    angle_a=current_angle,
                    angle_b=next_angle,
                )
            else:
                # Draw dot
                x_pos, y_pos = FGCDrawer.polarToCartesian(
                    0, 0, radius=vector_length, angleInDegrees=current_angle
                )
                shapes[ring_number].add(
                    drawing.circle(center=(x_pos, y_pos), r=FGCDrawer.STROKE_WIDTH / 2)
                )

        print("Bit capacity:     %i" % number_of_bits_in_ring)
        print("Processed bits:   %i" % len(my_data))
        print("Unprocessed bits: %i" % len(unprocessed_data))

        return unprocessed_data

    def polarToCartesian(centerX, centerY, radius, angleInDegrees):
        angleInRadians = (angleInDegrees - 90) * math.pi / 180.0
        return (
            centerX + (radius * math.cos(angleInRadians)),
            centerY + (radius * math.sin(angleInRadians)),
        )

    def addArc(drawing, shape, radius, angle_a=0, angle_b=0, center_x=0, center_y=0):
        """Adds an Arc to the svg"""
        start_x, start_y = FGCDrawer.polarToCartesian(
            center_x, center_y, radius, angle_b
        )
        end_x, end_y = FGCDrawer.polarToCartesian(center_x, center_y, radius, angle_a)

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

    def draw_fgc(data, all_data, output_file, color_start, color_end):
        color_start = Color(color_start)
        color_end = Color(color_end)

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
        with open(FGCDrawer.CSS_FILE, "r") as file:
            css = file.read()
        drawing.defs.add(drawing.style(css))
        drawing.add(
            drawing.rect(
                insert=(-width / 2, -width / 2),
                size=(width, height),
                rx=None,
                ry=None,
                fill="#f0f0f0",
            )
        )
        shapes = [drawing.g(id="basic-shapes")]

        unprocessed_data: list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = FGCDrawer.draw_data_as_ring(
                drawing=drawing,
                shapes=shapes,
                ring_number=ring_number,
                data=unprocessed_data,
            )
            ring_number += 1

        # Inner circles for distance measure and orientation
        # Center
        shapes[0].add(drawing.circle(center=(0, 0), r=FGCDrawer.STROKE_WIDTH * 2))
        # Orientation
        shapes[0].add(
            drawing.circle(
                center=(0, -FGCDrawer.CIRCLE_DISTANCE * 2), r=FGCDrawer.STROKE_WIDTH / 2
            )
        )
        # First arc for distance measure
        FGCDrawer.addArc(
            drawing=drawing,
            shape=shapes[0],
            radius=FGCDrawer.CIRCLE_DISTANCE * 2,
            angle_a=30,
            angle_b=330,
        )
        # Data as text
        current_line = 0
        for line in data.split("\n"):
            shapes[0].add(
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

        # Apply some color
        colors = list(color_start.range_to(color_end, len(shapes) - 1))
        print("=" * 80)
        print("Color start: %s" % color_start)
        print("Color end:   %s" % color_end)
        for i, shape in enumerate(shapes):
            if i == 0:
                color = "black"
            else:
                color = colors[i - 1]
            for element in shape.elements:
                attributes = {}
                if type(element) == svgwrite.shapes.Circle:
                    attributes["fill"] = color
                elif type(element) == svgwrite.path.Path:
                    attributes["stroke"] = color
                element.update(attributes)
            # Add all shapes to drawing
            drawing.add(shape)

        # Save drawing to svg file
        print("=" * 80)
        print("Saving svg file...")
        drawing.save()
        print("Done.")
