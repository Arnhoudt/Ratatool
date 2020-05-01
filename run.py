import getopt
import os
import sys

import cv2 as cv
import numpy as np

import RatUtils
from progress.bar import Bar
from PIL import ImageGrab

from DataVisualizer import DataVisualizer

#   SETTINGS

# This is how black black must be
BLACK_THRESHOLD = 5

# PIXELS TO CHECK
# Checks the pixels relative to the top center of the video [row, col]
# More pixels = less false detections
PIXELS_TO_CHECK = [[50, -50], [50, 50]]

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

#   END OF SETTINGS

video = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "ldvi:s:b:e:", ["input=", "skips=", "begin_frame=", "end_frame="])
except getopt.GetoptError:
    print("run.py -i <inputvideo> -s <progress_bar_frame_skips> -b <begin_frame> -e <end_frame>")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-i", "--inputvideo"):
        video = arg
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

if not VISUAL and SHOW_BLACK_PIXEL_DETECTORS:
    VISUAL = True  # If a user enables black pixel detectors the visual should also be shown

if not os.path.isfile(video):
    print("Oops, I could not find this video {}".format(video))
    sys.exit()
cap = cv.VideoCapture()
cap.open(video)
cap.set(cv.CAP_PROP_POS_FRAMES, BEGIN_FRAME)

width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))

frameCounter = 0
loadingFrameCounter = 0
frameRate = cap.get(cv.CAP_PROP_FPS)
if END_FRAME == -1:
    END_FRAME = cap.get(cv.CAP_PROP_FRAME_COUNT)
totalFrames = END_FRAME - BEGIN_FRAME

dataVisualizer = DataVisualizer(FONT)

if not VISUAL:
    progressBar = Bar('Processing', max=totalFrames // PROGRESS_BAR_FRAME_SKIPS, suffix='%(index)d/%(max)d - %('
                                                                                        'percent).1f%% - %(eta)ds')

while True:
    frameCounter += 1
    if LIVE_MODE:
        printscreen_pil = ImageGrab.grab()
        frame = cv.resize(np.array(printscreen_pil, dtype="uint8"), (0, 0), fx=0.2, fy=0.2)
    else:
        ret, frame = cap.read()

    if RatUtils.isLoadingFrame(frame, PIXELS_TO_CHECK, BLACK_THRESHOLD, width):
        loadingFrameCounter += 1

    if VISUAL:
        dataVisualizer.add("Data", DataVisualizer.HEADER)
        dataVisualizer.add("frame: {}/{}".format(frameCounter, totalFrames), DataVisualizer.TEXT)
        dataVisualizer.add("{} loading frames".format(loadingFrameCounter), DataVisualizer.TEXT)
        dataVisualizer.add("{}%".format(round(loadingFrameCounter / frameCounter * 100, 2)), DataVisualizer.TEXT)
        dataVisualizer.add("framerate: {}".format(frameRate), DataVisualizer.TEXT)
        minutes, seconds = RatUtils.timeCalc(frameCounter // frameRate)
        dataVisualizer.add("realtime: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
        minutes, seconds = RatUtils.timeCalc(frameCounter // frameRate)
        dataVisualizer.add("without loads: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
        dataVisualizer.display(frame)
        cv.imshow("ratatool", frame)
    elif frameCounter % PROGRESS_BAR_FRAME_SKIPS == 0:
        progressBar.next()

    if cv.waitKey(1) & 0xFF == ord(EXIT_KEY):
        break
    if frameCounter == END_FRAME - BEGIN_FRAME:
        break

cap.release()
if VISUAL and frameCounter == END_FRAME - BEGIN_FRAME:
    cv.waitKey(0)
    cv.destroyWindow('frame')
else:
    progressBar.finish()
