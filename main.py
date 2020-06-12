

from BotBase import BotBase

if __name__ == "__main__":
    bot = BotBase((0, 0), (800, 600))
    bot.screen_record()

"""import cv2
import matplotlib
import numpy as np

if __name__ == "__main__":
    cap = cv2.VideoCapture("sample.mp4")

    while cap.isOpened():
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow('frame', gray)
        cv2.waitKey(25)

    cap.release()
    cv2.destroyAllWindows()"""