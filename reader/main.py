import numpy as np
import cv2
import imutils

img = cv2.imread('test_images/photo1.jpg')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)      # img in hsv space
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)



# setting threshold of gray image
_, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
  
# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
)

cv2.imshow('threshold', threshold)
cv2.waitKey(0)

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
        cv2.putText(
            img, str(round(bounding_rect_size, 1)), (int(x), int(y)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )

x = [p[0] for p in centroids_only]
y = [p[1] for p in centroids_only]
centroid = (sum(x) / len(centroids_only), sum(y) / len(centroids_only))
centroid = (int(centroid[0]), int(centroid[1]))
cv2.putText(
    img, "Center?", centroid,
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2
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
cv2.imshow('shapes', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

