from fgc_tools import FGCReader
import matplotlib.pyplot as plt
from fgc_tools.cvfunctions import *


def main():
    print("FGC Reader started")

    test_images = [
        { "img": 'static/test_images/1.jpg', "content": "Level1" },
        { "img": 'static/test_images/2.jpg', "content": "Level2 which is harder" },
        { "img": 'static/test_images/3.jpg', "content": "Level3 which is super hard" },
        { "img": 'static/test_images/4.jpg', "content": "Meister der Galaxie." },
        { "img": 'static/test_images/5.jpg', "content": "Such pretty colors!" },
        { "img": 'static/test_images/6.jpg', "content": "Eine URL: https://google.com" },
        { "img": 'static/test_images/7.jpg', "content": "🥐" },
    ]
    passed_cnt = 0
    failed_cnt = 0
    total_time = 0

    for test_image in test_images:
        print("="*60)
        print("Test image: %s" % test_image["img"])
        print("-"*60)
        str_data, version, read_time, raw_binary_string, output_image, binary_img = FGCReader.read_image(test_image["img"])
        show_image("Output of: " + test_image["img"], output_image)
        # show_image("Binary of: " +  test_image["img"], binary_img)

        print("-"*60)
        print("RAW Read:   %s" % raw_binary_string)
        print("Version:    %s" % str(version))
        print("Read Time:  %.3fs" % read_time)
        print("Test data:  %s" % str(list(test_image["content"])))
        print("Read data:  %s" % str(list(str_data)))
        print("Result:     ", end="")
        if str_data == test_image["content"]:
            print("PASSED.")
            passed_cnt += 1
        else:
            print("FAILED.")
            failed_cnt += 1
        
        total_time += read_time 
    
    print("="*60)
    print("TOTAL PASSED:  %i" % passed_cnt)
    print("TOTAL FAILED:  %i" % failed_cnt)
    print("AVERAGE TIME:  %.3fs" % (total_time / len(test_images)))

    plt.show()

if __name__ == '__main__':
    main()