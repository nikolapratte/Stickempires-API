import asyncio
from typing import Tuple

import pyautogui

from ScreenHandler import ScreenHandler


class InputHandler:
    """The InputHandler class handles inputs to Stickempires."""
    DEFAULT_CLICK_DELAY = 0.01
    DEFAULT_RETRY_DELAY = 0.1
    
    def __init__(self):
        pass


    async def click(self, loc: Tuple[int, int], delay: float = DEFAULT_CLICK_DELAY, left_click: bool = True) -> None:
        """Clicks on the provided coordinate on the screen, with the provided delay between
        pressing down and lifting up."""
        #print(f"Location is {loc}.")

        if left_click:
            pyautogui.mouseDown(*loc, button='left')
            await asyncio.sleep(delay)
            pyautogui.mouseUp(button='left')

    
    async def find_click(self, screen: ScreenHandler,img_name: str, 
    x_delta: float = 0, y_delta: float = 0, threshold: float = 0.9) -> bool:
        """Finds the given image and clicks on the center of it, or a point away from the center
        by x_delta and y_delta. For example, will click on (100,100) if the image's center is there,
        or (120, 120) if x_delta = 20 and y_delta = 20.
        Returns True if successfully clicked, otherwise False.
        """
        res = await screen.screen_find(img_name, threshold)

        if res is None:
            return False

        x = res[0] + res[2]//2 + x_delta
        y = res[1] + res[3]//2 + y_delta

        await self.click((x, y))

        return True

    
    async def wait_click(self, screen: ScreenHandler, img_name: str, x_delta: float = 0, y_delta: float = 0,
    threshold: float = 0.9, retry_delay: float = DEFAULT_RETRY_DELAY) -> None:
        """Similar to find_click, but stalls with asyncio.sleep() until a click is successfully inputted on the
        provided image."""
        while not await self.find_click(screen, img_name, x_delta = x_delta, y_delta = y_delta, threshold = threshold):
            await asyncio.sleep(retry_delay)