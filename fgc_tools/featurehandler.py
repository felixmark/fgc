import cv2
import math
import numpy as np
from .commonfunctions import CommonFunctions


def find_circle_positions_with_hough_transform(img, features) -> bool:
    # Hough transform parameters
    minDist = 100
    param1 = 80
    param2 = 60
    minRadius = 5
    maxRadius = 100
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    
    # Store detected hough circles in features
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


def find_center_with_contours(img, features) -> bool:
    """Funky function to determine the center of the fgc.
    It tries to find a point in the image, where two overlapping contours are as close as possible to a hough transform found circle."""

    contours, _ = cv2.findContours(
        img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    # Store all possible elements of the fgc in this list
    possible_fgc_elements = []

    for contour in contours[1:]:
    
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        
        # finding center point of shape
        M = cv2.moments(contour)
        if M['m00'] != 0.0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])
    
        # The number of contour sides
        contour_sides = len(approx)
        bounding_rect = cv2.minAreaRect(contour)
        (_x_br, _y_br), (width, height), _angle = bounding_rect
        bounding_rect_size = width * height

        # Only consider elements with a certain amount of contour sides and a minimum size.
        if contour_sides > 6 and contour_sides < 22 and bounding_rect_size > 250:
            box = cv2.boxPoints(bounding_rect)
            box = np.int0(box)

            possible_fgc_elements.append(
                {"contour": contour, "x": x, "y": y, "bounding_rect": bounding_rect}
            )
    # Store possible fgc elements in features
    features["possible_fgc_elements"] = possible_fgc_elements

    # Store contour pairs with their distance to each other and to the next hough transform circle in a list
    circle_pairs_with_offset_and_closeness_to_hough_circle = []
    for a, contour_dict_1 in enumerate(possible_fgc_elements):
        for b, contour_dict_2 in enumerate(possible_fgc_elements):
            # Do not consider elements themself
            if a == b:
                continue

            offset_x = abs(contour_dict_1["x"] - contour_dict_2["x"]) 
            offset_y = abs(contour_dict_1["y"] - contour_dict_2["y"])
            pair_offset = offset_x + offset_y

            # Calculate the average center of both contours 
            average_circle_center = ((contour_dict_1["x"] + contour_dict_2["x"])/2, (contour_dict_1["y"] + contour_dict_2["y"])/2)

            # Find minimum distance to a hough circle
            min_closeness_to_hough_circle = None
            for circle_position in features["hough_circle_positions"]:
                closeness_to_hough_circle = calculate_distance(circle_position, average_circle_center)
                if min_closeness_to_hough_circle is None or closeness_to_hough_circle < min_closeness_to_hough_circle:
                    min_closeness_to_hough_circle = closeness_to_hough_circle

            # Store the found pair
            circle_pairs_with_offset_and_closeness_to_hough_circle.append({
                "x": int(average_circle_center[0]),
                "y": int(average_circle_center[1]),
                "pair_offset": pair_offset,
                "closeness_to_hough_circle": min_closeness_to_hough_circle,
                "shape_a": contour_dict_1["contour"],
                "shape_b": contour_dict_2["contour"],
                "center_a": (contour_dict_1["x"], contour_dict_1["y"]),
                "center_b": (contour_dict_2["x"], contour_dict_2["y"]),
            })

    # Now we can determine the best match for our fgc center
    center_of_fgc = None
    best_score = None
    for circle_pair in circle_pairs_with_offset_and_closeness_to_hough_circle:
        score = circle_pair["pair_offset"] + circle_pair["closeness_to_hough_circle"]
        if best_score is None or score < best_score:
            best_score = score
            center_of_fgc = circle_pair

    # If a center is found
    if center_of_fgc is not None:
        x_a, y_a, w_a, h_a = cv2.boundingRect(center_of_fgc["shape_a"])
        x_b, y_b, w_b, h_b = cv2.boundingRect(center_of_fgc["shape_b"])
        if w_a * h_a < w_b * h_b:
            true_center = center_of_fgc["center_a"]
            center_shape = center_of_fgc["shape_a"]
            orientation_shape = center_of_fgc["shape_b"]
        else:
            true_center = center_of_fgc["center_b"]
            center_shape = center_of_fgc["shape_b"]
            orientation_shape = center_of_fgc["shape_a"]
        
        # Store the center to the features
        features["center_circle"] = center_shape
        features["orientation_ring"] = orientation_shape
        features["center_coordinates"] = true_center
        return True
    return False


