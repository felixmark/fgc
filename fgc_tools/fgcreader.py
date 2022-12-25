import cv2
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from cvfunctions import *
from commonfunctions import CommonFunctions
from commonconstants import CommonConstants




def rotate_vector(v,deg):
    v = np.array(v)
    assert len(v)==2
    
    phi = np.deg2rad(deg)
    s = np.sin(phi)
    c = np.cos(phi)
    M = np.array([[c,-s],[s, c]])

    return M.dot(v)


def check_contour_for_color(img, contour, color, color_precision = 255/10):
    """Will check img in contour region for that average color
    Will return value of average color if color argument is None"""

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    mask = cv2.drawContours(mask, [contour], 0, 255, -1)
    
    col_mean = cv2.mean(img,mask)
    if type(color) not in [list, tuple]:
        col_mean = col_mean[0]
    else:
        col_mean = col_mean[:len(color)]
    
    if color is None:
        return col_mean
    else:
        diff = np.abs(color - col_mean)
        return diff <= color_precision


def check_contour_for_spherical(contour):
    ellipse = cv2.fitEllipse(contour) # ( (position), (FULL axes), rotation)
    axes = ellipse[1] # these are NOT semi-axes!!!
    a = max(axes) / 2
    b = min(axes) / 2
    ratio_axes = b/a # ratio between the axes: 1=circle
    
    e_sq = 1.0 - ratio_axes**2  # eccentricity squared
    arc_ellipse = 4*a*scipy.special.ellipe(e_sq)  # circumference formula
    arc_cont = cv2.arcLength(contour, True)
    arcs = [arc_ellipse, arc_cont]
    ratio_arc = min(arcs) / max(arcs)
    
    area_ellipse = min(axes) * max(axes) * np.pi / 4
    area_cont = cv2.contourArea(contour)
    areas = [area_ellipse, area_cont]
    ratio_area = min(areas) / max(areas)

    ratio_geom_mean = np.power(ratio_axes * ratio_area * ratio_arc, 1/3) # geometric mean between all ratios
    
    return ratio_geom_mean, ratio_axes, ratio_area, ratio_arc


def find_dot_orientation(img_bin, center, radius):
    assert len(img_bin.shape)==2
    
    img = img_bin.copy()
    img_negative = img.copy()
    # show_image(1, img)
    
    center = np.array(center)
    c1 = np.array(np.round(center), dtype=np.int)
    # c1 = np.flip(c1)
    
    r_mid = int( np.round(radius * 6/4) )
    
    f_radi = [1.125, 1.875]
    r_min = int( np.round(radius * f_radi[0]) )
    r_max = int( np.round(radius * f_radi[1]) )
    
    img_t = np.zeros(img.shape[:2], dtype=np.uint8) # template for first ring
    # cv.circle(	img, center, radius, color[, thickness
    img_t = cv2.circle(img_t, c1, r_max, [255], -1)
    img_t = cv2.circle(img_t, c1, r_min, 0, -1)
    
    img = cv2.bitwise_and(img_negative, img_t)
    show_image(1, img)
    
    img_1 = np.zeros(img.shape, dtype=np.uint8)
    img_1 = cv2.circle(img_1, c1, r_mid, 255, 5)
    
    img_2 = cv2.bitwise_xor(img, img_1, mask=img_1)
    img_2 = cv2.dilate(img_2, np.ones((3,3))*255)
    show_image(2, img_2)
    
    contours, _ = cv2.findContours(img_2, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours)==2
    
    pts = []
    for cont in contours:
        M = cv2.moments(cont)
        cx = M['m10']/M['m00']
        cy = M['m01']/M['m00']
        cxy = (np.array([cx,cy]) - c1)*2 + c1
        cxy = np.array(cxy, dtype=np.int)
        pts.append( cxy )

    pts.append(c1)
    con_3 = [np.array([val]) for val in pts]
    con_3 = np.array(con_3)
    
    img_t = np.zeros(img.shape[:2], dtype=np.uint8) # template for first ring
    img_t = cv2.drawContours(img_t, [con_3], 0, 255, -1)
    img_3 = cv2.bitwise_and(img, img_t, mask=img_t)
    show_image(3, img_3)
    
    contours, _ = cv2.findContours(img_3, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours)==1
    
    cont = contours[0]
    cxy = cv2.fitEllipse(cont)[0]
    # cxy = np.array(cxy, dtype=np.int)
    v_dot = cxy-center
    # r_dot = np.sqrt( np.sum( np.square(c_dot) ) )
    # angle = np.arctan2(c_dot[1],c_dot[0]) * 180/np.pi
    
    return v_dot


