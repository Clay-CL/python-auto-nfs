import numpy as np
from PIL import ImageGrab
import cv2
from PyKeyboard import PressKey, ReleaseKey, W, A, S, D
import time
from Constants import VERTICES
from statistics import mean


def roi(image, vertices):
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(image, mask)
    return masked


def draw_lines(processed_img, lines, color):
    try:
        for line in lines:
            coordinates = line[0]
            cv2.line(processed_img,
                     (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                     color,
                     3)
    except:
        pass
    return processed_img


def myMouseListener(event, x, y, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX, mouseY = x, y
        print(mouseX, mouseY)
        # cv2.putText(new_screen, f"{mouseX},{mouseY}", (780, 580), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        # cv2.circle(img,(x,y),100,(255,0,0),-1)


def process_img(original_image):
    color_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=120, threshold2=300)

    processed_img = cv2.GaussianBlur(processed_img, (5, 5), 0)

    vertices = np.array(VERTICES)
    processed_img = roi(processed_img, [vertices])

    minLineLength = 100
    maxLineGap = 5
    lines = cv2.HoughLinesP(processed_img, 1, np.pi / 180, 180, np.array([]), minLineLength, maxLineGap)
    # processed_img = draw_lines(color_img, lines, [0, 255, 0])

    m1, m2 = 0, 0
    try:
        print("jihk")
        l1, l2, m1, m2 = draw_lanes(lines)
        cv2.line(color_img, (l1[0], l1[1]), (l1[2], l1[3]), [0, 255, 0], 3)
        cv2.line(color_img, (l2[0], l2[1]), (l2[2], l2[3]), [0, 255, 0], 3)
    except Exception as e:
        print(str(e))
        pass

    return color_img, m1, m2


def draw_lanes(lines):
    try:
        ys = []
        print(enumerate(lines))
        for i in lines:
            ys += [i[0][1], i[0][3]]
            # for y_cord in i:
            #     ys += [y_cord[1], y_cord[3]]

        min_y = min(ys)
        max_y = 600
        new_lines = []
        line_dict = {}

        for idx, i in enumerate(lines):
            for xyxy in i:
                x_coords = (xyxy[0], xyxy[2])
                y_coords = (xyxy[1], xyxy[3])
                A = np.vstack([x_coords, np.ones(len(x_coords))]).T
                m, b = np.linalg.lstsq(A, y_coords)[0]

                x1 = (min_y - b) / m
                x2 = (max_y - b) / m

                line_dict[idx] = [m, b, [int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])
        final_lanes = {}

        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]

            if len(final_lanes) == 0:
                final_lanes[m] = [[m, b, line]]

            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms * 1.2) > abs(m) > abs(other_ms * 0.8):
                            if abs(final_lanes_copy[other_ms][0][1] * 1.2) > abs(b) > abs(
                                    final_lanes_copy[other_ms][0][1] * 0.8):
                                final_lanes[other_ms].append([m, b, line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [[m, b, line]]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2], lane1_id, lane2_id

    except Exception as e:
        print(str(e))


def average_lane(lane_data):
    x1s = []
    y1s = []
    x2s = []
    y2s = []
    for data in lane_data:
        x1s.append(data[2][0])
        y1s.append(data[2][1])
        x2s.append(data[2][2])
        y2s.append(data[2][3])
    return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))


for i in list(range(4))[::-1]:
    print(i + 1)
    time.sleep(1)


# print('Gas')
# PressKey(W)
# time.sleep(3)
# print('Release Gas pedal')
# ReleaseKey(W)

def straight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(W)


def left():
    ReleaseKey(W)
    PressKey(A)
    ReleaseKey(D)
    ReleaseKey(A)


def right():
    ReleaseKey(W)
    PressKey(D)
    ReleaseKey(A)
    ReleaseKey(D)


def slowdown():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)


while True:
    global new_screen
    screen = np.array(ImageGrab.grab(bbox=(0, 40, 800, 600)))
    new_screen, m1, m2 = process_img(screen)

    cv2.imshow('window2', new_screen)
    # cv2.setMouseCallback('window2', myMouseListener)

    if m1 < 0 and m2 < 0:
        right()
    elif m1 > 0 and m2 > 0:
        left()
    else:
        straight()


    # cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
