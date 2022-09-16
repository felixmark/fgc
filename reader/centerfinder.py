import cv2
import math
import numpy as np


def find_circle_positions_with_hough_transform(img, features) -> bool:
    # Hough transform
    minDist = 100
    param1 = 80
    param2 = 60
    minRadius = 5
    maxRadius = 100
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    features["hough_circles"] = circles

    circle_positions = []
    if circles is not None:
        for circle in circles:
            circle = circle[0]
            x = int(circle[0])
            y = int(circle[1])
            circle_positions.append((x,y))

        features["hough_circle_positions"] = circle_positions
        return True

    return False


def calculate_distance(point1, point2) -> bool:
    """Calculate distance of points."""
    distance = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return distance


def find_center_with_outlines(img, features) -> bool:
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
        (_x, _y), (width, height), angle = bounding_rect
        bounding_rect_size = width * height

        # putting shape name at center of each shape
        if contour_sides > 6 and contour_sides < 22 and bounding_rect_size > 300:
            box = cv2.boxPoints(bounding_rect)
            box = np.int0(box)
            possible_fgc_elements.append(
                {"contour": contour, "x": x, "y": y, "bounding_rect": bounding_rect}
            )

    features["possible_fgc_elements"] = possible_fgc_elements

    

    circle_pairs_with_offset_and_closeness_to_hough_circle = []
    for a, contour_dict_1 in enumerate(possible_fgc_elements):
        for b, contour_dict_2 in enumerate(possible_fgc_elements):
            if a == b:
                continue
            offset_x = abs(contour_dict_1["x"] - contour_dict_2["x"]) 
            offset_y = abs(contour_dict_1["y"] - contour_dict_2["y"])
            pair_offset = offset_x + offset_y

            average_circle_center = ((contour_dict_1["x"] + contour_dict_2["x"])/2, (contour_dict_1["y"] + contour_dict_2["y"])/2)

            for circle_position in features["hough_circle_positions"]:
                closeness_to_hough_circle = calculate_distance(circle_position, average_circle_center)
                circle_pairs_with_offset_and_closeness_to_hough_circle.append({
                    "x": int(average_circle_center[0]),
                    "y": int(average_circle_center[1]),
                    "pair_offset": pair_offset,
                    "closeness_to_hough_circle": closeness_to_hough_circle,
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

    if center_of_fgc is not None:
        x_a, y_a, w_a, h_a = cv2.boundingRect(center_of_fgc["shape_a"])
        x_b, y_b, w_b, h_b = cv2.boundingRect(center_of_fgc["shape_b"])
        if w_a * h_a < w_b * h_b:
            center_shape = center_of_fgc["shape_a"]
            orientation_shape = center_of_fgc["shape_b"]
        else:
            center_shape = center_of_fgc["shape_b"]
            orientation_shape = center_of_fgc["shape_a"]
        
        features["center_circle"] = center_shape
        features["orientation_ring"] = orientation_shape
        features["center_coordinates"] = (center_of_fgc["x"], center_of_fgc["y"])

        return True

    return False


def find_orientation_dot(features) -> None:
    for possible_fgc_element in features["possible_fgc_elements"]:
        possible_fgc_element["distance_to_center"] = calculate_distance((possible_fgc_element["x"], possible_fgc_element["y"]), features["center_coordinates"])
    
    sorted_possible_fgc_elements = sorted(features["possible_fgc_elements"], key=lambda elem: elem["distance_to_center"])

    features["possible_fgc_elements"] = sorted_possible_fgc_elements
    features["orientation_dot"] = sorted_possible_fgc_elements[2]

def sanitize_data(features) -> None:
    max_jump_distance = features["orientation_dot"]["distance_to_center"]
    print("Max jump distance:", max_jump_distance)
    last_distance = 0
    index = 0
    while index < len(features["possible_fgc_elements"]):
        element = features["possible_fgc_elements"][index]
        if element["distance_to_center"] - last_distance > max_jump_distance:
            # print("Removing:", int(element["distance_to_center"]))
            features["possible_fgc_elements"].pop(index)
        else:
            # print("Keeping:", int(element["distance_to_center"]))
            last_distance = element["distance_to_center"]
            index += 1