The Stickempires (SE) API provides an interface to make Stickempires bots. Since SE doesn't
have an official API, this API relies on screen capturing Stickempires and abstracting away
those details of the game so bot makers can focus on higher-level details.

Since an installer is not included, I will write out dependencies I needed (you may prefer
others depending on your computer specs):
    openCV/cv2 (image recognition)
    ffmpeg (playing videos)
    pyautogui (screen capture)

Installation guide:
    1. Download numpy, pyautogui ("pip install numpy", "pip install pyautogui")
    2. Download cv2.
        a) Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
        b) Download the appropriate version for you.
        c) Install the whl file using pip.
    3. Download ffmpeg.
        a) Download the latest ffmpeg version here: https://ffmpeg.zeranoe.com/builds/
        b) Extract the files and put it somewhere safe (Program Files, for example)
        c) Add the bin folder to the PATH variable

        alternatively, a python ffmpeg wrapper can be installed if you would like to keep it in
        a virtual environment. This article seemed good:
        https://stackoverflow.com/questions/48811312/install-ffmpeg-in-to-virtual-environment 