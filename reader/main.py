import numpy as np
import cv2

img = cv2.imread('photo1.jpg')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.medianBlur(gray, 5) #cv2.bilateralFilter(gray,10,50,50)

minDist = 30
param1 = 80 #500
param2 = 45 #200 #smaller value-> more false circles
minRadius = 5
maxRadius = 100 #10

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

    orientation_dot_x = np.float(orientation_dot[0])
    orientation_dot_y = np.float(orientation_dot[1])

    extended_orientation_point_x = (center_circle_x + (orientation_dot_x - center_circle_x) * 10)
    extended_orientation_point_y = (center_circle_y + (orientation_dot_y - center_circle_y) * 10)

    circle_distance = closest_position / 3

    # Center Circle
    cv2.circle(img, (center_circle[0], center_circle[1]), center_circle[2], (0, 255, 0), 4)
    # Orientation dot
    cv2.circle(img, (orientation_dot[0], orientation_dot[1]), orientation_dot[2], (0, 255, 0), 4)
    # Layers
    for i in range(1,6):
        cv2.circle(img, (center_circle[0], center_circle[1]), int(closest_position + i*(circle_distance + circle_distance/2)), (0, 0, 255), 4)
    # Line for orientation
    cv2.line(img, (center_circle[0], center_circle[1]), (int(extended_orientation_point_x), int(extended_orientation_point_y)), (0, 0, 255), 4)



# Show result for testing:
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()