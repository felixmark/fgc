import cv2
import matplotlib.pyplot as plt


def set_brightness_contrast(img, brightness=255, contrast=127):
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            max = 255
        else:
            shadow = 0
            max = 255 + brightness
 
        al_pha = (max - shadow) / 255
        ga_mma = shadow
        cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
    else:
        cal = img
 
    if contrast != 0:
        Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        Gamma = 127 * (1 - Alpha)
        cal = cv2.addWeighted(cal, Alpha, cal, 0, Gamma)

    return cal

def show_image(unique_name, image, title=None):
    plt_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(unique_name)
    if title != None and type(title) is str:
        plt.title(title)
    plt.imshow(plt_image)
    plt.show(block=False)

