import cv2


def process_img(image):
    """Processes a normal image into an edges image."""
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1 = 100, threshold2 = 200)
    return processed_img