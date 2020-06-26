from Action import Action
from BotBase import BotBase
from constants import UnitType

class EmptyBot(BotBase):
    """Does nothing except update resources."""
    async def on_step(self):
        return [Action(self.update_res)]