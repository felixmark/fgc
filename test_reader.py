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
        data_string = FGCReader.read_image(test_image["img"])

        print("Test image:", test_image["img"])
        print("Result: ", end="")
        if data_string == test_image["content"]:
            print("PASSED.")
        else:
            print("FAILED.")
        
        # Only process first image for now
        break

    plt.show()

    input("Press Enter to quit.\n")

if __name__ == '__main__':
    main()