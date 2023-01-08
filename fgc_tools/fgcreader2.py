import numpy as np
import cv2
import time
from .cvfunctions import *
from .featurehandler import *
from bitarray import bitarray
from .libs.hamming import *


# Currently used fgc reader

class FGCReader():


    def read_image(image_path) -> str:

        # Run operations on img and draw on output_img
        img = cv2.imread(image_path)
        output_img = cv2.imread(image_path)


        # Brightness, Contrast increase
        img = set_brightness_contrast(img, 200, 180)

        # show_image("Contrast improved of: " + image_path, img)

        # Features is used to store a lot of useful information 
        features = {
            "center_coordinates": None,
            "center_circle": None,
            "orientation_ring": None,
            "orientation_dot": None,
            "hough_circle_positions": None,
            "hough_circles": None
        }

        # Get image dimensions
        height = img.shape[0]
        width = img.shape[1]

        # Print some information
        print("="*60)
        print("Image:  " + image_path)
        print("Width:  %i" % width)
        print("Height: %i" % height)

        # Measure time of calculations for optimization purposes (since it will be re-written in C++ for mobile devices later)
        start_time = time.time()

        # Calculate some alternative representations of the input image
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 5)
        _, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
        # show_image("Binary of: " + image_path, binary_img)
        # hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    # Not needed yet

        print("Result: ", end="")
        if find_circle_positions_with_hough_transform(blurred_gray_img, features):
            if find_center_with_contours(binary_img, features):
                print("FOUND center of fgc!")

                # Now that we've found the center circle of the fgc, do some more examination of the data and contours
                find_orientation_dot(features)
                sanitize_data(features)
                get_all_angles(features)
                divide_elements_into_rings_by_angle_and_distance(features)
                get_data_from_rings(features)

                # Print some info on the output image
                cv2.circle(output_img, [features["center_coordinates"][0], features["center_coordinates"][1]], 4, (255,255,255), 2)

                for target_position in features["target_positions"]:
                    cv2.drawMarker(output_img, target_position, (255,0,0), cv2.MARKER_DIAMOND, 5, 3)

                for ring_id, ring in enumerate(features["rings"]):
                    for element_id, element in enumerate(ring):
                        cv2.circle(output_img, [element["x"], element["y"]], 4, (255,255,0), 1)

                        outline_color = (255,255,0)
                        if ring_id % 2:
                            outline_color = (0,255,255)
                        cv2.drawContours(output_img,[element["contour"]],0,outline_color,2)

                        cv2.putText(
                            output_img, 
                            str(ring_id) + ":" + str(element_id), 
                            (element["x"], element["y"] - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, (0,190,0), 1, cv2.LINE_AA
                        )
                        cv2.putText(
                            output_img, 
                            str(int(element["angle"])) + " deg", 
                            (element["x"], element["y"]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, (190,0,0), 1, cv2.LINE_AA
                        )
                        cv2.putText(
                            output_img, 
                            str(int(element["furthest_distance_to_center"])), 
                            (element["x"], element["y"] + 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, (0,0,190), 1, cv2.LINE_AA
                        )

                # Draw outline of center and orientation ring
                cv2.drawContours(output_img, [features["center_circle"]], 0, (0, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_ring"]], 0, (0, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_dot"]["contour"]], 0, (0, 255, 0), 2)
            else:
                print("Could not find outline of circle.")
        else:
            print("Could not find fgc at all.")

        raw_binary_string = ''.join([str(ch) for ch in features["data"]])
        read_time = (time.time() - start_time)
        show_image("Result of " + image_path, output_img)
        

        all_data_decoded = hamming_decode(features["data"])
        version = all_data_decoded[:4]
        text = all_data_decoded[4:]
        binary_string = ''.join([str(ch) for ch in text])

        str_data = "".join([chr(int(x,2)) for x in [
                binary_string[i:i+8] for i in range(0,len(binary_string), 8)
            ]
        ])[:-1]

        return (str_data, version, read_time, raw_binary_string)
