from Action import Action
from BotBase import BotBase
from constants import AutoPlay, UnitType

class SampleBot(BotBase):
    async def on_step(self):
        return [Action(self.update_res)]

        #return [Action(self.build, UnitType.Miner), Action(self.update_res)]