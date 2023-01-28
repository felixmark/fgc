import cv2
import math
import numpy as np
from .libs.commonfunctions import CommonFunctions

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation = inter)
    return resized

def find_circle_positions_with_hough_transform(img, features) -> bool:
    # Hough transform parameters
    minDist = 10
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
        print(f"Found {len(circle_positions)} hough circle{'' if len(circle_positions) == 1 else 's'}.")
        return True
    return False


def calculate_distance(point1, point2) -> bool:
    """Calculate distance of points."""
    distance = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return distance

def get_color_for_contour(img, contour):
    # Gets called A LOT -> make it more efficient
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    mask = cv2.drawContours(mask, [contour], -1, 255, -1)
    col_mean = cv2.mean(img,mask)
    return (col_mean[0] + col_mean[1] + col_mean[2]) // 3

def find_center_with_contours(img_edged, img_original, output_img, features) -> bool:
    """Funky function to determine the center of the fgc.
    It tries to find a point in the image, where two overlapping contours are as close as possible to a hough transform found circle."""

    contours, _ = cv2.findContours(
        img_edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    # Store all possible elements of the fgc in this list
    possible_fgc_elements = []
    rejected_too_few_sides_cnt = 0
    rejected_too_many_sides_cnt = 0
    rejected_too_small_cnt = 0

    for contour in contours[1:]:
        cv2.drawContours(output_img, [contour], 0, (0,0,255), 1)
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        
        # finding center point of shape
        M = cv2.moments(contour)
        x, y = 0, 0
        if M['m00'] != 0.0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])
    
        # The number of contour sides
        contour_sides = len(approx)
        bounding_rect = cv2.minAreaRect(contour)
        (_x_br, _y_br), (width, height), _angle = bounding_rect
        bounding_rect_size = width * height

        # Only consider elements with a certain amount of contour sides and a minimum size.
        if contour_sides >= 5 and contour_sides <= 35 and bounding_rect_size >= 20 and x and y:
            box = cv2.boxPoints(bounding_rect)
            box = np.int0(box)
            
            color = get_color_for_contour(img_original, contour)

            possible_fgc_elements.append(
                {"contour": contour, "x": x, "y": y, "bounding_rect": bounding_rect, "bounding_rect_size": bounding_rect_size, "sides": contour_sides, "color": color}
            )
        else:
            if contour_sides < 5:
                rejected_too_few_sides_cnt += 1
            elif contour_sides > 25:
                rejected_too_many_sides_cnt += 1
            elif bounding_rect_size < 20:
                rejected_too_small_cnt += 1

    print(f"Rejected {rejected_too_few_sides_cnt + rejected_too_many_sides_cnt + rejected_too_small_cnt} of {len(contours[1:])} contours.")
    print(f"Too few sides:  {rejected_too_few_sides_cnt} contours.")
    print(f"Too many sides: {rejected_too_many_sides_cnt} contours.")
    print(f"Too small:      {rejected_too_small_cnt} contours.")

    # Store possible fgc elements in features
    features["possible_fgc_elements"] = possible_fgc_elements

    # Store contour pairs with their distance to each other and to the next hough transform circle in a list
    circle_pairs_with_offset_and_closeness_to_hough_circle = []
    for a, contour_dict_1 in enumerate(possible_fgc_elements):
        for b, contour_dict_2 in enumerate(possible_fgc_elements):
            # Get bounding rect sizes
            bounding_rect_size_a = contour_dict_1["bounding_rect_size"]
            bounding_rect_size_b = contour_dict_2["bounding_rect_size"]

            # Do not consider elements themself or combinations, where a > b
            if a == b or (bounding_rect_size_a + bounding_rect_size_a/4 >= bounding_rect_size_b) or (bounding_rect_size_a/4 >= bounding_rect_size_b):
                continue

            pair_offset = calculate_distance([contour_dict_1["x"], contour_dict_1["y"]],[contour_dict_2["x"], contour_dict_2["y"]])

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
                "bounding_rect_size_small": bounding_rect_size_a,
                "bounding_rect_size_big": bounding_rect_size_a,
                "total_sides": contour_dict_1["sides"] + contour_dict_2["sides"],
                "total_color": contour_dict_1["color"] + contour_dict_2["color"],
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
        # relation_big_small_score = abs(circle_pair["bounding_rect_size_small"] - (circle_pair["bounding_rect_size_big"] * 0.75))
        pair_offset_score = circle_pair["pair_offset"] * 10
        size_score = (1 / (circle_pair["bounding_rect_size_small"] + circle_pair["bounding_rect_size_big"])) * 200000
        closeness_to_hough_circle_score = circle_pair["closeness_to_hough_circle"] * 10
        side_score = circle_pair["total_sides"] / 10
        color_score = circle_pair["total_color"] * 10
        score = pair_offset_score + closeness_to_hough_circle_score + side_score + color_score + size_score
        if best_score is None or score < best_score:
            best_score = score
            center_of_fgc = circle_pair

    #  Print all scores of winning center
    pair_offset_score = center_of_fgc["pair_offset"]
    size_score = (1 / (center_of_fgc["bounding_rect_size_small"] + center_of_fgc["bounding_rect_size_big"])) * 200000
    closeness_to_hough_circle_score = center_of_fgc["closeness_to_hough_circle"] * 10
    side_score = center_of_fgc["total_sides"] / 10
    color_score = center_of_fgc["total_color"] * 20
    score = pair_offset_score + closeness_to_hough_circle_score + side_score + color_score + size_score
    print("Best pair scores:")
    print("pair_offset_score:", pair_offset_score)
    print("size_score:", size_score)
    print("closeness_to_hough_circle_score", closeness_to_hough_circle_score)
    print("side_score:", side_score)
    print("color_score:", color_score)
    print("total_score:", score)

    # If a center is found
    if center_of_fgc is not None:
        true_center = center_of_fgc["center_a"]
        center_shape = center_of_fgc["shape_a"]
        orientation_shape = center_of_fgc["shape_b"]
        
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

    possible_orientation_dot_index = 2
    while (possible_orientation_dot_area >= center_circle_area):
        possible_orientation_dot_index += 1
        print("Removing possible_orientation_dot_area.")
        if len(features["possible_fgc_elements"]) > 2:
            possible_orientation_dot = features["possible_fgc_elements"][possible_orientation_dot_index]
            _x,_y,w,h = cv2.boundingRect(possible_orientation_dot["contour"])
            possible_orientation_dot_area = w * h
        else:
            break
    features["orientation_dot"] = possible_orientation_dot


