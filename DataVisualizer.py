import cv2 as cv


class DataVisualizer:
    HEADER = 1
    SUBTITLE = 2
    TEXT = 3

    def __init__(self, font, width=300, height=300, x=0, y=0, marginLeft=20, colWidth = 120):
        self.font = font
        self.marginLeft = marginLeft
        self.x = x
        self.y = y
        self.yPos = y
        self.data = []
        self.width = width
        self.height = height
        self.colWidth = colWidth

    def add(self, text, size, r=255, g=255, b=255):
        self.data.append({"text": text, "size": size, "red": r, "green": g, "blue": b})

    def display(self, frame):
        cv.rectangle(frame, (self.x, self.y), (self.width + self.x, self.height + self.y), (20, 20, 20), -1)
        for info in self.data:
            size = 0
            if info["size"] == self.HEADER:
                self.yPos += 50
                size = 1.5

            if info["size"] == self.SUBTITLE:
                self.yPos += 40
                size = 1

            if info["size"] == self.TEXT:
                self.yPos += 20
                size = 0.5

            posx = self.marginLeft
            for col in info["text"]:
                cv.putText(frame, col, (posx, self.yPos), self.font, size,
                           (info["blue"], info["green"], info["red"]), int(size + 0.5), cv.LINE_AA)
                posx += self.colWidth
            if info["size"] == self.HEADER:
                self.yPos += 10

            if info["size"] == self.SUBTITLE:
                self.yPos += 10

        self.data = []
        self.yPos = self.y
