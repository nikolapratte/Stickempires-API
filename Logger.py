from enum import Enum
from typing import Set

class LFlag(Enum):
    """The LFlag Enum represents different kinds of debugging/logger flags."""
    Input = 0
    Screen = 1
    Resources = 2


class Logger:
    """The Logger class is used to log/debug things."""
    def __init__(self, enabled: bool = True, flags: LFlag or Set[LFlag] = None):
        """
        Parameters:
            - enabled: If disabled, print statements and other logging commands won't do anything when executed.
            - flags: Flags (associated with types of information) to examine. If None, all output is allowed.
        """
        self.enabled = enabled
        self.flags = set([flags]) if type(flags) is LFlag else flags


    def print(self, string: str, flags: LFlag or Set[LFlag] = None):
        """Prints the given string to the console, if at least one of the flags provided is being examined
        by the logger.
        If no flags are provided, then the string is unconditionally printed."""
        if self.enabled:
            correct_flag = True
            if self.flags is not None and flags is not None:
                correct_flag = flags in self.flags if type(flags) is LFlag else (True if self.flags & flags else False)
            
            if correct_flag:
                print(string)