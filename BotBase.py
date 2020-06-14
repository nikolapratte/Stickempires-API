import abc
import asyncio
import time
from typing import List, Tuple

import cv2
from directkeys import PressKey, ReleaseKey
import numpy as np
from PIL import ImageGrab
import pyautogui

from Action import Action
from helpers import AutoPlay, ImageName, process_img, UnitType
from hexkeys import HexKey

class BotBase(abc.ABC):
    """The BotBase class is meant to be inherited by the bot classes of bot creators.
    It provides a high-level interface that allows bot creators to get specific
    information from the game."""
    # global constants
    DEFAULT_CLICK_DELAY = 0.01
    DEFAULT_BUTTON_DELAY = 0.1
    DEFAULT_ITER_RATE = 0.3
    DEFAULT_STATE = "main"

    def __init__(self, topleft_coord: (int, int), botright_coord: (int, int), iter_rate: int = DEFAULT_ITER_RATE,
    state: str = DEFAULT_STATE, autoplay_flg: AutoPlay = None):
        """
        Params:
            topleft_coord: Top left coordinate of the stickempires game window (not entire browser).
            botright_coord: Bottom right coordinate of the game window.
            iter_rate: Rate actions can be made at. Default: 0.3 seconds
            state: Name of state the bot will be started in. Default: main menu
            autoplay: Whether or not to have the bot automatically do something. Default: None (no)
            
        Notes:
            If iter_rate is too low, actions might start getting missed.
            This is because some actions in SE have a base amount of time they take (like scrolling on the
            minimap).
            If iter_rate is too high, actions may not be done frequently enough (bad for micro).
        """
        self.topleft = topleft_coord
        self.botright = botright_coord
        self.iter_rate = iter_rate
        self.state = state
        self.autoplay = autoplay_flg

    ### functions related to the inner workings of the bot
    async def main(self):
        """Main function of the bot. Manages timing of on_step, screen recording, logging, etc."""
        # setup
        screen_task = asyncio.create_task(self.screen_record())
        
        await self.main_loop()

        # cleanup
        await screen_task


    async def main_loop(self):
        """Handles game-related functions, menu navigation."""
        while True:
            if self.state == "main":
                await self.main_menu_loop()
            if self.state == "custom":
                await self.custom_menu_loop()
            if self.state == "play":
                try:
                    # NOTE not sure if timeout will work, since asyncio wasn't interrupting
                    # tasks fast enough before it seemed... (if they don't await)
                    actions: List[Action] = await asyncio.wait_for(self.on_step(), self.iter_rate)
                except asyncio.TimeoutError:
                    actions = []

                for action in actions:
                    await action.func(action.args)


    async def main_menu_loop(self):
        """Bot run loop for when its in the main menu."""
        assert self.state == "main", f"State is currently {self.state}, should be 'main' to run bot's main menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.wait_click(ImageName["custom"])

            self.state = "custom"


    async def custom_menu_loop(self):
        """Bot run loop for when its in the custom match menu."""
        assert self.state == "custom", f"State is currently {self.state}, should be 'custom' to run bot's custom menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.wait_click(ImageName["choose_map"], y_delta = 25)
            await self.wait_click(ImageName["gates"])
            # if a friend is online, easy chaos won't be default selection
            if not await self.screen_find(ImageName["easy_chaos"]):
                await self.wait_click(ImageName["choose_friend"], y_delta = 25)
                await self.wait_click(ImageName["easy_chaos"])


            self.state = "race_selection"


    async def click(self, loc: Tuple[int, int], delay: float = DEFAULT_CLICK_DELAY, left_click: bool = True) -> None:
        """Clicks on the provided coordinate on the screen, with the provided delay between
        pressing down and lifting up."""
        print(f"Location is {loc}.")

        if left_click:
            pyautogui.mouseDown(*loc, button='left')
            await asyncio.sleep(delay)
            pyautogui.mouseUp(button='left')


    async def screen_find(self, img_name: str, threshold: float = 0.9) -> (int, int, int, int):
        """Finds the given image and returns its x coord, y coord, width, and height.
        If a match cannot be found, returns None.
        If multiple matches are found, returns the first match.
        Params:
            threshold: the closer threshold is to 1, the more exact a match the function will look for."""
        screen_coords = (self.topleft[0], self.topleft[1],self.botright[0], self.botright[1])
        screen = np.array(ImageGrab.grab(bbox=screen_coords))
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

        grayscale = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(img_name, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(grayscale, template, cv2.TM_CCOEFF_NORMED)
        threshold = threshold
        loc = np.where(res >= threshold)
        
        if loc[0].size > 0:
            # note that the first array in loc is y-coordinates, while the second array is x-coordinates
            return [loc[1][0], loc[0][0], w, h]

    
    async def find_click(self, img_name: str, x_delta: float = 0, y_delta: float = 0, threshold: float = 0.9) -> bool:
        """Finds the given image and clicks on the center of it, or a point away from the center
        by x_delta and y_delta. For example, will click on (100,100) if the image's center is there,
        or (120, 120) if x_delta = 20 and y_delta = 20.
        Returns True if successfully clicked, otherwise False.
        """
        res = await self.screen_find(img_name, threshold)

        if res is None:
            return False

        x = res[0] + res[2]//2 + x_delta
        y = res[1] + res[3]//2 + y_delta

        await self.click((x, y))

        return True

    
    async def wait_click(self, img_name: str, x_delta: float = 0, y_delta: float = 0, threshold: float = 0.9) -> None:
        """Similar to find_click, but stalls with asyncio.sleep() until a click is successfully inputted on the
        provided image."""
        while not await self.find_click(img_name, x_delta = x_delta, y_delta = y_delta, threshold = threshold):
            await asyncio.sleep(1)


    async def screen_record(self):
        """Shows the screen. Contrary to the function's name, this function does not record."""
        last_time = time.time()

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
            #retval, threshold = cv2.threshold(screen, 55, 255, cv2.THRESH_BINARY)
            #threshold = cv2.adaptiveThreshold(grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
            #retval2, threshold = cv2.threshold(grayscale, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            template = cv2.imread(ImageName["custom"], 0)
            w, h = template.shape[::-1]

            res = cv2.matchTemplate(grayscale, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.9
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

            # show the screen
            cv2.imshow('original', screen)
            #cv2.imshow('Thresholded', threshold)
            #cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
            
            # ghetto way of getting the asynchronous process to respond to stop requests...
            # should be able to get rid of this when start doing more asynchronous processes?
            await asyncio.sleep(0.01)


    ### public functions (api interface)
    def run(self) -> None:
        """Starts up the bot."""
        asyncio.run(self.main())


    @abc.abstractmethod
    async def on_step(self) -> List[Action]:
        """Meant to be replaced by botmaker, this function is run on every iteration,
        generating a list of actions to take for the current iteration."""
        pass


    async def build(self, unit: UnitType) -> None:
        """Sends an order to build the provided unit.
        Does not do anything if the unit cannot be purchased."""
        val = HexKey[unit.value]

        PressKey(val)
        await asyncio.sleep(self.DEFAULT_BUTTON_DELAY)
        ReleaseKey(val)