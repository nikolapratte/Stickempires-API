from enum import Enum


class AutoPlay(Enum):
    """The AutoPlay enum represents autoplay options for the bot."""
    Manual = 0
    EasyChaos = 1


"""The ImageName dictionary contains the filenames of images used by the bot."""
ImageName = {
    "0": "images/0.png",
    "1": "images/1.png",
    "2": "images/2.png",
    "3": "images/3.png",
    "4": "images/4.png",

    "5": "images/5.png",
    "6": "images/6.png",
    "7": "images/7.png",
    "8": "images/8.png",
    "9": "images/9.png",

    "choose_friend": "images/Choose Friend.PNG",
    "choose_map": "images/Choose Map.PNG",
    "custom": "images/Custom Match Button.PNG",

    "easy_chaos": "images/Easy Chaos AI.PNG",

    "gates": "images/Gates.PNG",
    "gold": "images/gold count.png",
    "mana": "images/mana count.png",

    "order": "images/Order Empire.PNG",
    "play_match": "images/Play Match.PNG",
    "supply": "images/supply count.png"
}


class MenuState(Enum):
    """The MenuState enum represents different menus the bot can be in."""
    Main = 0
    Custom = 1
    Race = 2
    Loading = 3
    Playing = 4


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