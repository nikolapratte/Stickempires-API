from Action import Action
from BotBase import BotBase
from helpers import AutoPlay, UnitType

class SampleBot(BotBase):
    async def on_step(self):
        return [Action(self.build, UnitType.Miner)]

if __name__ == "__main__":
    topleft = (0, 0)
    botright = (800, 600)
    #bot = SampleBot((0, 0), (800, 600))
    bot = SampleBot(topleft, botright, autoplay_flg=AutoPlay.EasyChaos)
    bot.run()