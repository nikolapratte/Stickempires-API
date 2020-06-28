import asyncio

import cv2
import pytest

from constants import ImageName
from EmptyBot import EmptyBot
from helpers import CounterLE


@pytest.fixture
def bot1():
    topleft = (0, 0)
    botright = (800, 800)
    bot = EmptyBot(topleft, botright)

    return bot


@pytest.fixture
def swamp_500():
    return cv2.imread(ImageName["500_swamp"], cv2.IMREAD_UNCHANGED)


def test_find_numbers_500_swamp(bot1, swamp_500):
    res = CounterLE([num for num, _, _ in asyncio.run(bot1._find_numbers(swamp_500))])

    assert CounterLE("500") <= res


def test_update_gold_500_swamp(bot1, swamp_500):
    bot1.gold = 500
    asyncio.run(bot1.update_gold(swamp_500))

    assert bot1.gold == 500