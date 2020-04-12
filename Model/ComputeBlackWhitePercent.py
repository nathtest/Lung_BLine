import numpy as np
import qimage2ndarray
from PyQt5.QtGui import QImage


class ComputeBlackWhitePercent:
    """
    This class is used to calculate the ratio between black and white pixel of the image.
    """

    def __init__(self, img):
        self.img = img
        self.threshold = 40

    def getRatio(self):
        image = self.img.toImage().convertToFormat(QImage.Format_Grayscale8)

        arr = qimage2ndarray.byte_view(image)

        n_white_pix = np.sum(arr >= self.threshold)

        total_pixel = arr.shape[0] * arr.shape[1]

        return (n_white_pix / total_pixel) *100
