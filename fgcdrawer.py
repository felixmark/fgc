import math
import svgwrite
import base64

class FGCDrawer():

    # Draw constants
    CIRCLE_DISTANCE = 3
    STROKE_WIDTH = 2

    def draw_data_as_ring(self, ring_number, data):
        vector_length = self.CIRCLE_DISTANCE * 2 + ring_number * self.CIRCLE_DISTANCE
        degree_per_bit = max(4, 30 // ring_number)

        number_of_bits_in_ring = 360 // degree_per_bit
        my_data = data[0:number_of_bits_in_ring]
        unprocessed_data = data[number_of_bits_in_ring:]
        
        print("-"*80)
        print("Ring #%i" % ring_number)
        print("-"*80)
        print("Degrees per bit:  %i" % degree_per_bit)

        for i in range(0, len(my_data)):
            current_angle = degree_per_bit*i
            if my_data[i]:
                #  Draw dot
                self.addArc(radius=vector_length, stroke=self.color, angle_a=current_angle, angle_b=current_angle)
                # Draw Arc if necessary
                if len(my_data) > 1 and i == len(my_data) - 1 and my_data[0] == True and len(unprocessed_data) > 0:
                    self.addArc(radius=vector_length, stroke=self.color, angle_a=current_angle, angle_b=360)
                elif len(my_data) > 1 and i < len(my_data) - 1 and my_data[i+1] == True:
                    next_angle = current_angle + degree_per_bit
                    self.addArc(radius=vector_length, stroke=self.color, angle_a=current_angle, angle_b=next_angle)
            
        print("Bit capacity:     %i" % number_of_bits_in_ring)
        print("Processed bits:   %i" % len(my_data))
        print("Unprocessed bits: %i" % len(unprocessed_data))

        return unprocessed_data

    def polarToCartesian(self, centerX, centerY, radius, angleInDegrees):
        angleInRadians = (angleInDegrees-90) * math.pi / 180.0
        return centerX + (radius * math.cos(angleInRadians)), centerY + (radius * math.sin(angleInRadians))

    def addArc(self, radius, stroke, angle_a=0, angle_b=0, center_x=0, center_y=0):
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
        self.shapes.add(
            self.drawing.path(d=d,
                fill="none", 
                stroke=stroke, stroke_width=self.STROKE_WIDTH,
                stroke_linecap="round"
            )
        )

    def draw_fgc(self, data, all_data, color, output_file):
        self.color = color

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
        self.shapes = self.drawing.add(self.drawing.g(id='shapes', fill=self.color))

        unprocessed_data:list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = self.draw_data_as_ring(ring_number=ring_number, data=unprocessed_data)
            ring_number += 1

        # Inner circles for distance measure and orientation
        # Center
        self.shapes.add(self.drawing.circle(center=(0, 0), r=self.STROKE_WIDTH*2, fill='black'))
        # Orientation
        self.addArc(radius=self.CIRCLE_DISTANCE*2, stroke='black', angle_a=0, angle_b=0)
        # First circle for distance measure
        self.addArc(radius=self.CIRCLE_DISTANCE*2, stroke='black', angle_a=30, angle_b=330)

        # Data as text
        current_line = 0
        for line in data.split("\n"):
            self.drawing.add(self.drawing.text(
                line, 
                insert=(0, ring_number * self.CIRCLE_DISTANCE + self.CIRCLE_DISTANCE*3 + current_line * 5), 
                fill="black",
                style="font-size:5px; font-weight: bold; text-anchor: middle;",
            ))
            current_line += 1

        self.drawing.save()