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
    "left_mass": "images/left_mass.PNG", # garrison if bot spawns on left side of game, advance if right
    "left_mass_miner": "images/left_mass_miner.PNG",
    "mana": "images/mana count.png",
    "defend_mass": "images/mass_defend.PNG",

    "order": "images/Order Empire.PNG",
    "play_match": "images/Play Match.PNG",
    "supply": "images/supply count.png",
    "right_mass": "images/right_mass.PNG",
    "right_mass_miner": "images/right_mass_miner.PNG",


    "500_swamp": "images/test/500_swamp_0.PNG"
}


class Mass(Enum):
    """The Mass enum has different mass action options (garrison, defend, attack)."""
    Garrison = 0
    Defend = 1
    Attack = 2
    MinerGarrison = 3
    MinerAdvance = 4


class MenuState(Enum):
    """The MenuState enum represents different menus the bot can be in."""
    Main = 0
    Custom = 1
    Race = 2
    Loading = 3
    Playing = 4

"""Threshold nums represents the thresholds necessary to detect certain numbers
(using cv2.matchThreshold)."""
THRESHOLDS_NUMS = {
                0.5: "1",
                0.6: "0",
                0.7: "23456789"
}

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

"""UnitCost gives the cost of units as Tuple(gold, mana, supply)."""
UnitCost = {
    UnitType.Miner: (150, 0, 2),
    UnitType.Sword: (125, 0, 1)
}