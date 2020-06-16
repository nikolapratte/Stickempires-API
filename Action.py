from typing import Any, List

class Action:
    """The Action class represents an action that the bot takes."""
    def __init__(self, func: "function", *args: List[Any]):
        """If a function takes no arguments, its args attribute will be None."""
        self.func = func
        if args:
            self.args = args
        else:
            self.args = None