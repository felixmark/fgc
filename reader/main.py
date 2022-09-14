import numpy as np
import cv2
import imutils

import numpy as np
import cv2

img = cv2.imread('test_images/photo1.jpg')

def show_image(image, title="Image"):
    cv2.imshow(title, image)
    cv2.waitKey(0)




gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.medianBlur(gray, 5) #cv2.bilateralFilter(gray,10,50,50)

minDist = 100
param1 = 80 #500
param2 = 60 #200 #smaller value-> more false circles
minRadius = 5
maxRadius = 100 #10

show_image(blurred, "Blurry")

# docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

if circles is not None:
    center_circle = None
    largest_radius = 0

    closest_position = None
    orientation_dot = None

    circles = np.uint16(np.around(circles))
    for circle in circles[0,:]:
        radius = circle[2]
        if radius > largest_radius:
            largest_radius = radius
            center_circle = circle
        cv2.circle(img, (circle[0], circle[1]), radius, (255, 0, 0), 2)

    center_circle_x = np.float(center_circle[0])
    center_circle_y = np.float(center_circle[1])

    for circle in circles[0,:]:
        position_x = np.float(circle[0])
        position_y = np.float(circle[1])
        closeness_x = abs(center_circle_x - position_x)
        closeness_y = abs(center_circle_y - position_y)
        closeness_total = closeness_x + closeness_y
        if closest_position is None or closeness_total < closest_position:
            if closeness_total == 0 or circle[2] >= center_circle[2]/2:
                continue
            closest_position = closeness_total
            orientation_dot = circle

    # orientation_dot_x = np.float(orientation_dot[0])
    # orientation_dot_y = np.float(orientation_dot[1])

    # extended_orientation_point_x = (center_circle_x + (orientation_dot_x - center_circle_x) * 10)
    # extended_orientation_point_y = (center_circle_y + (orientation_dot_y - center_circle_y) * 10)

    # circle_distance = closest_position / 3

    # # Center Circle
    # cv2.circle(img, (center_circle[0], center_circle[1]), center_circle[2], (0, 255, 0), 4)
    # # Orientation dot
    # cv2.circle(img, (orientation_dot[0], orientation_dot[1]), orientation_dot[2], (0, 255, 0), 4)
    # # Layers
    # for i in range(1,6):
    #     cv2.circle(img, (center_circle[0], center_circle[1]), int(closest_position + i*(circle_distance + circle_distance/2)), (0, 0, 255), 4)
    # # Line for orientation
    # cv2.line(img, (center_circle[0], center_circle[1]), (int(extended_orientation_point_x), int(extended_orientation_point_y)), (0, 0, 255), 4)



# Show result for testing:
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows() 





















hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)      # img in hsv space
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)



# setting threshold of gray image
_, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
  
# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
)

possible_fgc_ements = []
centroids_only = []

for contour in contours[1:]:
  
    # cv2.approxPloyDP() function to approximate the shape
    approx = cv2.approxPolyDP(
        contour, 0.01 * cv2.arcLength(contour, True), True)
  
    # finding center point of shape
    M = cv2.moments(contour)
    if M['m00'] != 0.0:
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
  
    contour_sides = len(approx)
    bounding_rect = cv2.minAreaRect(contour)
    (x, y), (width, height), angle = bounding_rect
    bounding_rect_size = width * height

    # putting shape name at center of each shape
    if contour_sides > 6 and contour_sides < 22 and bounding_rect_size > 300:
        box = cv2.boxPoints(bounding_rect)
        box = np.int0(box)
        # cv2.drawContours(img,[box],0,(0,0,255),2)

        possible_fgc_ements.append(
            {"contour": contour, "x": x, "y": y}
        )
        centroids_only.append((x, y))
        cv2.drawContours(img, [contour], 0, (0, 255, 0), 2)
        """
        cv2.putText(
            img, str(round(bounding_rect_size, 1)), (int(x), int(y)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        """

x = [p[0] for p in centroids_only]
y = [p[1] for p in centroids_only]
centroid = (sum(x) / len(centroids_only), sum(y) / len(centroids_only))
centroid = (int(centroid[0]), int(centroid[1]))
cv2.putText(
    img, "Center?", centroid,
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
)

min_offset = None
min_offset_pair = None
for a, contour_dict_1 in enumerate(possible_fgc_ements):
    for b, contour_dict_2 in enumerate(possible_fgc_ements):
        if a == b:
            continue
        offset_x = abs(contour_dict_1["x"] - contour_dict_2["x"]) 
        offset_y = abs(contour_dict_1["y"] - contour_dict_2["y"])
        total_offset = offset_x + offset_y
        if min_offset is None or total_offset < min_offset:
            min_offset = total_offset
            min_offset_pair = (contour_dict_1, contour_dict_2)

cv2.drawContours(img, [min_offset_pair[0]["contour"]], 0, (0, 0, 255), 2)
cv2.drawContours(img, [min_offset_pair[1]["contour"]], 0, (0, 0, 255), 2)
  
# displaying the image after drawing contours
show_image(img, "Result")
cv2.destroyAllWindows()

