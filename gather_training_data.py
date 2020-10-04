from utils import capture_screen, get_keys
import numpy as np
import cv2
import os
import time

file_name = 'training_data_1.npy'
folder_raw_img = "D:/python-projs/python-auto-nfs/raw-images/"


def keys_to_output(keys):
    """
        one hot encoded
        [A,W,D] boolean values.
    """
    output = [0, 0, 0]

    if 'A' in keys:
        output[0] = 1
    elif 'D' in keys:
        output[2] = 1
    else:
        output[1] = 1
    return output


def main():
    if os.path.isfile(file_name):
        print('File exists, loading previous data!')
        training_data = list(np.load(file_name, allow_pickle=True))
    else:
        print('File does not exist, starting fresh!')
        training_data = []

    for i in list(range(4))[::-1]:
        print(i + 1)
        time.sleep(1)

    paused = False
    count = 0
    while True:

        if not paused:
            # an 800x600 window
            screen = capture_screen.grab_screen(region=(0, 40, 800, 600))
            captured_screen = screen.copy()
            captured_screen = cv2.cvtColor(captured_screen, cv2.COLOR_BGR2RGB)
            last_time = time.time()
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (160, 120))
            # resize to something a bit more acceptable for a CNN
            keys = get_keys.key_check()
            output = keys_to_output(keys)
            training_data.append([screen, output])

            if len(training_data) % 1000 == 0:
                print(len(training_data))
                np.save(file_name, training_data)

        keys = get_keys.key_check()
        if 'P' in keys:
            if paused:
                paused = False
                print('unpaused!')
                time.sleep(1)
            else:
                print('Pausing!')
                paused = True
                time.sleep(1)
        elif 'M' in keys:
            # save the image
            cv2.imwrite(f"{folder_raw_img}{count}.jpg", captured_screen)
            count += 1


if __name__ == '__main__':
    main()
