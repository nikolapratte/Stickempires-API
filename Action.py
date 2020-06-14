from typing import Any, List

class Action:
    """The Action class represents an action that the bot takes."""
    def __init__(self, func: "function", args: List[Any]):
        self.func = func
        self.args = args