def find_orientation_dot(features) -> None:
    """Try to find the orientation dot by determing the contour with the minimum distance to the fgc center."""

    for possible_fgc_element in features["possible_fgc_elements"]:
        possible_fgc_element["distance_to_center"] = calculate_distance((possible_fgc_element["x"], possible_fgc_element["y"]), features["center_coordinates"])
    
    sorted_possible_fgc_elements = sorted(features["possible_fgc_elements"], key=lambda elem: elem["distance_to_center"])

    features["possible_fgc_elements"] = sorted_possible_fgc_elements

    possible_orientation_dot = features["possible_fgc_elements"][2]
    _x,_y,w,h = cv2.boundingRect(possible_orientation_dot["contour"])
    _x2,_y2,w2,h2 = cv2.boundingRect(features["center_circle"])
    possible_orientation_dot_area = w * h
    center_circle_area = w2 * h2
    while (possible_orientation_dot_area >= center_circle_area):
        features["possible_fgc_elements"].pop(2)
        possible_orientation_dot = features["possible_fgc_elements"][2]
        _x,_y,w,h = cv2.boundingRect(possible_orientation_dot["contour"])
        possible_orientation_dot_area = w * h
    features["orientation_dot"] = possible_orientation_dot


def sanitize_data(features) -> None:
    """Try to get rid of all contours outside of the fgc by setting a max jump distance between contour distances to the center."""

    max_jump_distance = features["orientation_dot"]["distance_to_center"] * 0.7
    last_distance = features["orientation_dot"]["distance_to_center"]
    index = 2
    while index < len(features["possible_fgc_elements"]):
        element = features["possible_fgc_elements"][index]
        if element["distance_to_center"] - last_distance > max_jump_distance:
            features["possible_fgc_elements"].pop(index)
        else:
            last_distance = element["distance_to_center"]
            element["index"] = index
            index += 1

def get_all_angles(features) -> None:
    vector_from_center_to_orientation_point = [
        features["orientation_dot"]["x"] - features["center_coordinates"][0],
        features["orientation_dot"]["y"] - features["center_coordinates"][1],
    ]
    for element in features["possible_fgc_elements"]:
        vector_from_center_to_element = [
            element["x"] - features["center_coordinates"][0],
            element["y"] - features["center_coordinates"][1],
        ]

        unit_vector_1 = vector_from_center_to_orientation_point / np.linalg.norm(vector_from_center_to_orientation_point)
        unit_vector_2 = vector_from_center_to_element / np.linalg.norm(vector_from_center_to_element)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        clipped_dot_product = np.clip(dot_product, -1.0, 1.0)
        rad = np.arccos(clipped_dot_product)
        if vector_from_center_to_orientation_point[0] * vector_from_center_to_element[1] - vector_from_center_to_orientation_point[1] * vector_from_center_to_element[0] < 0:
            rad = -rad
        deg = 0
        if not math.isnan(rad):
            deg = math.degrees(rad)
            deg = math.floor(deg+0.5)
            if deg < 0:
                deg = 180 + (180 - abs(deg))
            if deg >= 359:
                deg = 0

        element["angle"] = deg


