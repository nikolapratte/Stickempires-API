from collections import Counter
import cv2


class CounterLE(Counter):
    """Counter subclass that adds a less than or equal to function similar to how sets work (subset)."""
    def __le__(self, other):
        for key, amt in self.items():
            if key not in other or amt > other[key]:
                return False

        return True


def process_img(image):
    """Processes a normal image into an edges image."""
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1 = 100, threshold2 = 200)
    return processed_img