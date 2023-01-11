import numpy as np
import cv2
import time
from .cvfunctions import *
from .featurehandler import *
from .libs.hamming import *


# Currently used fgc reader

class FGCReader():

    def read_image(image_path=None, image_file=None) -> str:
        np.seterr(invalid='ignore')

        # Run operations on img and draw on output_img
        if image_path:
            img = cv2.imread(image_path)
            output_img = cv2.imread(image_path)
        elif image_file:
            image_path = "Memory"
            img = cv2.imdecode(np.fromstring(image_file, np.uint8), 1)
            output_img = cv2.imdecode(np.fromstring(image_file, np.uint8), 1)
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
            output_img = image_resize(output_img, width=max_w_h)
        elif height > max_w_h:
            img = image_resize(img, height=max_w_h)
            output_img = image_resize(output_img, height=max_w_h)

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
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 7)
        _, binary_img = cv2.threshold(gray_img, 128, 255, cv2.THRESH_BINARY)
        show_image("Binary of: " + image_path, binary_img)
        # hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    # Not needed yet

        if find_circle_positions_with_hough_transform(blurred_gray_img, features):
            if find_center_with_contours(binary_img, img, features):

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
            show_image("Result of " + image_path, output_img)

            all_data_decoded = hamming_decode(features["data"])
            version = all_data_decoded[:4]
            text = all_data_decoded[4:]
            binary_string = ''.join([str(ch) for ch in text])

            str_data = "".join([chr(int(x,2)) for x in [
                    binary_string[i:i+8] for i in range(0,len(binary_string), 8)
                ]
            ])
            # Strip all 0s away
            while (str_data[-1] == "\0"):
                str_data = str_data[:-1]

            return (str_data, version, read_time, raw_binary_string, output_img, binary_img)
        except:
            return ("", [], read_time, "-", output_img, binary_img)
