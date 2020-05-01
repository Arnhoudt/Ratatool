def isLoadingFrame(frame, pixelsToCheck, blackThreshold, screenWidth):
    loading = True
    for pixel in pixelsToCheck:
        if frame[pixel[0], screenWidth // 2 + pixel[1]][0] > blackThreshold:
            loading = False
    return loading


def timeCalc(seconds):
    return int(seconds // 60), int(seconds % 60)
