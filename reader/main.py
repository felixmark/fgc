import numpy as np
import cv2
import imutils
from centerfinder import *


def show_image(image, title="Image"):
    resize_factor = 4
    h, w = image.shape[:2]  #  suits for image containing any amount of channels
    h = int(h / resize_factor)  #  one must compute beforehand
    w = int(w / resize_factor)  #  and convert to INT
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, w, h)
    cv2.imshow(title, image)
    cv2.waitKey(0)


def main():

    test_images = [
        { "img": 'test_images/1.jpg', "content": "Example" },
        { "img": 'test_images/2.jpg', "content": "Milch." },
        { "img": 'test_images/3.jpg', "content": "Milch." },
        { "img": 'test_images/4.jpg', "content": "Milch." },
        { "img": 'test_images/5.jpg', "content": "Milch." }
    ]


    for test_image in test_images:

        # Run two seperate methods and draw on output image
        img = cv2.imread(test_image["img"])
        output_img = cv2.imread(test_image["img"])

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_gray_img = cv2.medianBlur(gray_img, 5)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)



        circle_positions = find_circle_positions_with_hough_transform(blurred_gray_img, output_img)
        find_center_with_outlines(binary_img, output_img, circle_positions)
        show_image(output_img, "Result 1 (Blue) and 2 (Red)")
        cv2.destroyAllWindows() 
        
        
if __name__ == "__main__":
    main()
