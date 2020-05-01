import getopt
import os
import sys

import cv2 as cv

from DataVisualizer import DataVisualizer


"""
INLINE DOCUMENTATION

# How it detests if the game is loading
For artistic reasons the game uses an other resolution when showing cutscenes, this resolution is kept when loading
This means that the only thing we need to do to check if the game is loading is checking if there are 2 pixels
in the top of the screen that are (almost) black
"""

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

#   END OF SETTINGS

video = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:", ["input="])
except getopt.GetoptError:
    print("run.py -i <inputvideo>")
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print("run.py -i <inputvideo>")
        sys.exit()
    elif opt in ("-i", "--inputvideo"):
        video = arg

if not os.path.isfile(video):
    print("Oops, I could not find this video {}".format(video))
    sys.exit()
cap = cv.VideoCapture(video)
cap.open(video)
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))

frameCounter = 0
loadingFrameCounter = 0
totalFrames = cap.get(cv.CAP_PROP_FRAME_COUNT)
frameRate = cap.get(cv.CAP_PROP_FPS)

dataVisualizer = DataVisualizer(FONT)

while True:
    frameCounter += 1
    ret, frame = cap.read()
    loading = True

    for pixel in PIXELS_TO_CHECK:
        if frame[pixel[0], width // 2 + pixel[1]][0] > BLACK_THRESHOLD:
            loading = False

    if loading:
        loadingFrameCounter += 1

    if SHOW_DATA_ON_SCREEN:

        dataVisualizer.add("Data", DataVisualizer.HEADER)
        dataVisualizer.add("frame: {}/{}".format(frameCounter, totalFrames), DataVisualizer.TEXT)
        dataVisualizer.add("{} loading frames".format(loadingFrameCounter), DataVisualizer.TEXT)
        dataVisualizer.add("{}%".format(round(loadingFrameCounter / frameCounter * 100, 2)), DataVisualizer.TEXT)
        dataVisualizer.add("framerate: {}".format(frameRate), DataVisualizer.TEXT)
        seconds = frameCounter // frameRate
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        dataVisualizer.add("realtime: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
        seconds = (frameCounter-loadingFrameCounter) // frameRate
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        dataVisualizer.add("without loads: {:02d}:{:02d}".format(minutes, seconds), DataVisualizer.TEXT)
        dataVisualizer.display(frame)

    if SHOW_VIDEO:
        #cv.imshow("frame", cv.resize(frame, (0, 0), fx=0.4, fy=0.4))
        cv.imshow("ratatool", frame)

    if cv.waitKey(1) & 0xFF == ord(EXIT_KEY):
        break
    if frameCounter % 30 == 0:
        print("{} seconds without loading".format((frameCounter - loadingFrameCounter) / frameRate))
    # print(loading)

cap.release()
# cv.destroyWindow('frame')