def find_dot_orientation_2(img_bin, center, vector_0):
    assert len(img_bin.shape)==2
    img_debug = img_bin.copy()
    r_max = int(img_bin.shape[0]/2)
    r_0 = 60
    r_0_real = np.sqrt( np.sum( np.square(vector_0) ) )
    v_center = np.array(center)
    
    vU = vector_0 / r_0_real # unit vector
    Rscale = r_0_real/r_0
    
    ret_list = [vector_0]
    step = 30
    
    timeout = 20
    r = r_0 + step
    n = 1
    while r < r_max and timeout > 0:
        
        pt1 = np.array(v_center + vU * (r-step/2) * Rscale, dtype=int)
        pt2 = np.array(v_center + vU * (r+step/2) * Rscale, dtype=int)
        print(pt1 - pt2, pt1, pt2)
        
        # show_image(1, img_bin,"binary")
        img_temp = np.zeros(img_bin.shape, dtype=np.uint8)
        img_temp = cv2.line(img_temp, pt1, pt2, 255, 3)
        # show_image(2, img_temp, "temp line")
        img_temp = cv2.bitwise_and(img_bin, img_temp, mask=img_temp)
        # show_image(3, img_temp, "result of detection")
        # print("r:", r)
        
        
        contours, _ = cv2.findContours(img_temp, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)
        contours = list(contours)
        contours.sort(key= lambda x: cv2.contourArea(x), reverse=True) # biggest area
        cont = contours[0]
        
        M = cv2.moments(cont)
        assert M['m00'] > 0
        cx = M['m10']/M['m00']
        cy = M['m01']/M['m00']
        v_ci = np.array([cx,cy])
        
        ret_list.append(v_ci-v_center)
        
        n += 1
        r += step
        timeout -= 1
    
    return ret_list


