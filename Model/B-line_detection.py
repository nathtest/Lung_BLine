from Model import DICOM_Reader
import numpy as np
from scipy import ndimage
from scipy.signal import hilbert
import cv2


class BLine_detect():
    """
    This class takes an array of images from a DICOM file and apply different transforms to extract B-line forms
    into a mask.
    The order is :
    1) axial_gradient_image
    2) hilbert_transform
    3) log_transform
    4) binary_mask

    To use this class, the get_binary_mask() funct must be used.
    """

    def __init__(self,img=None):
        self.img = img


    def axial_gradient_image(self, img):
        """
        Extract the axial gradient of img to only keep the elongated lines.
        :param img:
        :return:
        """

        # TODO remove useless code line
        # noyau en x
        # kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        # noyau en y
        # ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        # test
        # ktest = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        # Calcul du gradient en x
        # x = ndimage.convolve(img, kx)
        # Calcul du gradient en y
        # y = ndimage.convolve(img, ky)
        #
        # k = ndimage.convolve(img, ktest)
        #
        # laplacian = cv2.Laplacian(img, cv2.CV_64F, ksize=1)
        # sobelx = cv2.Sobel(img, cv2.CV_8U, 1, 0, ksize=3)
        # sobely = cv2.Sobel(img, cv2.CV_8U, 0, 1, ksize=5)

        kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
        edges_x = cv2.filter2D(img, cv2.CV_8U, kernelx)
        edges_y = cv2.filter2D(img, cv2.CV_8U, kernely)

        # return np.uint8(np.absolute(sobelx)), y
        return edges_x, edges_y

    def hilbert_transform(self, gradient_axial):
        """
        Compute the hilbert transform of the axial gradient of the image.
        :param gradient_axial:
        :return:
        """
        hilbert_signal = hilbert(gradient_axial)

        return hilbert_signal

    def log_transform(self, hilbert_signal):
        """
        Apply a logorithm transform of the absolute date.
        :param hilbert_signal:
        :return:
        """
        Absolute_signal = np.absolute(hilbert_signal)
        Log_transform = np.log(Absolute_signal)

        return Log_transform

    def binary_mask(self, img, log_transform):
        """
        Return a mask between the log_transform and the original image.
        :param img:
        :param log_transform:
        :return:
        """
        img_original = np.array(img, dtype='d')
        mask = np.array(log_transform, dtype='d')
        result = cv2.bitwise_and(src1=img_original, src2=mask)

        return result

    def fast_denoising(self, img):
        # Enhance image
        img = cv2.fastNlMeansDenoising(img, dst=None, h=4, templateWindowSize=7, searchWindowSize=21)

        cv2.imshow('image', img)
        cv2.waitKey(0)

        return img

    def multi_denoising(self, img):
        # Enhance image
        img = cv2.fastNlMeansDenoisingMulti(img, imgToDenoiseIndex=2, temporalWindowSize=5, dst=None, h=1,
                                            templateWindowSize=7, searchWindowSize=21)

        cv2.imshow('image', img)
        cv2.waitKey(0)

        return img

    def get_binary_mask(self):
        """
        Apply all transforms to the original image and return binary mask.
        :return:
        """
        if self.img is not None:
            axial_gradient, _ = self.axial_gradient_image(img)

            hilbert_signal = self.hilbert_transform(axial_gradient)

            transform = self.log_transform(hilbert_signal)

            result = self.binary_mask(self.img, transform)

            return result
        else:
            return None


if __name__ == "__main__":
    reader = DICOM_Reader.DICOMReader(r'C:\Users\21506969t\PycharmProjects\Lung_BLine\2019010A', True)
    reader.get_dicom_details()
    array_image = reader.extract_images_opencv_dev(False)

    detect = BLine_detect()

    img = detect.fast_denoising(array_image[1])

    axial_gradient, _ = detect.axial_gradient_image(img)

    cv2.imshow('image', axial_gradient)
    cv2.waitKey(0)

    hilbert_signal = detect.hilbert_transform(axial_gradient)

    # cv2.imshow('image', hilbert_signal)
    # cv2.waitKey(0)

    transform = detect.log_transform(hilbert_signal)

    cv2.imshow('image', transform)
    cv2.waitKey(0)

    # print(array_image[12].shape)
    print(transform.shape)

    result = detect.binary_mask(array_image[1], transform)

    cv2.imshow('image', result)
    cv2.waitKey(0)
