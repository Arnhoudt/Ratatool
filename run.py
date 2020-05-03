import getopt
import os
import sys

import cv2 as cv
import numpy as np

import RatUtils
from progress.bar import Bar
from PIL import ImageGrab, Image

from DataVisualizer import DataVisualizer

#   SETTINGS

# This is how black black must be
BLACK_THRESHOLD = 5

# PIXELS TO CHECK
# Checks the pixels relative to the top center of the video [row, col]
# More pixels = less false detections
PIXELS_TO_CHECK = [[30, -50], [30, 50]]
#PIXELS_TO_CHECK = [[530, -350], [525, -300], [530, -250], [535, -200], [530, -150], [525, -100], [530, -50], [535, 0], [530, 50], ]

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

# Fullscreen (this reduces the speed dramatically)
FULLSCREEN = False

# Border
BORDER_LEFT = 400
BORDER_BOTTOM = 40

#   END OF SETTINGS

video = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "fSldvi:s:b:e:p:t:o:",
                               ["input=", "skips=", "begin_frame=", "end_frame=", "pixels=", "threshold=", "output="])
except getopt.GetoptError:
    print("run.py -i <inputvideo> -s <progress_bar_frame_skips> -b <begin_frame> -e <end_frame>")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-f", "--fullscreen"):
        FULLSCREEN = True
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

width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + BORDER_LEFT
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) + BORDER_BOTTOM

frameCounter = 0
loadingFrameCounter = 0
frameRate = cap.get(cv.CAP_PROP_FPS)
if END_FRAME == -1:
    END_FRAME = cap.get(cv.CAP_PROP_FRAME_COUNT)
totalFrames = END_FRAME - BEGIN_FRAME

dataVisualizer = DataVisualizer(FONT, width=width, height=BORDER_BOTTOM, x=0, y=height - BORDER_BOTTOM, colWidth=180)
out = 0
if OUTPUT:
    out = cv.VideoWriter(outputLocation, cv.VideoWriter_fourcc(*'XVID'), frameRate, (width, height))


def display():
    rm, rs = RatUtils.timeCalc(frameCounter // frameRate)
    wm, ws = RatUtils.timeCalc((frameCounter - loadingFrameCounter) // frameRate)
    dataVisualizer.add(["frame: {}/{}".format(frameCounter, totalFrames),
                        "{} loading frames".format(loadingFrameCounter),
                        "{}%".format(round(loadingFrameCounter / frameCounter * 100, 2)),
                        "framerate: {}".format(frameRate),
                        "realtime: {:02d}:{:02d}".format(rm, rs),
                        "without loads: {:02d}:{:02d}".format(wm, ws)], DataVisualizer.TEXT)
    dataVisualizer.display(frame)


if SPLITS:
    splitVisualizer = DataVisualizer(FONT, y=0)
    speed = frameRate
    activeSplit = 0
    while True:
        k = cv.waitKey(0)
        if k & 0xFF == ord(EXIT_KEY):
            break
        elif k & 0xFF == ord("j"):
            speed += 1
        elif k & 0xFF == ord("k"):
            if speed != 0:
                speed -= 1
        elif k & 0xFF == ord("h"):
            if frameCounter - speed > 0:
                frameCounter -= speed
            else:
                frameCounter = 0
        elif k & 0xFF == ord("l"):
            frameCounter += speed
        elif k & 0xFF == ord(" "):
            activeSplit += 1
        elif k & 0xFF == 8:
            SPLIT_POINTS[activeSplit][1] = 0
            activeSplit -= 1
        if activeSplit > len(SPLIT_POINTS) - 1:
            break
        SPLIT_POINTS[activeSplit][1] = frameCounter
        splitVisualizer.add(["Splits"], DataVisualizer.HEADER)
        splitVisualizer.add(["Speed: " + str(round(speed / frameRate, 2)) + " seconds"], DataVisualizer.TEXT)

        for split in SPLIT_POINTS:
            minutes, seconds = RatUtils.timeCalc(split[1] // frameRate)
            r, g, b = 255, 255, 255
            if split is SPLIT_POINTS[activeSplit]:
                r = 0
            splitVisualizer.add([split[0], "{:d}:{:02d}".format(minutes, seconds)], DataVisualizer.TEXT, r=r, g=g, b=b)

        cap.set(cv.CAP_PROP_POS_FRAMES, frameCounter + BEGIN_FRAME)
        ret, frame = cap.read()
        if SHOW_BLACK_PIXEL_DETECTORS:
            RatUtils.showDetectors(frame, PIXELS_TO_CHECK, width)
        splitVisualizer.display(frame)
        cv.imshow("splitfinder", frame)

    cap.set(cv.CAP_PROP_POS_FRAMES, BEGIN_FRAME)
    cv.destroyWindow("splitfinder")
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
    if RatUtils.isLoadingFrame(frame, PIXELS_TO_CHECK, BLACK_THRESHOLD, width - BORDER_LEFT):
        loadingFrameCounter += 1
    if SHOW_BLACK_PIXEL_DETECTORS:
        RatUtils.showDetectors(frame, PIXELS_TO_CHECK, width - BORDER_LEFT)
    frame = cv.copyMakeBorder(frame, 0, BORDER_BOTTOM, BORDER_LEFT, 0, cv.BORDER_CONSTANT, (0, 0, 0))

    if SPLITS:
        sv = DataVisualizer(FONT, y=0, width=BORDER_LEFT, height=height - BORDER_BOTTOM)
        sv.add(["Splits"], DataVisualizer.SUBTITLE)
        sv.add(["split", "with loads", "without loads"], DataVisualizer.TEXT)
        for split in SPLIT_POINTS:
            if split[1] < frameCounter:
                rm, rs = RatUtils.timeCalc(split[1] // frameRate)
                wm, ws = RatUtils.timeCalc((split[1] - loadingFrameCounter) // frameRate)
                r, g, b = 0, 255, 0
            elif split is SPLIT_POINTS[activeSplit]:
                rm, rs = RatUtils.timeCalc(frameCounter // frameRate)
                wm, ws = RatUtils.timeCalc((frameCounter - loadingFrameCounter) // frameRate)
                r, g, b = 0, 255, 255
            else:
                rm, rs = 0, 0
                wm, ws = 0, 0
                r, g, b = 200, 200, 200
            sv.add([split[0], "{:d}:{:02d}".format(rm, rs), "{:d}:{:02d}".format(wm, ws)], DataVisualizer.TEXT, r=r,
                   g=g, b=b)
        if SPLIT_POINTS[activeSplit][1] == frameCounter:
            activeSplit += 1
        if activeSplit > len(SPLIT_POINTS) - 1:
            break
        sv.display(frame)

    display()
    if VISUAL:
        if FULLSCREEN:
            cv.namedWindow("ratatool", cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty("ratatool", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        cv.imshow("ratatool", frame)
    elif frameCounter%100 == 0:
        loading = np.zeros((200, 300, 3), np.uint8)
        loadingVisualizer = DataVisualizer(FONT, 200, 300)
        loadingVisualizer.add(["loading..."], DataVisualizer.HEADER)
        loadingVisualizer.add([str(round(frameCounter/totalFrames*100, 2))], DataVisualizer.TEXT)
        loadingVisualizer.display(loading)
        cv.imshow("loading", loading)
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
    if SHOW_BLACK_PIXEL_DETECTORS:
        RatUtils.showDetectors(frame, PIXELS_TO_CHECK, width - BORDER_LEFT)
    display()
    while True:
        if cv.waitKey(1) & 0xFF == ord(EXIT_KEY):
            break
    cv.destroyWindow('ratatool')
    progressBar.finish()
