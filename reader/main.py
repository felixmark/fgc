import numpy as np
import cv2
# import imutils
from centerfinder import *
import matplotlib.pyplot as plt
import time


def show_image(index, image) -> None:
    """Displays an image."""
    resize_factor = 4
    h, w = image.shape[:2]
    h = int(h / resize_factor)
    w = int(w / resize_factor)

    plt_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(index)
    plt.imshow(plt_image)
    plt.show(block=False)


def main() -> None:
    print("FGC Reader started")

    # List of test images with their expected content
    test_images = [
        { "img": 'test_images/1.jpg', "content": "Example" },
        { "img": 'test_images/2.jpg', "content": "Milch." },
        { "img": 'test_images/3.jpg', "content": "Milch." },
        { "img": 'test_images/4.jpg', "content": "Milch." },
        { "img": 'test_images/5.jpg', "content": "Milch." }
    ]

    for i, test_image in enumerate(test_images):

        # Run operations on img and draw on output_img
        img = cv2.imread(test_image["img"])
        output_img = cv2.imread(test_image["img"])

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
        print("Image:  " + test_image["img"])
        print("Width:  %i" % width)
        print("Height: %i" % height)

        # Measure time of calculations for optimization purposes (since it will be re-written in C++ for mobile devices later)
        start_time = time.time()

        # Calculate some alternative representations of the input image
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 5)
        _, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
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

                # Print some info on the output image
                for element in features["possible_fgc_elements"]:
                    cv2.drawContours(output_img,[element["contour"]],0,(255,255,0),2)

                    delta_x = element["x"] - features["center_coordinates"][0]
                    delta_y = element["y"] - features["center_coordinates"][1]
                    theta_radians = math.atan2(delta_y, delta_x)
                    deg = (math.degrees(theta_radians) + 90) % 360

                    cv2.putText(
                        output_img, 
                        str(int(element["angle"])), 
                        (element["x"], element["y"]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (255,255,255), 2, cv2.LINE_AA
                    )

                # Draw outline of center and orientation ring
                cv2.drawContours(output_img, [features["center_circle"]], 0, (0, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_ring"]], 0, (255, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_dot"]["contour"]], 0, (0, 255, 0), 2)

                # TODO unfinished

            else:
                print("Could not find outline of circle.")
        else:
            print("Could not find fgc at all.")

        print("Time:   %.3f s" % (time.time() - start_time))
        show_image(i, output_img)

        # Only process first image for now
        # break
    
    input("Press Enter to quit.\n")
        
        
if __name__ == "__main__":
    main()
