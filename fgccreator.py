import svgwrite
import math
from bitarray import bitarray
from bitarray.util import serialize, deserialize
from enum import Enum
from hamming import *


class FGCCreator():
    """FGC Creator is used to create a Fancy Galaxy Code (FGC).
    """

    # Code constants
    VERSION_BITS = 4
    VERSION = 1

    # Draw constants
    CIRCLE_DISTANCE = 3
    STROKE_WIDTH = 2

    def __init__(self):
        self.color = None

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
    def int_from_bytes(self, xbytes: bytes) -> int:
        return int.from_bytes(xbytes, 'big')

    def string_to_binary_list(self, string):
        bit_array:bitarray = bitarray()
        for c in string:
            bit_array.extend(self.byte_to_binary_list(c, 8))
        return bit_array

    def byte_to_binary_list(self, data, lenght_in_bits):
        bit_array:bitarray = bitarray()
        if type(data) == str:
            data = ord(data)
        for i in range(lenght_in_bits):
            bit_array.append((bool) ((data >> i) & 1))
        return bit_array[::-1]

    def print_bitarray(self, binary_list, end="\n"):
        current_bit = 0
        for bit in binary_list:
            current_bit += 1
            print("%i" % (1 if bit else 0), end="")
            current_bit = current_bit % 60
            if current_bit == 0:
                print()
            if current_bit % 4 == 0:
                print("", end=" ")
        print("", end=end)

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
                x_pos, y_pos = self.polarToCartesian(0, 0, radius=vector_length, angleInDegrees=current_angle)
                self.shapes.add(self.drawing.circle(center=(x_pos, y_pos), r=self.STROKE_WIDTH/2))
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
                stroke=stroke, stroke_width=self.STROKE_WIDTH
            )
        )
    
    def create_fgc(self, data, output_file, color="#1060a0"):
        self.color = color

        all_data:bitarray = bitarray()

        print("="*80)
        print("Version: %i" % self.VERSION)
        print("Data:    %s" % data)

        version_bits = self.byte_to_binary_list(self.VERSION, self.VERSION_BITS)
        all_data.extend(version_bits)
        data_bits = self.string_to_binary_list(data)
        all_data.extend(data_bits)
        
        print("="*80)
        print("Raw data:")
        self.print_bitarray(all_data)

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
        while len(all_data) % 16 != 0:
            all_data.append(0)
        print("Original data extended to have a multiple of 16 bits:")
        self.print_bitarray(all_data)
        
        str_data = all_data.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_encoded = bitarray(hamming_code(str_data))

        print("Hamming encoded data:")
        self.print_bitarray(all_data_encoded)

        str_data = all_data_encoded.to01()
        str_data = [int(bit) for bit in str_data]
        all_data_decoded = bitarray(hamming_decode(str_data))

        print("Hamming decoded data:")
        self.print_bitarray(all_data_decoded)

        # Adding terminating 0
        all_data = all_data_encoded
        all_data.append(False)

        print("="*80)
        print("Error correction and termination added:")
        self.print_bitarray(all_data)

        # Inverting all bits
        all_data = ~all_data

        print("="*80)
        print("Inverted final data:")
        self.print_bitarray(all_data)
        print("="*80)

        unprocessed_data:list = all_data
        ring_number = 1
        while len(unprocessed_data) > 0:
            unprocessed_data = self.draw_data_as_ring(ring_number=ring_number, data=unprocessed_data)
            ring_number += 1

        # Inner circles for distance measure and orientation
        # Center
        self.shapes.add(self.drawing.circle(center=(0, 0), r=self.STROKE_WIDTH*2, fill='black'))
        # Orientation
        self.shapes.add(self.drawing.circle(center=(0, -self.CIRCLE_DISTANCE*2), r=self.STROKE_WIDTH/2, fill='black'))
        # First circle for distance measure
        end_l_x, end_l_y = self.polarToCartesian(0, 0, radius=2*self.CIRCLE_DISTANCE, angleInDegrees=45)
        end_r_x, end_r_y = self.polarToCartesian(0, 0, radius=2*self.CIRCLE_DISTANCE, angleInDegrees=315)
        self.shapes.add(self.drawing.circle(center=(end_l_x, end_l_y), r=self.STROKE_WIDTH/2, fill='black'))
        self.shapes.add(self.drawing.circle(center=(end_r_x, end_r_y), r=self.STROKE_WIDTH/2, fill='black'))
        self.addArc(radius=self.CIRCLE_DISTANCE*2, stroke='black', angle_a=45, angle_b=315)

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