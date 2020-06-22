from constants import AutoPlay, ImageName, MenuState
from SampleBot import SampleBot

if __name__ == "__main__":
    topleft = (0, 0)
    botright = (800, 800)
    #topleft = (785, 154)
    #botright = (1875, 1026)

    #bot = SampleBot((0, 0), (800, 600))
    bot = SampleBot(topleft, botright, state = MenuState.Main, autoplay_flg=AutoPlay.EasyChaos, debug=True)
    #bot = SampleBot(topleft, botright, autoplay_flg = AutoPlay.Manual, debug = True)

    bot.run()