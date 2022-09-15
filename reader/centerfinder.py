import cv2
import numpy as np


def find_circle_positions_with_hough_transform(img, output_img) -> list:
    # Hough transform
    minDist = 100
    param1 = 80
    param2 = 60
    minRadius = 5
    maxRadius = 100
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    circle_positions = []

    if circles is not None:
        for circle in circles:
            circle = circle[0]
            x = int(circle[0])
            y = int(circle[1])
            radius = int(circle[2])
            cv2.circle(output_img, (x, y), radius, (255, 0, 0), 2)
            circle_positions.append((x,y))

    return circle_positions


def calculate_distance(point1, point2) -> bool:
    """Calculate distance of points."""
    distance = abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
    return distance


def find_center_with_outlines(img, output_img, circle_positions):
    # using a findContours() function
    contours, _ = cv2.findContours(
        img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    possible_fgc_elements = []

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

            possible_fgc_elements.append(
                {"contour": contour, "x": x, "y": y}
            )


    

    circle_pairs_with_offset_and_closeness_to_hough_circle = []
    for a, contour_dict_1 in enumerate(possible_fgc_elements):
        for b, contour_dict_2 in enumerate(possible_fgc_elements):
            if a == b:
                continue
            offset_x = abs(contour_dict_1["x"] - contour_dict_2["x"]) 
            offset_y = abs(contour_dict_1["y"] - contour_dict_2["y"])
            pair_offset = offset_x + offset_y

            average_circle_center = ((contour_dict_1["x"] + contour_dict_2["x"])/2, (contour_dict_1["y"] + contour_dict_2["y"])/2)

            for circle_position in circle_positions:
                closeness_to_hough_circle = calculate_distance(circle_position, average_circle_center)
                circle_pairs_with_offset_and_closeness_to_hough_circle.append({
                    "x": int(average_circle_center[0]),
                    "y": int(average_circle_center[1]),
                    "pair_offset": int(pair_offset),
                    "closeness_to_hough_circle": int(closeness_to_hough_circle),
                    "shape_a": contour_dict_1["contour"],
                    "shape_b": contour_dict_2["contour"],
                })
    
    center_of_fgc = None
    best_score = None
    for circle_pair in circle_pairs_with_offset_and_closeness_to_hough_circle:
        score = circle_pair["pair_offset"] + circle_pair["closeness_to_hough_circle"]
        if best_score is None or score < best_score:
            best_score = score
            center_of_fgc = circle_pair

    cv2.putText(
        output_img, "Center", (center_of_fgc["x"], center_of_fgc["y"]),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
    )
    cv2.drawContours(output_img, [center_of_fgc["shape_a"]], 0, (0, 0, 255), 2)
    cv2.drawContours(output_img, [center_of_fgc["shape_b"]], 0, (0, 0, 255), 2)
