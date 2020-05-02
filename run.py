import getopt
import os
import sys

import cv2 as cv
import numpy as np

import RatUtils
from progress.bar import Bar
from PIL import ImageGrab, ImageFont

from DataVisualizer import DataVisualizer

#   SETTINGS

# This is how black black must be
BLACK_THRESHOLD = 5

# PIXELS TO CHECK
# Checks the pixels relative to the top center of the video [row, col]
# More pixels = less false detections
# PIXELS_TO_CHECK = [[30, -50], [30, 50]]
PIXELS_TO_CHECK = [[530, -350], [525, -300], [530, -250], [535, -200], [530, -150], [525, -100], [530, -50], [535, 0],
                   [530, 50], ]

# Show the video
SHOW_VIDEO = True

# Exit key
EXIT_KEY = "q"

# Show data
SHOW_DATA_ON_SCREEN = True

# font
FONT = cv.FONT_HERSHEY_SIMPLEX

# how frequently should the progress bar get updated
PROGRESS_BAR_FRAME_SKIPS = 300

# shows the black pixel detectors
SHOW_BLACK_PIXEL_DETECTORS = False

# Show video
VISUAL = False

# Beginning and end
BEGIN_FRAME = 0
END_FRAME = -1

# Live mode [DOES NOT WORK]
LIVE_MODE = False

# Splits
SPLITS = False
SPLIT_POINTS = [["tutorial", 0],
                ["river", 0],
                ["streets", 0],
                ["soup", 0],
                ["big skip", 0],
                ["plates", 0],
                ["shrimps", 0],
                ["book", 0],
                ["cooking", 0],
                ["RUN!!!", 0]]

# Output
OUTPUT = False
outputLocation = ""

#   END OF SETTINGS

video = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "Sldvi:s:b:e:p:t:o:",
                               ["input=", "skips=", "begin_frame=", "end_frame=", "pixels=", "threshold=", "output="])
except getopt.GetoptError:
    print("run.py -i <inputvideo> -s <progress_bar_frame_skips> -b <begin_frame> -e <end_frame>")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-S", "--splits"):
        SPLITS = True
    if opt in ("-i", "--inputvideo"):
        video = arg
    if opt in ("-t", "--threshold"):
        BLACK_THRESHOLD = int(arg)
    elif opt in ("-v", "--visual"):
        VISUAL = True
    elif opt in ("-d", "--detector"):
        SHOW_BLACK_PIXEL_DETECTORS = True
    elif opt in ("-s", "--skips"):
        PROGRESS_BAR_FRAME_SKIPS = int(arg)
    elif opt in ("-b", "--begin_frame"):
        BEGIN_FRAME = int(arg)
    elif opt in ("-e", "--end_frame"):
        END_FRAME = int(arg)
    elif opt in ("-l", "--live"):
        print("live mode does not work")
        exit()
        # LIVE_MODE = True
    elif opt in ("-p", "--pixels"):
        print("im sorry but you can't use that feature yet")
        exit()
        # PIXELS_TO_CHECK = arg
    elif opt in ("-o", "--output"):
        OUTPUT = True
        outputLocation = arg

if not os.path.isfile(video):
    print("Oops, I could not find this video {}".format(video))
    sys.exit()

cap = cv.VideoCapture()
cap.open(video)
cap.set(cv.CAP_PROP_POS_FRAMES, BEGIN_FRAME)

width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

frameCounter = 0
loadingFrameCounter = 0
frameRate = cap.get(cv.CAP_PROP_FPS)
if END_FRAME == -1:
    END_FRAME = cap.get(cv.CAP_PROP_FRAME_COUNT)
totalFrames = END_FRAME - BEGIN_FRAME

dataVisualizer = DataVisualizer(FONT)

out = 0
if OUTPUT:
    out = cv.VideoWriter(outputLocation, cv.VideoWriter_fourcc(*'XVID'), frameRate, (width, height))


