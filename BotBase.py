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
from constants import AutoPlay, ImageName, MenuState, THRESHOLDS_NUMS, UnitType, UnitCost
from helpers import CounterLE, process_img
from InputHandler import InputHandler
from hexkeys import HexKey
from Logger import Logger
from ScreenHandler import ScreenHandler

class BotBase(abc.ABC):
    """The BotBase class is meant to be inherited by the bot classes of bot creators.
    It provides a high-level interface that allows bot creators to get specific
    information from the game."""
    DEFAULT_BUTTON_DELAY = 0.1
    DEFAULT_ITER_RATE = 0.3
    DEFAULT_STATE = MenuState.Main

    STARTING_GOLD = 500
    STARTING_MANA = 0

    def __init__(self, topleft_coord: (int, int), botright_coord: (int, int), iter_rate: int = DEFAULT_ITER_RATE,
    state: MenuState = DEFAULT_STATE, autoplay_flg: AutoPlay = None, debug: bool = False):
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

        self.input = InputHandler()
        self.logger = Logger(debug)
        self.screen = ScreenHandler(self.topleft, self.botright)

        self.gold = self.STARTING_GOLD
        self.mana = self.STARTING_MANA

    ### functions related to the inner workings of the bot


    async def main(self):
        """Main function of the bot. Manages timing of on_step, screen recording, logging, etc."""
        # setup
        if self.debug:
            screen_task = asyncio.create_task(self.screen.show())
        
        await self.main_loop()

        # cleanup
        if self.debug:
            await screen_task


    async def main_loop(self):
        """Handles game-related functions, menu navigation."""
        if self.autoplay == AutoPlay.Manual:
            return

        while True:
            if self.state == MenuState.Main:
                await self.main_menu_loop()
            if self.state == MenuState.Custom:
                await self.custom_menu_loop()
            if self.state == MenuState.Race:
                await self.race_menu_loop()
            if self.state == MenuState.Loading:
                await self.loading_loop()
            if self.state == MenuState.Playing:
                await self.playing_loop()


    async def main_menu_loop(self):
        """Bot run loop for when its in the main menu."""
        assert self.state == MenuState.Main, f"State is currently {self.state}, should be 'main' to run bot's main menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.input.wait_click(self.screen, ImageName["custom"])

            self.state = MenuState.Custom


    async def custom_menu_loop(self):
        """Bot run loop for custom match menu."""
        assert self.state == MenuState.Custom, f"State is currently {self.state}, should be 'custom' to run bot's custom menu loop."

        if self.autoplay == AutoPlay.EasyChaos:
            await self.input.wait_click(self.screen, ImageName["choose_map"], y_delta = 25)
            await self.input.wait_click(self.screen, ImageName["gates"])
            # if a friend is online, easy chaos won't be default selection
            if not await self.screen.screen_find(ImageName["easy_chaos"]):
                await self.input.wait_click(self.screen, ImageName["choose_friend"], y_delta = 25)
                await self.input.wait_click(self.screen, ImageName["easy_chaos"])

            await self.input.wait_click(self.screen, ImageName["play_match"], threshold = 0.7)

            self.state = MenuState.Race


    async def race_menu_loop(self):
        """Bot run loop for race selection menu."""
        assert self.state == MenuState.Race, f"State is currently {self.state}, should be 'race_selection' to run bot's race selection loop."
        # TODO wait until loading screen starts to switch?
        await self.input.wait_click(self.screen, ImageName["order"])

        self.state = MenuState.Loading


    async def loading_loop(self):
        """Bot's loading (players, map screen) loop."""
        assert self.state == MenuState.Loading, f"State is currently {self.state}, should be 'loading' to run bot's loading loop."
        # TODO fix with appropriate logic to notice when loading screen is over, as well as record opponent race.
        await asyncio.sleep(2)

        self.state = MenuState.Playing


    async def playing_loop(self):
        """Bot's playing loop, responsible for playing the game."""
        assert self.state == MenuState.Playing, f"State is currently {self.state}, should be 'playing' to run bot's playing loop."
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
        # only proceed if can buy the unit
        g, m, s = UnitCost[unit]
        if g <= self.gold:
            self.gold -= g
        else:
            return


        val = HexKey[unit.value]

        PressKey(val)
        await asyncio.sleep(self.DEFAULT_BUTTON_DELAY)
        ReleaseKey(val)


    async def _find_numbers(self, screen_match: "image") -> List[Tuple[str, int, int]]:
        """Finds resource (gold, mana) numbers in the given image,
        returning matches and their coordinates."""
        # TODO improve by changing to priority queue, gets rid of a little waste later on in update_res

        numbers = []

        for threshold, nums in THRESHOLDS_NUMS.items():
            for num in nums:
                res = await self.screen.screen_find(ImageName[num], all_imgs = True,
                screen = screen_match, threshold = threshold, blackwhite = 200)

                if res:
                    xs, ys, _, _ = res
                    numbers += [(num, x, y) for x, y in zip(xs, ys)]

        self.logger.print(f"BotBase._find_numbers: Found {numbers} numbers.")

        return numbers


    async def update_res(self) -> None:
        """Updates gold and mana attributes."""
        
        gold_res = await self.screen.screen_find(ImageName["gold"], threshold = 0.7)
        mana_res = await self.screen.screen_find(ImageName["mana"], threshold = 0.7)
        supply_res = await self.screen.screen_find(ImageName["supply"], threshold = 0.7)

        if gold_res and mana_res and supply_res:
            gold_x, gold_y, _, _ = gold_res
            mana_x, mana_y, _, mana_h = mana_res
            supply_x, _, _, _ = supply_res
        else:
            self.logger.print(f"Gold: {gold_res}, mana: {mana_res}, supply: {supply_res}.")
            self.logger.print("BotBase.update_res: Unable to find gold, mana, or supply images.")
            return


        # image of the space between gold and mana (with a little extra space)
        gold_mana_img = self.screen.get_screen((gold_x, gold_y * 0.9), (mana_x, gold_y + mana_h))
        mana_supply_img = self.screen.get_screen((mana_x, mana_y * 0.9), (supply_x, mana_y + mana_h))


        # sort by horizontal coordinate (left-most number have the smallest x value)
        gold_nums = CounterLE([num for num, _, _ in await self._find_numbers(gold_mana_img)])

        # return prematurely if no numbers detected for gold
        if len(gold_nums) == 0:
            self.logger.print("BotBase.update_res: could not detect gold.")
            return

        # enumerate possible gold amounts
        # TODO +20 for center
        # maybe can check whether or not I have center
        realistic_gold_changes = [75, 150, 225, 300]
        # realistic_gold_changes = [20, 75, 95, 150, 170, 225, 245, 300, 320]
        pos_golds: List[str] = [str(self.gold + x) for x in realistic_gold_changes]

        self.logger.print(f"Gold numbers are: {gold_nums}")
        self.logger.print(f"Possible gold values considered are: {pos_golds}.")

        for pos_gold in pos_golds:
            pos_gold_ctr = CounterLE(pos_gold)
            if pos_gold_ctr <= gold_nums:
                self.gold = int(pos_gold)
                break

        self.logger.print(f"BotBase.update_res: {self.gold} gold detected.")

        # TODO return first possible match, since I'd rather have the bot use less gold
        # than it has than more gold.

        """
        gold_amt = sorted(await self._find_numbers(gold_mana_img, 0.7), key = lambda x: x[1])
        mana_amt = sorted(await self._find_numbers(mana_supply_img, 0.7), key = lambda x: x[1])

        gold_amt_str = ''.join(num for num, _, _ in gold_amt)
        mana_amt_str = ''.join(num for num, _, _ in mana_amt)

        if gold_amt_str:
            self.gold = int(gold_amt_str)
        if mana_amt_str:
            self.mana = int(mana_amt_str)

        if self.debug:
            if not gold_amt_str:
                self.logger.print("BotBase.update_res: could not detect gold.")
            else:
                self.logger.print(f"BotBase.update_res: {self.gold} gold detected.")

            if not mana_amt_str:
                self.logger.print("BotBase.update_res: could not detect mana.")
            else:
                self.logger.print(f"BotBase.update_res: {self.mana} mana detected.")

        """