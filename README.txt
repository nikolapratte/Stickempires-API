The Stickempires (SE) API provides an interface to make Stickempires bots. Since SE doesn't
have an official API, this API relies on screen capturing Stickempires and abstracting away
those details of the game so bot makers can focus on higher-level details.

Since an installer is not included, I will write out dependencies I needed (you may prefer
others depending on your computer specs):
    openCV/cv2 (image recognition)
    ffmpeg (playing videos)
    pyautogui (screen capture)