def display():
    if SHOW_BLACK_PIXEL_DETECTORS:
        RatUtils.showDetectors(frame, PIXELS_TO_CHECK, width)
    dataVisualizer.add("Ratatool", DataVisualizer.HEADER)
    dataVisualizer.add("frame: {}/{}".format(frameCounter, totalFrames), DataVisualizer.TEXT)
    dataVisualizer.add("{} loading frames".format(loadingFrameCounter), DataVisualizer.TEXT)
    dataVisualizer.add("{}%".format(round(loadingFrameCounter / frameCounter * 100, 2)), DataVisualizer.TEXT)
    dataVisualizer.add("framerate: {}".format(frameRate), DataVisualizer.TEXT)
    minutes, seconds = RatUtils.timeCalc(frameCounter // frameRate)
    dataVisualizer.add("realtime: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
    minutes, seconds = RatUtils.timeCalc((frameCounter - loadingFrameCounter) // frameRate)
    dataVisualizer.add("without loads: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
    dataVisualizer.display(frame)


if SPLITS:
    # I know the numbers look a little derpy, there are multiple ways to fix this
    # If you want to you may fix it
    splitVisualizer = DataVisualizer(FONT, y=400)
    speed = 10
    activeSplit = 0
    while True:
        k = cv.waitKey(0)
        if k & 0xFF == ord(EXIT_KEY):
            break
        elif k & 0xFF == ord("j"):
            speed += 1
        elif k & 0xFF == ord("k"):
            speed -= 1
        elif k & 0xFF == ord("h"):
            frameCounter -= speed
        elif k & 0xFF == ord("l"):
            frameCounter += speed
        elif k & 0xFF == ord(" "):
            activeSplit += 1
        if activeSplit > len(SPLIT_POINTS) - 1:
            break
        SPLIT_POINTS[activeSplit][1] = frameCounter
        splitVisualizer.add("Splits", DataVisualizer.HEADER)
        splitVisualizer.add("Speed: " + str(speed), DataVisualizer.TEXT)
        for split in SPLIT_POINTS:
            splitVisualizer.add("{0: <20}".format(split[0]) + str(split[1]), DataVisualizer.TEXT)
        cap.set(cv.CAP_PROP_POS_FRAMES, frameCounter + BEGIN_FRAME)
        ret, frame = cap.read()
        splitVisualizer.display(frame)
        cv.imshow("splitfinder", frame)

    cap.set(cv.CAP_PROP_POS_FRAMES, BEGIN_FRAME)
    cv.destroyWindow('splitfinder')
    frameCounter = 0

progressBar = Bar('Processing', max=totalFrames // PROGRESS_BAR_FRAME_SKIPS, suffix='%(index)d/%(max)d - %('
                                                                                    'percent).1f%% - %(eta)ds')

activeSplit = 0

while True:
    frameCounter += 1
    if LIVE_MODE:
        printscreen_pil = ImageGrab.grab()
        frame = cv.resize(np.array(printscreen_pil, dtype="uint8"), (0, 0), fx=0.2, fy=0.2)
    else:
        ret, frame = cap.read()

    if RatUtils.isLoadingFrame(frame, PIXELS_TO_CHECK, BLACK_THRESHOLD, width):
        loadingFrameCounter += 1

    if SPLITS:
        sv = DataVisualizer(FONT, y=400)
        sv.add("Splits", DataVisualizer.HEADER)
        for split in SPLIT_POINTS:
            if split[1] < frameCounter:
                sv.add("{0: <20}".format(split[0]) + str(split[1]), DataVisualizer.TEXT)
            elif split is SPLIT_POINTS[activeSplit]:
                sv.add("{0: <20}".format(split[0]) + str(frameCounter), DataVisualizer.TEXT)
            else:
                sv.add("{0: <20}".format(split[0]) + str(0), DataVisualizer.TEXT)
        if SPLIT_POINTS[activeSplit][1] == frameCounter:
            activeSplit += 1
        if activeSplit > len(SPLIT_POINTS) - 1:
            break
        sv.display(frame)

    if VISUAL:
        display()
        cv.imshow("ratatool", frame)
        if OUTPUT:
            out.write(frame)
    if frameCounter % PROGRESS_BAR_FRAME_SKIPS == 0:
        progressBar.next()

    if cv.waitKey(1) & 0xFF == ord(EXIT_KEY):
        break
    if frameCounter == END_FRAME - BEGIN_FRAME:
        break

cap.release()
out.release()
if VISUAL and frameCounter == END_FRAME - BEGIN_FRAME:
    cv.waitKey(0)
    cv.destroyWindow('ratatool')
else:
    display()
    while True:
        if cv.waitKey(1) & 0xFF == ord(EXIT_KEY):
            break
    cv.destroyWindow('ratatool')
    progressBar.finish()
