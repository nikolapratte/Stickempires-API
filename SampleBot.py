from Action import Action
from BotBase import BotBase
from constants import Mass, UnitType

class SampleBot(BotBase):
    def __init__(self, *args, **kwargs):
        BotBase.__init__(self, *args, **kwargs)
        self.unit_val = 0
        self.iteration = 0

    async def on_step(self):
        ### build() example: alternate between making miners and swords 
        actions = []
        
        actions.append(Action(self.update_res))

        if self.gold >= 150:
            if self.unit_val == 0:
                actions.append(Action(self.build, UnitType.Miner))
                self.unit_val = 1
            else:
                actions.append(Action(self.build, UnitType.Sword))
                self.unit_val = 0

        ### mass() example: do a variety of mass actions, change whether bot thinks they are on right/left
        ITERATIONS_PER_ACTION = 5

        mass_actions = (Mass.Attack, Mass.Defend, Mass.Garrison, Mass.MinerAdvance, Mass.MinerGarrison)
        idx = (self.iteration // ITERATIONS_PER_ACTION) % len(mass_actions)

        # alternate left/right side every 50 iterations
        if self.iteration != 0 and (self.iteration % (ITERATIONS_PER_ACTION * len(mass_actions))) == 0:
            self.on_left = False if self.on_left else True

        actions.append(Action(self.mass, mass_actions[idx]))

        ### cleanup

        self.logger.print(f"Currently on iteration {self.iteration}.")
        self.iteration += 1

        return actions