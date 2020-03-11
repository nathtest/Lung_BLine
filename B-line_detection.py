import DICOM_Reader
import numpy as np
from scipy import ndimage
from scipy.signal import hilbert
import cv2
import scipy.misc



def detect_Bline(img):
    # Enhance image
    img = cv2.fastNlMeansDenoising(img,None,10,7,21)

    cv2.imshow('image', img)
    cv2.waitKey(0)

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

    k = ndimage.convolve(img,ktest)

    laplacian = cv2.Laplacian(img, cv2.CV_64F,ksize=1)
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)

    return np.uint8(np.absolute(sobelx)), y


def hilbert_transform(gradient_axial):
    hilbert_signal = hilbert(gradient_axial)

    return hilbert_signal


def log_transform(hilbert_signal):
    Absolute_signal = np.absolute(hilbert_signal)
    Log_transform = np.log(Absolute_signal)

    return Log_transform


def binary_mask(img, log_transform):
    img_original = np.array(img,dtype='d')
    mask = np.array(log_transform,dtype='d')
    result = cv2.bitwise_and(src1=img_original, src2=mask)

    return result


if __name__ == "__main__":
    reader = DICOM_Reader.DICOMReader('2019010A', True)
    reader.get_dicom_details()
    array_image = reader.extract_images_opencv_dev(False)

    axial_gradient, _ = detect_Bline(array_image[192])

    # cv2.imshow('image', axial_gradient)
    # cv2.waitKey(0)

    hilbert_signal = hilbert_transform(axial_gradient)

    # cv2.imshow('image', hilbert_signal)
    # cv2.waitKey(0)

    transform = log_transform(hilbert_signal)

    cv2.imshow('image', transform)
    cv2.waitKey(0)

    print(array_image[192].shape)
    print(transform.shape)

    result = binary_mask(array_image[192],transform)

    cv2.imshow('image', result)
    cv2.waitKey(0)
