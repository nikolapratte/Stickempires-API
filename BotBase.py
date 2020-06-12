import time

import cv2
import numpy as np
from PIL import ImageGrab

class BotBase:
    """The BotBase class is meant to be inherited by the bot classes of bot creators.
    It provides a high-level interface that allows bot creators to get specific
    information from the game."""

    def __init__(self, topleft_coord: (int, int), botright_coord: (int, int)):
        """Params:
            topleft_coord: Top left coordinate of the stickempires game window (not entire browser).
            botright_coord: Bottom right coordinate of the game window.
        """
        self.topleft = topleft_coord
        self.botright = botright_coord


    def screen_record(self):
        last_time = time.time()

        while True:
            screen_coords = (self.topleft[0], self.topleft[1],self.botright[0], self.botright[1])
            screen = np.array(ImageGrab.grab(bbox=screen_coords))
            print(f"look took {time.time() - last_time} seconds.")
            last_time = time.time()

            cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break