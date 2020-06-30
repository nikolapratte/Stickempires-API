import asyncio
import time
from typing import List, Tuple

import cv2
import numpy as np
from PIL import ImageGrab

from constants import ImageName, THRESHOLDS_NUMS


class ScreenHandler:
    """The ScreenHandler class handles actions relating to the screen."""
    def __init__(self, topleft: Tuple[int, int], botright: Tuple[int, int]):
        """
        Params:
            topleft: Coordinates of the top left corner of the screen.
            botright: Coordinates of the bottom right corner of the screen.
        """
        self.topleft = topleft
        self.botright = botright

    
    def get_fullscreen(self) -> "image":
        """Returns the entire screen the bot sees."""
        return self.get_screen(self.topleft, self.botright)
    

    def get_screen(self, topleft: Tuple[int, int], botright: Tuple[int, int]) -> "image":
        """Returns the part of the screen contained within the given coordinates."""
        screen_coords = (topleft[0], topleft[1], botright[0], botright[1])
        screen = np.array(ImageGrab.grab(bbox=screen_coords))
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

        return screen

    
    async def screen_find(self, img_name: str, threshold: float = 0.9, all_imgs: bool = False,
    blackwhite: int = 0, screen: "image" = None) -> Tuple[int, int, int, int] or Tuple[List[int], List[int], int, int]:
        """Finds the given image and returns its x coord, y coord, width, and height.
        If a match cannot be found, returns None.
        If multiple matches are found, returns the first match (by default).
        Params:
            threshold: the closer threshold is to 1, the more exact a match the function will look for.
            all: whether to return all matches or not. If True, return is of type Tuple[List[int], List[int], int, int],
            where the first list is x-coordinates and the second list is y-coordinates. If False, only the first match
            is returned.
            blackwhite: Black and white threshold. Default: 0 (will not apply black and white filter)
            screen: screen image to use. Defaults to current bot screen."""
        if screen is None:
            screen = self.get_fullscreen()
        
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        if blackwhite:
            _, screen = cv2.threshold(screen, blackwhite, 255, cv2.THRESH_BINARY)

        template = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        threshold = threshold
        loc = np.where(res >= threshold)

        if loc[0].size > 0:
            # note that the first array in loc is y-coordinates, while the second array is x-coordinates
            if all_imgs:
                return [loc[1], loc[0], w, h]
            else:
                return [loc[1][0], loc[0][0], w, h]


    def highlightMatching(self, screen, screen_match, img_name, threshold: float = 0.9) -> None:
        """Highlights the provided image of img_name where it is found on screen_match,
        on screen (in case screen_match is different, for example grayscale or black and white)."""
        template = cv2.imread(img_name, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen_match, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

    
    async def show(self):
        """Shows the screen."""
        last_time = time.time()

        while True:
            # get current screen
            screen = self.get_fullscreen()

            print(f"loop took {time.time() - last_time} seconds.")
            last_time = time.time()
            
            grayscale = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            _, blackwhite = cv2.threshold(grayscale, 200, 255, cv2.THRESH_BINARY)

            for name in ("left_mass", "left_mass_miner", "right_mass", "right_mass_miner"):
                self.highlightMatching(screen, grayscale, ImageName[name])
            self.highlightMatching(screen, grayscale, ImageName["mass_defend"], 0.85)


            # show the screen
            cv2.imshow('original', screen)
            #cv2.imshow('other', grayscale)
            
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
            
            # TODO ghetto way of getting the asynchronous process to respond to stop requests...
            # should be able to get rid of this when start doing more asynchronous processes?
            await asyncio.sleep(0.01)