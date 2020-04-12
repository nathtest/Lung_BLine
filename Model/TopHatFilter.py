import cv2 as cv
import numpy as np


class TopHatFilter:
    """
    This class implement the top hat filter.
    """

    def __init__(self, img):
        self.img = img
        self.kernel = np.ones((5, 5), np.uint8)

    def get_top_hat(self):
        return cv.morphologyEx(self.img, cv.MORPH_TOPHAT, self.kernel)
