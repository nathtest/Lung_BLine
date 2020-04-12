from Model.BLineDetection import BLineDetect
from Model.AlternateSequentialFiltering import ASF
from Model.TopHatFilter import TopHatFilter


class RunAlgorithms:
    """
    This class is used to run BLine detection algorithms.
    """

    def runBlineDetection(self, img):
        """
        This function takes the selected image from the user and run the bline detection algorithm.
        It return the bline detected.
        """
        bline_detect = BLineDetect(img)
        binary_mask = bline_detect.get_binary_mask()
        asf = ASF(binary_mask)
        top_hat_filter = TopHatFilter(asf)

        return top_hat_filter

    def runAnotherBlineDetection(self, img):
        pass

    def runAnotherAnotherBlineDetection(self, img):
        pass