def sanitize_data(features) -> None:
    """Try to get rid of all contours outside of the fgc by setting a max jump distance between contour distances to the center."""

    print("Sanitizing data...")

    # Add furthest_distance_to_center entry to all contours
    for element in features["possible_fgc_elements"]:
        furthest_distance_to_center = 0
        for point in element["contour"]:

            point_distance = calculate_distance(features["center_coordinates"], point[0]) 
            if point_distance > furthest_distance_to_center:
                furthest_distance_to_center = point_distance
        element["furthest_distance_to_center"] = furthest_distance_to_center

    # Sort contours by furthest_distance_to_center
    features["possible_fgc_elements"] = sorted(features["possible_fgc_elements"], key=lambda elem: elem["furthest_distance_to_center"])

    # Remove all contours which are too far from the previous contour
    max_jump_distance = features["orientation_dot"]["distance_to_center"] * 0.5
    last_distance = features["possible_fgc_elements"][1]["furthest_distance_to_center"]
    index = 2
    while index < len(features["possible_fgc_elements"]):
        element = features["possible_fgc_elements"][index]
        if element["furthest_distance_to_center"] - last_distance > max_jump_distance:
            features["possible_fgc_elements"].pop(index)
        else:
            last_distance = element["furthest_distance_to_center"]
            element["index"] = index
            index += 1

def get_all_angles(features) -> None:
    """Get angles of all shapes regarding to the orientation dot."""

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

    # Divide elements into rings by furthest_distance_to_center
    for element in features["possible_fgc_elements"]:

        # Increase ring if there is a jump in distance to center
        if abs(current_distance - element["furthest_distance_to_center"]) >= features["orientation_dot"]["distance_to_center"] * 0.1:   # WAS 0.2
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
    features["data_rings"] = []
    features["data"] = []

    print(f"Getting data of { len(features['rings']) } rings...")

    for ring_id, ring in enumerate(features["rings"]):
        
        print(f"Ring #{ring_id} - Features:{len(features['rings'][ring_id])}")

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

            # Check all contours if they contain the calculated position
            found_contour = False
            closest_contour = None
            total_closest_point_distance = None
            for element in ring:
                is_point_in_contour = cv2.pointPolygonTest(element["contour"], (target_position[0], target_position[1]), False)
                if is_point_in_contour == 1:
                    # If target position lies within this contour, this is the one we are looking for
                    if pos > 0:
                        # Pos (bit in ring) has to be greater than 0 because first bit is always 0
                        if current_contour_angle is not None and current_contour_angle != element["angle"]:
                            currently_zero = not currently_zero
                        if currently_zero:
                            data_ring.append(0)
                            data.append(0)
                        else:
                            data_ring.append(1)
                            data.append(1)

                    found_contour = True
                    current_contour_angle = element["angle"]
                    break
            
            # Seperate from previous loop to prevent doing this time consuming calculation all the time
            if not found_contour:
                for element in ring:
                    # If target position lies outside contour, keep track of the distance to this contour
                    closest_point_distance_in_contour = None
                    for point in element["contour"]:
                        distance = calculate_distance(target_position, point[0])
                        if closest_point_distance_in_contour is None or distance < closest_point_distance_in_contour:
                            closest_point_distance_in_contour = distance

                    if total_closest_point_distance is None or closest_point_distance_in_contour < total_closest_point_distance:
                        total_closest_point_distance = closest_point_distance_in_contour
                        closest_contour = element

            if not found_contour:
                # If contour was not found yet, check the closest distance to a contour and decide if it should have been inside
                if closest_contour is None or total_closest_point_distance > features["orientation_dot"]["distance_to_center"] * 0.3:
                    # FGC might be finished
                    break
                else:
                    if pos > 0:
                        if current_contour_angle is not None and current_contour_angle != closest_contour["angle"]:
                            currently_zero = not currently_zero
                        if currently_zero:
                            data_ring.append(0)
                            data.append(0)
                        else:
                            data_ring.append(1)
                            data.append(1)

                    current_contour_angle = closest_contour["angle"]

            features["target_positions"].append(target_position)

        data_rings.append(data_ring)

    features["data_rings"] = data_rings
    features["data"] = data