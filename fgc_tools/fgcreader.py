import numpy as np
import cv2
import time
from bitarray import bitarray
from .cvfunctions import *
from .featurehandler import *
from .libs.hamming import *
import struct
import traceback


# Currently used fgc reader

class FGCReader():

    def read_image(image_path=None, image_file=None) -> str:
        np.seterr(invalid='ignore')

        # Run operations on img and draw on output_img
        if image_path:
            img = cv2.imread(image_path)
        elif image_file:
            image_path = "Memory"
            img = cv2.imdecode(np.fromstring(image_file, np.uint8), 1)
        else:
            return ("", [], 0, "-", None, None)

        # Get image dimensions
        height = img.shape[0]
        width = img.shape[1]
        print("Width:  ", width)
        print("Height: ", height)

        # Resize images if they are too large
        max_w_h = 2500
        if width > height and width > max_w_h:
            img = image_resize(img, width=max_w_h)
        elif height > max_w_h:
            img = image_resize(img, height=max_w_h)

        # Get image dimensions after resize
        height = img.shape[0]
        width = img.shape[1]

        # Features is used to store a lot of useful information 
        features = {
            "center_coordinates": None,
            "center_circle": None,
            "orientation_ring": None,
            "orientation_dot": None,
            "hough_circle_positions": None,
            "hough_circles": None
        }

        # Measure time of calculations for optimization purposes (since it will be re-written in C++ for mobile devices later)
        start_time = time.time()

        # Calculate some alternative representations of the input image
        output_img = img.copy()
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 7)
        _, binary_img = cv2.threshold(gray_img, 128, 255, cv2.THRESH_BINARY)

        if find_circle_positions_with_hough_transform(blurred_gray_img, features):
            if find_center_with_contours(binary_img, img, output_img, features):

                # Now that we've found the center circle of the fgc, do some more examination of the data and contours
                find_orientation_dot(features)
                sanitize_data(features)
                get_all_angles(features)
                divide_elements_into_rings_by_angle_and_distance(features)
                get_data_from_rings(features)

                # Print some info on the output image
                cv2.circle(output_img, (features["center_coordinates"][0], features["center_coordinates"][1]), 4, (255,255,255), 2)

                for target_position in features["target_positions"]:
                    cv2.drawMarker(output_img, (target_position[0], target_position[1]), (0,255,0), cv2.MARKER_TILTED_CROSS, 5, 1)

                for ring_id, ring in enumerate(features["rings"]):
                    for element_id, element in enumerate(ring):
                        # cv2.circle(output_img, (element["x"], element["y"]), 4, (255,255,0), 1)

                        outline_color = (255,255,0)
                        if ring_id % 2:
                            outline_color = (0,255,255)
                        cv2.drawContours(output_img, [element["contour"]], 0, outline_color, 1)

                        # cv2.putText(
                        #     output_img, 
                        #     str(ring_id) + ":" + str(element_id), 
                        #     (element["x"], element["y"] - 15), 
                        #     cv2.FONT_HERSHEY_SIMPLEX, 
                        #     0.5, (0,190,0), 1, cv2.LINE_AA
                        # )
                        # cv2.putText(
                        #     output_img, 
                        #     str(int(element["angle"])) + " deg", 
                        #     (element["x"], element["y"]), 
                        #     cv2.FONT_HERSHEY_SIMPLEX, 
                        #     0.5, (190,0,0), 1, cv2.LINE_AA
                        # )
                        # cv2.putText(
                        #     output_img, 
                        #     str(int(element["furthest_distance_to_center"])), 
                        #     (element["x"], element["y"] + 15), 
                        #     cv2.FONT_HERSHEY_SIMPLEX, 
                        #     0.5, (0,0,190), 1, cv2.LINE_AA
                        # )

                # Draw outline of center and orientation ring
                cv2.drawContours(output_img, [features["center_circle"]], 0, (0, 0, 255), 1)
                cv2.drawContours(output_img, [features["orientation_ring"]], 0, (0, 0, 255), 1)
                cv2.drawContours(output_img, [features["orientation_dot"]["contour"]], 0, (0, 255, 0), 1)

                print("Processed FGC successfully.")
            else:
                print("Could not find center of circle.")
        else:
            print("Could not find FGC at all.")
        
        read_time = (time.time() - start_time)

        try:
            raw_binary_string = ''.join([str(ch) for ch in features["data"]])
            raw_binary_string = raw_binary_string.strip()
            print("RAW binary string:", raw_binary_string)

            raw_binary_bitarray = bitarray(raw_binary_string)
            str_data = raw_binary_bitarray.to01()
            str_data = [int(bit) for bit in str_data]
            all_data_decoded = bitarray(hamming_decode(str_data))
            print("DECODED binary string:", raw_binary_string)

            version = all_data_decoded[:4].to01()
            text = all_data_decoded[4:].to01()

            output = []
            skip_bytes = 0
            # iterate over the binary string in chunks of 8 bits
            for i in range(0, len(text), 8):
                if skip_bytes > 0:
                    skip_bytes -= 1
                    continue

                # convert 8 bits to an integer
                int_data = int(text[i:i+8], 2)
                # pack the integer as a utf-32-be encoded bytes object
                bytes_object = struct.pack('>I', int_data)
                # convert the bytes object to a utf-32-be encoded string
                str_data = bytes_object.decode('utf-32-be')

                if int_data == 0:
                    print("FOUND UTF-32 CHARACTER!")
                    int_data = int(text[i:i+32], 2)
                    bytes_object = struct.pack('>I', int_data)
                    str_data = bytes_object.decode('utf-32-be')
                    skip_bytes = 3

                output.append(str_data)
            text = str("".join(output))


            # Strip all 0s away
            while (text[-1] == "\0"):
                text = text[:-1]

            return (text, version, read_time, raw_binary_string, output_img, binary_img)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            return ("", [], read_time, "-", output_img, binary_img)
