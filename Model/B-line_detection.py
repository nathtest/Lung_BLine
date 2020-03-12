from Model import DICOM_Reader
import numpy as np
from scipy import ndimage
from scipy.signal import hilbert
import cv2


class BLine_detect():

    def axial_gradient_image(self, img):
        # noyau en x
        kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        # noyau en y
        ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        # test
        ktest = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        # Calcul du gradient en x
        x = ndimage.convolve(img, kx)
        # Calcul du gradient en y
        y = ndimage.convolve(img, ky)

        k = ndimage.convolve(img, ktest)

        laplacian = cv2.Laplacian(img, cv2.CV_64F, ksize=1)
        sobelx = cv2.Sobel(img, cv2.CV_8U, 1, 0, ksize=3)
        sobely = cv2.Sobel(img, cv2.CV_8U, 0, 1, ksize=5)

        kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
        edges_x = cv2.filter2D(img, cv2.CV_8U, kernelx)
        edges_y = cv2.filter2D(img, cv2.CV_8U, kernely)

        # return np.uint8(np.absolute(sobelx)), y
        return edges_x, y

    def hilbert_transform(self, gradient_axial):
        hilbert_signal = hilbert(gradient_axial)

        return hilbert_signal

    def log_transform(self, hilbert_signal):
        Absolute_signal = np.absolute(hilbert_signal)
        Log_transform = np.log(Absolute_signal)

        return Log_transform

    def binary_mask(self, img, log_transform):
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
