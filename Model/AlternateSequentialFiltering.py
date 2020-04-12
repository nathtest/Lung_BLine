import cv2 as cv
import numpy as np


class ASF:
    """
    This class implement the alternate sequential filtering.
    """

    def __init__(self, img):
        self.img = img
        self.kernel = np.ones((5, 5), np.uint8)
        self.scroll = 10  # 10 pixel scrolling

    def opening(self, img):
        """
        This function combine erode and dilatation operation to perform a morphology opening on img.
        """
        return cv.morphologyEx(img, cv.MORPH_OPEN, self.kernel)

    def closing(self, img):
        """
        This function combine erode and dilatation operation to perform a morphology closing on img.
        """
        return cv.morphologyEx(img, cv.MORPH_CLOSE, self.kernel)

    def get_ASF(self):
        """
        Implement the alternate sequential filtering by iterating vertically trough the image to elongate the Bline.
        """

        # we scroll verticaly the image to iterate through the elongated lines
        for i in range(0, self.img.shape[0], self.scroll):
            self.img[:, i:i + self.scroll] = self.opening(self.img[:, i:i + self.scroll])
            self.img[:, i:i + self.scroll] = self.closing(self.img[:, i:i + self.scroll])

        return self.img