def main() -> None:
    DEBUG_FLAG = False

    with open("_used_versions.txt","w") as f:
        f.write("cv2: {}\n".format(cv2.__version__) )
        f.write("numpy: {}\n".format(np.__version__) )
        f.write("matplotlib: {}\n".format(mpl.__version__) )
        f.write("seaborn: {}\n".format(sns.__version__) )
        f.write("scipy: {}\n".format(scipy.__version__) )

    test_images = [
        { "img": 'test_images/1.jpg', "content": "Level1" },
        { "img": 'test_images/2.jpg', "content": "Level2 which is harder" },
        { "img": 'test_images/3.jpg', "content": "Level3 which is super hard" },
        { "img": 'test_images/4.jpg', "content": "Level1" },
        { "img": 'test_images/5.jpg', "content": "Level2 which is harder" },
    ]

    path_test_image = test_images[0]["img"]

    dict_imgs={}

    img = cv2.imread(path_test_image)
    dict_imgs["high_contrast"] = img.copy()
    dict_imgs["high_contrast"] = set_brightness_contrast(dict_imgs["high_contrast"], 190, 178)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dict_imgs["20 gray"] = img.copy()

    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    dict_imgs["30 binary"] = img.copy()

    show_image(1, dict_imgs["30 binary"])

    img = dict_imgs["30 binary"]
    contours, _ = cv2.findContours(img, cv2.RETR_LIST , cv2.CHAIN_APPROX_SIMPLE)
    contours_binary = contours

    cont_2 = {}

    for i, contour in enumerate(contours):
        cont_2[i] = {"isDark":False, "sphereRating":0, "center":(0,0), "area":0}
        
        M = cv2.moments(contour)
        if M['m00'] > 0 :
            cx = int( M['m10']/M['m00'] )
            cy = int( M['m01']/M['m00'] )
            
            cont_2[i]["area"] = M['m00']
            cont_2[i]["center"] = ( int(cx), int(cy) )
        
        cont_2[i]["isDark"] = check_contour_for_color(img, contour, 0, 127)
        if not cont_2[i]["isDark"]: continue
        
        ratios = check_contour_for_spherical(contour)
        cont_2[i]["sphereRating"] = ratios[0]



    list_area = [entry["area"] for k,entry in cont_2.items() if (entry["isDark"]==True) and (entry["area"] > 0)]
    list_area.sort()

    n_bins = (max(list_area)-min(list_area))/100 # we want a bin width of abt 75
    n_bins = int(n_bins)
    if DEBUG_FLAG: plt.hist(list_area,n_bins)

    n,bins = np.histogram(list_area,n_bins)
    i_max = np.argmax(n)
    area_min = bins[i_max]
    area_max = bins[i_max+1]
    list_area = [a for a in list_area if a> area_min and a < area_max]

    area_median = np.mean(list_area)
    if DEBUG_FLAG: 
        plt.axvline(x=area_median,color="red", linestyle="dashed")
        plt.show()

    print("Average most common circle area: {:.2f}".format(area_median) )


    del DEBUG_FLAG

    img = dict_imgs["20 gray"]
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    list_dot_area = []
    for i,contour in enumerate(contours):
        col = [0,255,0]
        thick = 2
        txt = "{:>2} ".format(i)
        entry = cont_2[i]
        if not entry["isDark"]: 
            col = [255,127,0]
            thick = 1
        else:
            if entry["area"] >= 10:
                txt += "{:6.2f} {:6.0f}".format(entry["sphereRating"],entry["area"])
                if entry["sphereRating"] < 0.9: col = [0,0,255]

        img = cv2.drawContours(img, [contour], 0, col, thick)
        img = cv2.putText(img, txt, (10,5+12*(i+1)), cv2.FONT_HERSHEY_PLAIN, 1, col)
        img = cv2.putText(img, str(i), entry["center"], cv2.FONT_HERSHEY_PLAIN , 1, col)
        

    show_image("First", img)

    a = np.array([[1, 2]])
    b = np.array([[4, 1]])
    c = np.outer(a, b)

    v1 = np.ones(len(cont_2))
    for i, entry in cont_2.items():
        if entry["isDark"]==True and (entry["sphereRating"] > 0.9):
            v1[i] = entry["area"]
    v2 = np.array([1/v for v in v1])

    z1 = np.outer(v1,v2)
    z1 = z1/16
    z1 = np.log(z1)
    z1 = np.abs(z1)
    # print(np.min(z1))
    z1_flat = z1.flatten()

    z2 = [(i,v) for i,v in enumerate(z1_flat)]
    z2.sort(key = lambda val: val[1])
    z2 = [val for val in z2 if val[1] < 1]
    if len(z2)>10: z2 = z2[:10]

    points = {}
    for entry in z2:
        pos = entry[0]
        idx = np.unravel_index(pos, z1.shape)[0]
        if idx not in points: points[idx]=0
        
        points[idx] += 1
        pass

    point_ranking = []
    for key,val in points.items():
        point_ranking.append((key,val))
        pass

    point_ranking.sort(key = lambda val: val[1], reverse = True)
    center_idx = point_ranking[0][0]
    print("Center circle is at idx: {}".format(center_idx))

    img_negative = 255 - dict_imgs["30 binary"]
    img = img_negative.copy()

    cont_center = contours_binary[center_idx]
    ellipse = cv2.fitEllipse(cont_center)
    pos_center = np.array(ellipse[0])
    axes = np.array(ellipse[1])
    radius = np.mean(axes)/2


    kernel = np.ones((5,5), dtype=np.uint8) * 255
    iterations = int( radius/4 )

    img = cv2.dilate(img, kernel, iterations=iterations)
    show_image(1, img)

    img = cv2.erode(img, kernel, iterations=iterations-1)
    show_image("Some name", img)

    contours, _ = cv2.findContours(img, cv2.RETR_LIST , cv2.CHAIN_APPROX_SIMPLE)
    cont_new = None

    check_contours = []
    for cont in contours:
        if(check_contour_for_color(img, cont, 255, 10)):
            check_contours.append(cont)
            
            #np.array(pos_center, dtype=np.int)
            if cv2.pointPolygonTest(cont,pos_center, False) > 0:
                cont_new = cont
                break


    img_t = np.zeros(img.shape[:2], dtype=np.uint8)
    img_t = cv2.drawContours(img_t, [cont_new], 0, 255, -1)
    img_t = cv2.dilate(img_t, kernel, iterations=iterations)

    img = cv2.bitwise_and(img_negative, img_t)

    boundRect = cv2.boundingRect(cont_new)
    pt1 = np.array( (int(boundRect[0]), int(boundRect[1])) )
    pt2 = np.array( (int(boundRect[0]+boundRect[2]), int(boundRect[1]+boundRect[3])) )

    l_dist = np.array([pt1-pos_center, pt2-pos_center]).flatten()
    r = int( np.ceil( np.max( np.abs(l_dist) ) + radius/4 ) )
    vr = np.array([r,r])
    pt1 = np.array(pos_center - vr, dtype=np.int)
    pt2 = np.array(pos_center + vr, dtype=np.int)

    #get Region of Interest
    img = img_negative[ pt1[1]:pt2[1],pt1[0]:pt2[0] ].copy()

    # Scale to standard size
    scale_f = 40/radius
    if scale_f > 1.01:
        img = cv2.resize(img, None, fx=scale_f, fy=scale_f, interpolation=cv2.INTER_CUBIC )
    if scale_f < 0.99:
        img = cv2.resize(img, None, fx=scale_f, fy=scale_f, interpolation=cv2.INTER_AREA )

    # threshold scaled image
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # store work image
    dict_imgs["40 work"] = img.copy()
    cv2.imwrite("out_temp 3.png", img)

    show_image(3, img)


    #%%
    #plt.close("all")

    # img = dict_imgs["20 gray"]
    img = dict_imgs["40 work"]
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    img = cv2.cvtColor( img, cv2.COLOR_GRAY2BGR )
    img_ov = np.zeros(img.shape, dtype=np.uint8)

    list_contours = []
    a = input()
    for i,cont in enumerate(contours):
        ratios = check_contour_for_spherical(cont)
        ratio = ratios[0]
        isShpere = ratio > 0.95
        area = cv2.contourArea(cont)
        
        list_contours.append( {"idx":i,
                            "cont": cont,
                            "ratio": ratio,
                            "isShpere":isShpere,
                            "area": area } )
        pass

    list_sphere = []
    for entry in list_contours:
        if entry["isShpere"]:
            list_sphere.append(entry)
            pass
        pass

    list_sphere.sort(key = lambda val: val["area"], reverse = True)
    dot_center = list_sphere.pop(0)


    img_ov = cv2.drawContours(img_ov, [dot_center["cont"]], 0, [255,127,0], 5)

    list_areas = []
    for entry in list_sphere:
        img_ov = cv2.drawContours(img_ov, [entry["cont"]], 0, [0,255,0], 5)
        list_areas.append(entry["area"])
        pass

    sphere_area = np.mean(list_areas)


    img_out = cv2.addWeighted(img, 0.5, img_ov, 0.5, 0)
    show_image(1, img_out)



    #%%
    #plt.close("all")

    # img = dict_imgs["20 gray"]
    img = cv2.cvtColor( dict_imgs["40 work"], cv2.COLOR_GRAY2BGR )
    img_ov = np.zeros(img.shape, dtype=np.uint8)

    cont_center = dot_center["cont"]
    ellipse = cv2.fitEllipse(cont_center)
    pos_center = np.array(ellipse[0])
    axes = np.array(ellipse[1])/2
    angle = ellipse[2]

    radius = np.mean(axes)
    c1 = np.array( np.round(pos_center), dtype=np.int )
    ax = np.array( np.round(axes), dtype=np.int )


    vector_dot = find_dot_orientation(dict_imgs["40 work"], pos_center, radius)

    ret = find_dot_orientation_2(dict_imgs["40 work"],pos_center,vector_dot)

    v_dots = np.array(ret)
    radii = np.sqrt( np.sum( np.square(v_dots), 1 ) )
    angles = np.arctan2(v_dots[:,1], v_dots[:,0])
    # np.rad2deg(angles)
    phi_0 = np.mean([angles[0], angles[-1]])
    # np.rad2deg(phi_0)


    # raise Exception()

    for i,vR in enumerate(radii):
        r = int(np.round(vR) )
        img_ov = cv2.circle(img_ov, c1, int(r), [0,0,255], 1)
        if i>0:
            dpb = CommonFunctions.get_degrees_per_bit(i)
            for pos in range(int(360/dpb)):
                vi = rotate_vector(v_dots[i], dpb*pos)
                ci = np.array( np.round(pos_center + vi), dtype=np.int )
                img_ov = cv2.circle(img_ov, ci, 10, [255,0,0], -1)

    img_out = cv2.addWeighted(img, 0.5, img_ov, 0.5, 0)
    show_image(1, img_out)
    cv2.imwrite("out_temp 4.png", img_out)

    img_bin = dict_imgs["40 work"].copy()
    img = cv2.cvtColor( dict_imgs["40 work"], cv2.COLOR_GRAY2BGR )

    dict_rings = {}

    idx=0

    bit_string = ""

    for i,vDot in enumerate(v_dots):
        if i==0: continue
        
        
        dpb = CommonFunctions.get_degrees_per_bit(i)
        numBits = int(360/dpb)-1
        dict_rings[i] = []
        
        bitVal = False
        
        for pos in range(numBits):
            v_valid = rotate_vector(vDot, dpb * (pos + 1) )
            v_valid_c = np.array( np.round(pos_center + v_valid), dtype=np.int )
            bit_valid = img_bin[v_valid_c[1], v_valid_c[0] ] > 127 # check if the next dot exists for the bit inbetween to count
            if not bit_valid: break
            
            v_info = rotate_vector(vDot, dpb * (pos + 1/2) )
            v_info_c = np.array( np.round(pos_center + v_info), dtype=np.int )
            bit_info = img_bin[v_info_c[1], v_info_c[0] ] > 127 # check if bit is set
            dict_rings[i].append(1 if bit_info else 0)
            bitVal = bitVal if bit_info else not bitVal
            bit_string += str(1 if bitVal else 0)
            
            col = [63,200,0] if bit_info else [0,0,255]
            marker = cv2.MARKER_DIAMOND if bit_info else cv2.MARKER_TILTED_CROSS
            img = cv2.drawMarker(img, v_info_c, col, marker,5,3)
            
        

    for ring in dict_rings:
        print("ring",ring,dict_rings[ring])
    print(bit_string)

    show_image(2, img)
    cv2.imwrite("out_temp 5.png", img)


if __name__ == '__main__':
    main()
