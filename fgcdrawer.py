import math
import svgwrite
import base64
from libs.binarytools import print_bitarray
from colour import Color

class FGCDrawer():

    # Draw constants
    CIRCLE_DISTANCE = 3
    STROKE_WIDTH = 2

    def draw_data_as_ring(self, ring_number, data):
        vector_length = self.CIRCLE_DISTANCE * 2 + ring_number * self.CIRCLE_DISTANCE
        degree_per_bit = max(5, max(1, 20 / max(1, ring_number / 2)))
        number_of_bits_in_ring = (360 // int(degree_per_bit)) - 1
        my_data = data[0:number_of_bits_in_ring]
        unprocessed_data = data[number_of_bits_in_ring:]
        my_data.insert(0, False)   # Insert 0 at the beginning of every ring
        skip_bits = 0

        self.shapes.append(self.drawing.g(id=str(ring_number)))

        if len(unprocessed_data) == 0 and len(my_data) + 3 < number_of_bits_in_ring:
            # If orientation dot fits into outer ring, put it there
            self.shapes[0].add(self.drawing.circle(center=(0, -(vector_length)), r=self.STROKE_WIDTH/2))
            my_data.insert(0, False)   # Insert 0 at the beginning which will get skipped
            skip_bits = 1
        elif len(unprocessed_data) == 0:
            # If orientation dot does not fit into out ring put it in extra layer
            self.shapes[0].add(self.drawing.circle(center=(0, -(vector_length+self.CIRCLE_DISTANCE)), r=self.STROKE_WIDTH/2))
                
        print("-"*80)
        print("Ring #%i" % ring_number)
        print("-"*80)
        print("Data:")
        print_bitarray(my_data)
        print("Degrees per bit:  %i" % degree_per_bit)

        for i in range(0, len(my_data)):
            if skip_bits > 0:
                skip_bits -= 1
                continue
            current_angle = degree_per_bit*i
            if (i < len(my_data) - 1 and my_data[i] == my_data[i+1]) or (i == len(my_data) - 1 and my_data[i] == my_data[0]):
                # Draw arc
                next_angle = current_angle + degree_per_bit
                self.addArc(shape=self.shapes[ring_number], radius=vector_length, angle_a=current_angle, angle_b=next_angle)
            else:
                # Draw dot
                x_pos, y_pos = self.polarToCartesian(0, 0, radius=vector_length, angleInDegrees=current_angle)
                self.shapes[ring_number].add(self.drawing.circle(center=(x_pos, y_pos), r=self.STROKE_WIDTH/2))
                

        print("Bit capacity:     %i" % number_of_bits_in_ring)
        print("Processed bits:   %i" % len(my_data))
        print("Unprocessed bits: %i" % len(unprocessed_data))

        return unprocessed_data

    def polarToCartesian(self, centerX, centerY, radius, angleInDegrees):
        angleInRadians = (angleInDegrees-90) * math.pi / 180.0
        return centerX + (radius * math.cos(angleInRadians)), centerY + (radius * math.sin(angleInRadians))

    def addArc(self, shape, radius, angle_a=0, angle_b=0, center_x=0, center_y=0):
        """Adds an Arc to the svg"""
        start_x, start_y = self.polarToCartesian(center_x, center_y, radius, angle_b)
        end_x, end_y = self.polarToCartesian(center_x, center_y, radius, angle_a)

        largeArcFlag = "0"
        if angle_b - angle_a > 180:
            largeArcFlag = "1"
        
        d = " ".join([
            "M", str(start_x), str(start_y), 
            "A", str(radius), str(radius), "0", largeArcFlag, "0", str(end_x), str(end_y)
        ])
        shape.add(
            self.drawing.path(d=d,
                fill="none", 
                stroke_width=self.STROKE_WIDTH,
                stroke_linecap="round"
            )
        )

    def draw_fgc(self, data, all_data, output_file, color_start, color_end):
        self.color_start = Color(color_start)
        self.color_end = Color(color_end)

        width = 50+(len(all_data)/4)
        height = 50+(len(all_data)/4)
        self.drawing = svgwrite.Drawing(
            filename=output_file, 
            viewBox=(str(-width / 2) + "," + str(-height / 2)+","+str(width)+","+str(height)), 
            debug=True
        )
        with open('static/style.css', 'r') as file:
            css = file.read()
        self.drawing.defs.add(self.drawing.style(css))
        self.drawing.add(self.drawing.rect(insert=(-width / 2, -width / 2), size=(width, height), rx=None, ry=None, fill='#f0f0f0'))
        self.shapes = [self.drawing.g(id='basic-shapes')]

        unprocessed_data:list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = self.draw_data_as_ring(
                ring_number=ring_number, 
                data=unprocessed_data
            )
            ring_number += 1
        
        
        # Inner circles for distance measure and orientation
        # Center
        self.shapes[0].add(self.drawing.circle(center=(0, 0), r=self.STROKE_WIDTH*2, fill='black'))
        # Orientation
        self.shapes[0].add(self.drawing.circle(center=(0, -self.CIRCLE_DISTANCE*2), r=self.STROKE_WIDTH/2, fill='black'))
        # First arc for distance measure
        self.addArc(shape=self.shapes[0], radius=self.CIRCLE_DISTANCE*2, angle_a=30, angle_b=330)        
        # Data as text
        current_line = 0
        for line in data.split("\n"):
            self.shapes[0].add(self.drawing.text(
                line, 
                insert=(0, ring_number * self.CIRCLE_DISTANCE + self.CIRCLE_DISTANCE*4 + current_line * 5), 
                style="font-size:5px; font-weight: bold; text-anchor: middle;",
            ))
            current_line += 1



        # Apply some color
        self.colors = list(self.color_start.range_to(self.color_end, len(self.shapes) - 1))
        print("="*80)
        print("Color start: %s" % color_start)
        print("Color end:   %s" % color_end)
        for i, shape in enumerate(self.shapes):
            if i == 0:
                color = 'black'
            else:
                color = self.colors[i-1]
            for element in shape.elements:
                attributes = {}
                if type(element) == svgwrite.shapes.Circle:
                    attributes['fill'] = color
                elif type(element) == svgwrite.path.Path:
                    attributes['stroke'] = color
                element.update(attributes)
            # Add all shapes to drawing
            self.drawing.add(shape)


        print("="*80)
        print("Saving svg file...")
        self.drawing.save()
        print("Done.")