def divide_elements_into_rings_by_angle_and_distance(features):
    current_ring = 0
    current_distance = 0
    rings = []
    angle_sorted_rings = []

    # Add furthest_distance_to_center entry to all contours
    for element in features["possible_fgc_elements"]:
        furthest_distance_to_center = 0
        for point in element["contour"]:

            point_distance = calculate_distance(features["center_coordinates"], point[0]) 
            if point_distance > furthest_distance_to_center:
                furthest_distance_to_center = point_distance
        element["furthest_distance_to_center"] = furthest_distance_to_center

        arc_length = cv2.arcLength(element["contour"], True)    # Calculates the perimeter of the contour
        element["arc_length"] = arc_length

    # Sort contours by furthest_distance_to_center
    features["possible_fgc_elements"] = sorted(features["possible_fgc_elements"], key=lambda elem: elem["furthest_distance_to_center"])

    # Divide elements into rings by furthest_distance_to_center
    for element in features["possible_fgc_elements"]:

        # Increase ring if there is a jump in distance to center
        if abs(current_distance - element["furthest_distance_to_center"]) >= features["orientation_dot"]["distance_to_center"] * 0.3:
            current_ring += 1
        
        # Append new ring to rings if necessary and append current contour element
        if current_ring >= len(rings):
            rings.append([])
        
        # Current ring append contour
        rings[current_ring - 1].append(element)

        # Set current distance to own maximum distance
        current_distance = element["furthest_distance_to_center"]

    # Get number of dots for each contour
    for ring in rings:
        if len(ring) < 1: continue
        sorted_ring = sorted(ring, key=lambda elem: elem["angle"])
        angle_sorted_rings.append(sorted_ring)

    features["rings"] = angle_sorted_rings


def rotate_vector(v,deg):
    v = np.array(v)
    assert len(v)==2
    
    phi = np.deg2rad(deg)
    s = np.sin(phi)
    c = np.cos(phi)
    M = np.array([[c,-s],[s, c]])

    return M.dot(v)


def get_data_from_rings(features):
    currently_zero = True
    data_rings = []
    data = []
    
    features["target_positions"] = []

    for ring_id, ring in enumerate(features["rings"]):

        # Skip first two "rings" because they are the center circle and the orientation ring+dot
        if ring_id < 2:
            continue

        ring_id = ring_id - 1

        data_ring = []
        currently_zero = True   # Every ring begins with a zero
        vector_from_center_to_orientation_point = [
            (features["orientation_dot"]["x"] - features["center_coordinates"][0]),
            (features["orientation_dot"]["y"] - features["center_coordinates"][1]),
        ]
        vector_from_center_to_dot = [
            vector_from_center_to_orientation_point[0] / 2 + ((vector_from_center_to_orientation_point[0] / 2) * (ring_id + 1)),
            vector_from_center_to_orientation_point[1] / 2 + ((vector_from_center_to_orientation_point[1] / 2) * (ring_id + 1)),
        ]

        degrees_per_bit = CommonFunctions.get_degrees_per_bit(ring_id)
        numBits = int( 360 / degrees_per_bit )
        
        current_contour_angle = None

        for pos in range(numBits):
            rotated_vector = vector_from_center_to_dot
            if pos > 0:
                rotated_vector = rotate_vector( vector_from_center_to_dot, degrees_per_bit * pos )
            # Get position and check in which contour it lands in
            target_position = [
                int(features["center_coordinates"][0] + rotated_vector[0]), 
                int(features["center_coordinates"][1] + rotated_vector[1])
            ]
            features["target_positions"].append(target_position)

            # Check all contours if they contain the calculated position
            for element in ring:
                is_point_in_contour = cv2.pointPolygonTest(element["contour"], (target_position[0], target_position[1]), False)
                if is_point_in_contour == 1:
                    if pos > 0:
                        if current_contour_angle is not None and current_contour_angle != element["angle"]:
                            currently_zero = not currently_zero
                        if currently_zero:
                            data_ring.append(0)
                            data.append(0)
                        else:
                            data_ring.append(1)
                            data.append(1)

                    current_contour_angle = element["angle"]
        
        data_rings.append(data_ring)

    features["data_rings"] = data_rings
    features["data"] = data