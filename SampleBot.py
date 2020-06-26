from Action import Action
from BotBase import BotBase
from constants import UnitType

class SampleBot(BotBase):
    def __init__(self, *args, **kwargs):
        BotBase.__init__(self, *args, **kwargs)
        self.unit_val = 0

    async def on_step(self):
        # alternate between making miners and swords 
        actions = []
        
        actions.append(Action(self.update_res))

        if self.gold >= 150:
            if self.unit_val == 0:
                actions.append(Action(self.build, UnitType.Miner))
                self.unit_val = 1
            else:
                actions.append(Action(self.build, UnitType.Sword))
                self.unit_val = 0

        return actions