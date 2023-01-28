import numpy as np
import cv2
import time
from bitarray import bitarray
from .readresult import ReadResult
from .cvfunctions import *
from .featurehandler import *
from .libs.hamming import *
import struct
import traceback


# Currently used fgc reader

class FGCReader():

    def read_image(image_path=None, image_file=None) -> str:
        np.seterr(invalid='ignore')

        read_result = ReadResult()

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
        if width * height > 1_000_000:
            max_w_h = 2500
            resized = True
            if width >= height and width > max_w_h:
                img = image_resize(img, width=max_w_h, inter=cv2.INTER_CUBIC)
            elif height > max_w_h:
                img = image_resize(img, height=max_w_h, inter=cv2.INTER_CUBIC)
            else:
                resized = False
            if resized:
                height = img.shape[0]
                width = img.shape[1]
                print("Resized the image.")
                print("Width:  ", width)
                print("Height: ", height)

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
        blurred_gray_img = cv2.medianBlur(gray_img, 5)
        heavy_blurred_gray_img = cv2.medianBlur(gray_img, 11)
        edged = cv2.Canny(blurred_gray_img, 150, 220)
        # _, binary_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY)
        print("Time conversions:", (time.time() - start_time))

        if find_circle_positions_with_hough_transform(heavy_blurred_gray_img, features):
            print("Time finding circles:", (time.time() - start_time))
            if find_center_with_contours(edged, img, output_img, features):
                print("Time finding center:", (time.time() - start_time))

                # Now that we've found the center circle of the fgc, do some more examination of the data and contours
                find_orientation_dot(features)
                print("Time finding orientation dot:", (time.time() - start_time))
                sanitize_data(features)
                print("Time sanitizing data:", (time.time() - start_time))
                get_all_angles(features)
                print("Time getting angles:", (time.time() - start_time))
                divide_elements_into_rings_by_angle_and_distance(features)
                print("Time dividing elements into rings:", (time.time() - start_time))
                get_data_from_rings(features)
                print("Time getting data:", (time.time() - start_time))

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
                        if ring_id > 1:
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
                cv2.drawContours(output_img, [features["center_circle"]], 0, (0, 255, 0), 2)
                cv2.drawContours(output_img, [features["orientation_dot"]["contour"]], 0, (255, 0, 0), 2)
                cv2.drawContours(output_img, [features["orientation_ring"]], 0, (0, 200, 0), 2)

                print("Processed FGC successfully.")
            else:
                print("Could not find center of circle.")
        else:
            print("Could not find FGC at all.")
        
        # Store read time and output img
        read_result.read_time = (time.time() - start_time)
        read_result.output_img = output_img
        
        try:
            raw_binary_string = ''.join([str(ch) for ch in features["data"]])
            read_result.raw_binary_string = raw_binary_string
            raw_binary_bitarray = bitarray(raw_binary_string)
            str_data = raw_binary_bitarray.to01()
            print("RAW:        ", str_data)
            str_data = [int(bit) for bit in str_data]
            all_data_decoded = bitarray(hamming_decode(str_data))
            print("Decoded:    ", all_data_decoded.to01())

            # Cenvert binary version to int
            read_result.version = int(all_data_decoded[:4].to01(), 2)

            # Convert binary text to utf-8
            text = all_data_decoded[4:].to01()
            output_bytes = []
            # iterate over the binary string in chunks of 8 bits
            for i in range(0, len(text), 8):
                int_byte = int(text[i:i+8], 2)
                output_bytes.append(int_byte.to_bytes(1, byteorder='big'))
            print("Bytes Text:    ", output_bytes)

            # Decode text as far as possible
            utf8_text = None
            while utf8_text is None and len(output_bytes) > 0:
                try:
                    utf8_text = b''.join(output_bytes).decode("utf-8")
                    print("UTF-8 Text:    ", utf8_text)
                except Exception as e:
                    print("Could not decode to utf-8.")
                    print(e)
                    print(traceback.format_exc())
                    read_result.has_error = True
                    output_bytes = output_bytes[:-1]

            # Strip all 0s away
            while (utf8_text[-1] == "\0"):
                utf8_text = utf8_text[:-1]

            read_result.text = utf8_text
            return read_result
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            return read_result
