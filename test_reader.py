from fgc_tools import FGCReader
import matplotlib.pyplot as plt


def main():
    print("FGC Reader started")

    test_images = [
        { "img": 'static/test_images/1.jpg', "content": "Level1" },
        { "img": 'static/test_images/2.jpg', "content": "Level2 which is harder" },
        { "img": 'static/test_images/3.jpg', "content": "Level3 which is super hard" },
        { "img": 'static/test_images/4.jpg', "content": "Level1" },
        { "img": 'static/test_images/5.jpg', "content": "Level2 which is harder" },
    ]

    for test_image in test_images:
        str_data, version, read_time, raw_binary_string = FGCReader.read_image(test_image["img"])

        print("Test image: %s" % test_image["img"])
        print("RAW Read:   %s" % raw_binary_string)
        print("Version:    %s" % str(version))
        print("Read Time:  %s" % str(read_time))
        print("Test data:  %s" % str(list(test_image["content"])))
        print("Read data:  %s" % str(list(str_data)))
        print("Result:     ", end="")
        if str_data == test_image["content"]:
            print("PASSED.")
        else:
            print("FAILED.")
        
        # Only process first image for now
        

    plt.show()

if __name__ == '__main__':
    main()