import cv2 as cv


class DataVisualizer:
    HEADER = 1
    SUBTITLE = 2
    TEXT = 3

    data = []

    yPos = 0

    def __init__(self, font, marginLeft=30):
        self.font = font
        self.marginLeft = marginLeft

    def add(self, text, size):
        self.data.append({"text": text, "size": size})

    def display(self, frame):
        cv.rectangle(frame, (0, 0), (300, 300), (0, 0, 0), -1)
        for info in self.data:
            if info["size"] == self.HEADER:
                self.yPos += 50
                cv.putText(frame, info["text"], (self.marginLeft, self.yPos), self.font, 1.5, (255, 255, 255), 2, cv.LINE_AA)

            if info["size"] == self.SUBTITLE:
                self.yPos += 40
                cv.putText(frame, info["text"], (self.marginLeft + 3, self.yPos), self.font, 1, (255, 255, 255), 1.5, cv.LINE_AA)

            if info["size"] == self.TEXT:
                self.yPos += 25
                cv.putText(frame, info["text"], (self.marginLeft + 6, self.yPos), self.font, 0.5, (255, 255, 255), 1, cv.LINE_AA)
        self.data = []
        self.yPos = 0
