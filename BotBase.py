import time

import cv2
from directkeys import PressKey
from hexkeys import HexKey
import numpy as np
from PIL import ImageGrab
import pyautogui

from helpers import process_img

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

        time.sleep(3)
        while True:
            PressKey(HexKey["1"])
            pyautogui.click()
            time.sleep(1)
            # get current screen
            screen_coords = (self.topleft[0], self.topleft[1],self.botright[0], self.botright[1])
            screen = np.array(ImageGrab.grab(bbox=screen_coords))
            
            print(f"loop took {time.time() - last_time} seconds.")
            last_time = time.time()
            # turn screen into edges screen
            screen = process_img(screen)
            cv2.imshow('window', screen)
            #cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break