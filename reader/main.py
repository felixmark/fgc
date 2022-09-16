import numpy as np
import cv2
# import imutils
from centerfinder import *
import matplotlib.pyplot as plt
import time


def show_image(index, image):
    resize_factor = 4
    h, w = image.shape[:2]  #  suits for image containing any amount of channels
    h = int(h / resize_factor)  #  one must compute beforehand
    w = int(w / resize_factor)  #  and convert to INT

    plt_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(index)
    plt.imshow(plt_image)
    plt.show(block=False)


def main():

    print("FGC Reader started")

    test_images = [
        { "img": 'test_images/1.jpg', "content": "Example" },
        { "img": 'test_images/2.jpg', "content": "Milch." },
        { "img": 'test_images/3.jpg', "content": "Milch." },
        { "img": 'test_images/4.jpg', "content": "Milch." },
        { "img": 'test_images/5.jpg', "content": "Milch." }
    ]

    for i, test_image in enumerate(test_images):

        # Run two seperate methods and draw on output image
        img = cv2.imread(test_image["img"])
        output_img = cv2.imread(test_image["img"])

        features = {
            "center_coordinates": None,
            "center_circle": None,
            "orientation_ring": None,
            "orientation_dot": None,
            "hough_circle_positions": None,
            "hough_circles": None
        }

        height = img.shape[0]
        width = img.shape[1]

        print("="*60)
        print("Image:  " + test_image["img"])
        print("Width:  %i" % width)
        print("Height: %i" % height)

        start_time = time.time()

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 5)
        # hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    # Not needed yet
        _, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)


        print("Result: ", end="")
        if find_circle_positions_with_hough_transform(blurred_gray_img, features):
            if find_center_with_outlines(binary_img, features):
                print("FOUND center of fgc!")

                find_orientation_dot(features)
                sanitize_data(features)

                for element in features["possible_fgc_elements"]:
                    cv2.drawContours(output_img,[element["contour"]],0,(255,255,0),2)

                    delta_x = element["x"] - features["center_coordinates"][0]
                    delta_y = element["y"] - features["center_coordinates"][1]
                    theta_radians = math.atan2(delta_y, delta_x)
                    deg = (math.degrees(theta_radians) + 90) % 360

                    cv2.putText(
                        output_img, 
                        str(int(deg)), 
                        (element["x"], element["y"]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (255,255,255), 2, cv2.LINE_AA
                    )

                # Draw outline of center and orientation ring
                cv2.drawContours(output_img, [features["center_circle"]], 0, (0, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_ring"]], 0, (255, 0, 255), 2)
                cv2.drawContours(output_img, [features["orientation_dot"]["contour"]], 0, (0, 255, 0), 2)

                # TODO

            else:
                print("Could not find outline of circle.")
        else:
            print("Could not find fgc at all.")

        print("Time:   %.3f s" % (time.time() - start_time))

        show_image(i, output_img)

        # Only process first image for now
        break
    
    input("Press Enter to quit.\n")
        
        
if __name__ == "__main__":
    main()
