import abc
import asyncio
from collections import defaultdict
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
from Logger import Logger

class BotBase(abc.ABC):
    """The BotBase class is meant to be inherited by the bot classes of bot creators.
    It provides a high-level interface that allows bot creators to get specific
    information from the game."""
    # global constants
    DEFAULT_BUTTON_DELAY = 0.1
    DEFAULT_CLICK_DELAY = 0.01
    DEFAULT_ITER_RATE = 0.3
    DEFAULT_RETRY_DELAY = 0.1
    DEFAULT_STATE = "main"

    def __init__(self, topleft_coord: (int, int), botright_coord: (int, int), iter_rate: int = DEFAULT_ITER_RATE,
    state: str = DEFAULT_STATE, autoplay_flg: AutoPlay = None, debug: bool = False):
        """
        Params:
            topleft_coord: Top left coordinate of the stickempires game window (not entire browser).
            botright_coord: Bottom right coordinate of the game window.
            iter_rate: Rate actions can be made at. Default: 0.3 seconds
            state: Name of state the bot will be started in. Default: main menu
            autoplay: Whether or not to have the bot automatically do something. Default: None (no)
            debug: Whether or not to have debug messages on. Default: False
            
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
        self.debug = debug

        self.logger = Logger()

        self.gold = 0
        self.mana = 0

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
        if self.autoplay == AutoPlay.Manual:
            return

        while True:
            if self.state == "main":
                await self.main_menu_loop()
            if self.state == "custom":
                await self.custom_menu_loop()
            if self.state == "race_selection":
                await self.race_menu_loop()
            if self.state == "loading":
                await self.loading_loop()
            if self.state == "playing":
                await self.playing_loop()


    async def main_menu_loop(self):
        """Bot run loop for when its in the main menu."""
        assert self.state == "main", f"State is currently {self.state}, should be 'main' to run bot's main menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.wait_click(ImageName["custom"])

            self.state = "custom"


    async def custom_menu_loop(self):
        """Bot run loop for custom match menu."""
        assert self.state == "custom", f"State is currently {self.state}, should be 'custom' to run bot's custom menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.wait_click(ImageName["choose_map"], y_delta = 25)
            await self.wait_click(ImageName["gates"])
            # if a friend is online, easy chaos won't be default selection
            if not await self.screen_find(ImageName["easy_chaos"]):
                await self.wait_click(ImageName["choose_friend"], y_delta = 25)
                await self.wait_click(ImageName["easy_chaos"])

            await self.wait_click(ImageName["play_match"])

            self.state = "race_selection"


    async def race_menu_loop(self):
        """Bot run loop for race selection menu."""
        assert self.state == "race_selection", f"State is currently {self.state}, should be 'race_selection' to run bot's race selection loop."
        # TODO wait until loading screen starts to switch?
        await self.wait_click(ImageName["order"])

        self.state = "loading"


    async def loading_loop(self):
        """Bot's loading (players, map screen) loop."""
        assert self.state == "loading", f"State is currently {self.state}, should be 'loading' to run bot's loading loop."
        # TODO fix with appropriate logic to notice when loading screen is over, as well as record opponent race.
        await asyncio.sleep(2)

        self.state = "playing"


    async def playing_loop(self):
        """Bot's playing loop, responsible for playing the game."""
        assert self.state == "playing", f"State is currently {self.state}, should be 'playing' to run bot's playing loop."
        try:
            # NOTE not sure if timeout will work, since asyncio wasn't interrupting
            # tasks fast enough before it seemed... (if they don't await)
            actions: List[Action] = await asyncio.wait_for(self.on_step(), self.iter_rate)
        except asyncio.TimeoutError:
            actions = []

        for action in actions:
            # TODO create tasks for actions that can be done asynchronously to other tasks (i.e. sending units
            # on minimap and moving minimap, or building units while microing)
            if action.args is None:
                await action.func()
            else:
                await action.func(*action.args)
            

    async def click(self, loc: Tuple[int, int], delay: float = DEFAULT_CLICK_DELAY, left_click: bool = True) -> None:
        """Clicks on the provided coordinate on the screen, with the provided delay between
        pressing down and lifting up."""
        print(f"Location is {loc}.")

        if left_click:
            pyautogui.mouseDown(*loc, button='left')
            await asyncio.sleep(delay)
            pyautogui.mouseUp(button='left')


    async def screen_find(self, img_name: str, threshold: float = 0.9, all_imgs: bool = False,
    blackwhite: int = 0) -> Tuple[int, int, int, int] or Tuple[List[int], List[int], int, int]:
        """Finds the given image and returns its x coord, y coord, width, and height.
        If a match cannot be found, returns None.
        If multiple matches are found, returns the first match (by default).
        Params:
            threshold: the closer threshold is to 1, the more exact a match the function will look for.
            all: whether to return all matches or not. If True, return is of type Tuple[List[int], List[int], int, int],
            where the first list is x-coordinates and the second list is y-coordinates. If False, only the first match
            is returned.
            blackwhite: Black and white threshold. Default: 0 (will not apply black and white filter)"""
        screen_coords = (self.topleft[0], self.topleft[1],self.botright[0], self.botright[1])
        screen = np.array(ImageGrab.grab(bbox=screen_coords))
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        if blackwhite:
            _, screen = cv2.threshold(screen, blackwhite, 255, cv2.THRESH_BINARY)

        template = cv2.imread(img_name, 0) # TODO for blackwhite
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
            await asyncio.sleep(self.DEFAULT_RETRY_DELAY)


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
            _, blackwhite = cv2.threshold(grayscale, 200, 255, cv2.THRESH_BINARY)
            #retval, threshold = cv2.threshold(screen, 55, 255, cv2.THRESH_BINARY)
            #threshold = cv2.adaptiveThreshold(grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
            #retval2, threshold = cv2.threshold(grayscale, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            #template = cv2.imread(ImageName["0"], 0)
            #w, h = template.shape[::-1]

            for num in "0123456789":
                template = cv2.imread(ImageName[num], 0)
                w, h = template.shape[::-1]

                res = cv2.matchTemplate(blackwhite, template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.75
                loc = np.where(res >= threshold)

                for pt in zip(*loc[::-1]):
                    cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

            # show the screen
            cv2.imshow('original', screen)
            cv2.imshow('blackwhite', blackwhite)
            #cv2.imshow('Thresholded', threshold)
            #cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
            
            # TODO ghetto way of getting the asynchronous process to respond to stop requests...
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


    async def update_res(self) -> None:
        """Updates gold and mana attributes."""

        # numbers is a list of tuples of the form (number, x_coord, y_coord)
        numbers = []
        for num in "0123456789":
            xs, ys, _, _ = await self.screen_find(ImageName[num], all_imgs = True)
            numbers += [(num, x, y) for x, y in zip(xs, ys)]
        
        numbers = sorted(numbers, key = lambda x: x[1])

        if self.debug:
            self.logger.print(f"BotBase.update_res: numbers on screen detected are {numbers}")

        # algorithm to find the division indicies between gold-mana, and mana-supply
        DIVISION_LENGTH = 3 # if the difference in x-coord between two numbers is greater
        # than this number times the last difference, then assume its a field division.

        idx = 0
        cur_val = 0
        dif = 0
        division_idxs = [] # division indicies are the first number in the new field

        while True:
            if idx >= len(numbers):
                break

            last_val = cur_val
            cur_val = numbers[idx]

            last_dif = dif
            dif = cur_val - last_val

            if idx > 0:
                # last values won't be accurate for first index
                if dif >= DIVISION_LENGTH*last_dif:
                    division_idxs.append(idx)

            idx += 1

        # end algorithm

        if self.debug:
            self.logger.print(f"BotBase.update_res: division indicies between numbers are {division_idxs}")

        # TODO inefficient way of converting a stream of numbers into the whole number (not dealing with str more efficient)
        self.gold = int(''.join(str(num) for num in numbers[:division_idxs[0]]))
        self.mana = int(''.join(str(num) for num in numbers[division_idxs[0]:division_idxs[1]]))

        if self.debug:
            self.logger.print(f"BotBase.update_res: Detected {self.gold} gold and {self.mana} mana.")

        