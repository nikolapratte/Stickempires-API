from Action import Action
from BotBase import BotBase
from helpers import AutoPlay, UnitType

class SampleBot(BotBase):
    async def on_step(self):
        return [Action(self.build, UnitType.Miner), Action(self.update_res)]

if __name__ == "__main__":
    topleft = (0, 0)
    botright = (800, 800)
    #bot = SampleBot((0, 0), (800, 600))
    #bot = SampleBot(topleft, botright, state = "playing", autoplay_flg=AutoPlay.EasyChaos, debug=True)
    bot = SampleBot(topleft, botright, autoplay_flg = AutoPlay.Manual, debug = True)
    bot.run()