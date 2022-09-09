"""Fancy Galaxy Code (FGC)
"""

import svgwrite
import math
import sys
from enum import Enum


class CorrectionType(Enum):
    TWO_BITS = 0         # Highest correction
    FOUR_BITS = 1
    EIGHT_BITS = 2
    SIXTEEN_BITS = 3     # Lowest correction


class FGCCreator():
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    VERSION_BITS = 4

    def __init__(self, color="#1060a0", correction_type=CorrectionType.TWO_BITS):
        self.color = color
        self.version = 1
        self.error_correction_type = correction_type

        self.circle_distance = 3
        self.stroke_width = 2

    def string_to_binary_list(self, string):
        binary_list:list = []
        for c in string:
            binary_list.extend(self.byte_to_binary_list(c, 8))
        return binary_list

    def byte_to_binary_list(self, data, lenght_in_bits):
        binary_list:list = []
        if type(data) == str:
            data = ord(data)
        for i in range(lenght_in_bits):
            binary_list.append((bool) ((data >> i) & 1))
        return binary_list[::-1]

    def print_binary_list(self, binary_list, end="\n"):
        current_bit = 0
        for bit in binary_list:
            current_bit += 1
            if bit:
                print("1", end=" ")
            else:
                print("0", end=" ")
            current_bit = current_bit % 40
            if current_bit == 0:
                print()
        print("", end=end)

    def draw_data_as_ring(self, ring_number, data):
        vector_length = self.circle_distance * 2 + ring_number * self.circle_distance
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
                x_pos, y_pos = self.polarToCartesian(0, 0, radius=vector_length, angleInDegrees=current_angle)
                self.shapes.add(self.drawing.circle(center=(x_pos, y_pos), r=self.stroke_width/2))
                # Draw Arc if necessary
                if len(my_data) > 1 and i == len(my_data) - 1 and my_data[0] == True and len(unprocessed_data) > 0:
                    self.addArc(radius=vector_length, stroke=self.color, stroke_width=self.stroke_width, angle_a=current_angle, angle_b=360)
                elif len(my_data) > 1 and i < len(my_data) - 1 and my_data[i+1] == True:
                    next_angle = current_angle + degree_per_bit
                    self.addArc(radius=vector_length, stroke=self.color, stroke_width=self.stroke_width, angle_a=current_angle, angle_b=next_angle)

        print("Bit capacity:     %i" % number_of_bits_in_ring)
        print("Processed bits:   %i" % len(my_data))
        print("Unprocessed bits: %i" % len(unprocessed_data))

        return unprocessed_data

    def polarToCartesian(self, centerX, centerY, radius, angleInDegrees):
        angleInRadians = (angleInDegrees-90) * math.pi / 180.0
        return centerX + (radius * math.cos(angleInRadians)), centerY + (radius * math.sin(angleInRadians))

    def addArc(self, radius, stroke, stroke_width, angle_a=0, angle_b=0, center_x=0, center_y=0):
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
                stroke=stroke, stroke_width=stroke_width
            )
        )
    
    def create_fgc(self, data, output_file):
        all_data = []

        binary_list = self.byte_to_binary_list(self.error_correction_type.value, 2)
        all_data.extend(binary_list)
        binary_list = self.byte_to_binary_list(self.version, FGCCreator.VERSION_BITS)
        all_data.extend(binary_list)
        binary_list = self.string_to_binary_list(data)
        all_data.extend(binary_list)

        print("="*80)
        print("Version: %i" % self.version)
        print("Data:    %s" % data)
        print("="*80)
        print("Raw data:")
        self.print_binary_list(all_data)

        width = 50+(len(all_data)/2)
        height = 50+(len(all_data)/4)
        self.drawing = svgwrite.Drawing(
            filename=output_file, 
            viewBox=(str(-width / 2) + "," + str(-height / 2)+","+str(width)+","+str(height)), debug=True) # draw.Drawing(width, height, origin='center', displayInline=False)
        with open('style.css', 'r') as file:
            css = file.read()
        self.drawing.defs.add(self.drawing.style(css))
        self.shapes = self.drawing.add(self.drawing.g(id='shapes', fill=self.color))

        # Apply Error Correction
        check_bits = []
        b = 0   # Skip error correction type bytes
        while b < len(all_data):
            check_bits.append(all_data[b])
            if len(check_bits) > self.error_correction_type.value + 1:
                xor_value = False
                for check_bit in check_bits:
                    xor_value = xor_value ^ check_bit
                all_data.insert(b, xor_value)
                check_bits.clear()
                b += 1
            b += 1
        # Check remaining bits
        xor_value = False
        for check_bit in check_bits:
            xor_value = xor_value ^ check_bit
        all_data.insert(b+1, xor_value)

        # Adding terminating 0
        all_data.append(False)

        print("="*80)
        print("Error correction and termination added:")
        self.print_binary_list(all_data)

        # Inverting all bits
        for b in range(len(all_data)):
            all_data[b] = not all_data[b]

        print("="*80)
        print("Inverted final data:")
        self.print_binary_list(all_data)
        print("="*80)

        unprocessed_data:list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = self.draw_data_as_ring(ring_number=ring_number, data=unprocessed_data)
            ring_number += 1

        # Inner circles for distance measure and orientation
        # Center
        self.shapes.add(self.drawing.circle(center=(0, 0), r=self.stroke_width*2, fill='black'))
        # Orientation
        self.shapes.add(self.drawing.circle(center=(0, -self.circle_distance*2), r=self.stroke_width/2, fill='black'))
        # First circle for distance measure
        end_l_x, end_l_y = self.polarToCartesian(0, 0, radius=2*self.circle_distance, angleInDegrees=45)
        end_r_x, end_r_y = self.polarToCartesian(0, 0, radius=2*self.circle_distance, angleInDegrees=315)
        self.shapes.add(self.drawing.circle(center=(end_l_x, end_l_y), r=self.stroke_width/2, fill='black'))
        self.shapes.add(self.drawing.circle(center=(end_r_x, end_r_y), r=self.stroke_width/2, fill='black'))
        self.addArc(radius=self.circle_distance*2, stroke='black', stroke_width=self.stroke_width, angle_a=45, angle_b=315)

        # Data as text
        current_line = 0
        for line in data.split("\n"):
            self.drawing.add(self.drawing.text(
                line, 
                insert=(0, ring_number * self.circle_distance + self.circle_distance*3 + current_line * 5), 
                fill="black",
                style="font-size:5px; font-weight: bold; text-anchor: middle;",
            ))
            current_line += 1

        self.drawing.save()

def main():
    data = ""
    argument_count = len(sys.argv)
    
    if argument_count > 1:
        data = sys.argv[1]

    print("Fancy Galaxy Code creator")
    fgc_creator = FGCCreator(
        "#008070",
        correction_type=CorrectionType.FOUR_BITS
    )
    fgc_creator.create_fgc(
        data=data,
        output_file="fgc.svg"
    )

if __name__ == '__main__':
    main()