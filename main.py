from constants import AutoPlay, ImageName, MenuState
from EmptyBot import EmptyBot
from SampleBot import SampleBot


if __name__ == "__main__":
    topleft = (0, 0)
    botright = (800, 800)
    #topleft = (785, 154)
    #botright = (1875, 1026)

    #bot = EmptyBot(topleft, botright, state = MenuState.Playing, autoplay_flg = AutoPlay.EasyChaos, debug = True)
    bot = SampleBot(topleft, botright, state= MenuState.Playing,autoplay_flg = AutoPlay.EasyChaos, debug = True)

    bot.run()