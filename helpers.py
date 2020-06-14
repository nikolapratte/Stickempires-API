from enum import Enum

import cv2

class AutoPlay(Enum):
    """The AutoPlay enum represents autoplay options for the bot."""
    EasyChaos = 1


class UnitType(Enum):
    """The UnitType enum represents units that the bot can build (as Order)."""
    Miner = "1"
    Sword = "2"
    Archer = "3"
    Meric = "4"
    Magikill = "5"
    Spear = "6"
    Ninja = "7"
    Albow = '8'
    Giant = '9'

"""The ImageName dictionary contains the filenames of images used by the bot."""
ImageName = {
    "choose_friend": "images/Custom Friend.PNG"
    "choose_map": "images/Custom Map.PNG"
    "custom": "images/Custom Match Button.PNG"
}


def process_img(image):
    """Processes a normal image into an edges image."""
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1 = 100, threshold2 = 200)
    return processed_img