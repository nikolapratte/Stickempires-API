import asyncio
import time

import cv2
from directkeys import PressKey, ReleaseKey
from helpers import UnitType
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

    ### functions related to the inner workings of the bot

    async def screen_record(self):
        last_time = time.time()

        time.sleep(3)
        while True:
            # get current screen
            screen_coords = (self.topleft[0], self.topleft[1],self.botright[0], self.botright[1])
            screen = np.array(ImageGrab.grab(bbox=screen_coords))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

            print(f"loop took {time.time() - last_time} seconds.")
            last_time = time.time()
            # process the screen a bit
            #screen = process_img(screen)
            
            grayscale = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            retval, threshold = cv2.threshold(screen, 55, 255, cv2.THRESH_BINARY)
            #threshold = cv2.adaptiveThreshold(grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
            #retval2, threshold = cv2.threshold(grayscale, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # show the screen
            cv2.imshow('original', screen)
            cv2.imshow('Thresholded', threshold)
            #cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break

    
    ### public functions (api interface)

    def run(self) -> None:
        """Starts up the bot."""
        asyncio.run(self.screen_record())


    async def build(self, unit: UnitType) -> None:
        """Sends an order to build the provided unit.
        Does not do anything if the unit cannot be purchased."""
        val = HexKey[unit.value]

        PressKey(val)
        await asyncio.sleep(0.1)
        ReleaseKey(val)