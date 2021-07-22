import numpy as np
import cv2 as cv
import math
import scipy.ndimage
import data_singleton


class Rect():
    def __init__(self, x, y, width, height):
        self.start = Point(x, y)
        self.end = Point(x + width, y + height)
        self.width = width
        self.height = height

    def getStart(self):
        return self.start.x, self.start.y

    def getEnd(self):
        return self.end.x, self.end.y


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


def removeDamage(img):
    fudgefactor = 1.3
    sigma = 21
    kernel = 2 * math.ceil(2 * sigma) + 1

    gray_image = img / 255.0
    blur = cv.GaussianBlur(gray_image, (kernel, kernel), sigma)
    gray_image = cv.subtract(gray_image, blur)

    sobelx = cv.Sobel(gray_image, cv.CV_64F, 1, 0, ksize=1)
    sobely = cv.Sobel(gray_image, cv.CV_64F, 0, 1, ksize=1)
    mag = np.hypot(sobelx, sobely)
    ang = np.arctan2(sobely, sobelx)

    threshold = 4 * fudgefactor * np.mean(mag)
    mag[mag < threshold] = 0

    kc = data_singleton.instance.closing_value

    mag = cv.normalize(mag, 0, 255, cv.NORM_MINMAX)
    kernel = np.ones((kc, kc), np.uint8)  # this
    result = cv.morphologyEx(mag, cv.MORPH_CLOSE, kernel)

    kd = data_singleton.instance.dilation_value

    mask = cv.normalize(src=result, dst=None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8UC1)
    kerneldi = np.ones((kd, kd), np.uint8)  # this
    dilation = cv.dilate(mask, kerneldi, iterations=3)  # this
    dst = cv.inpaint(img, dilation, 3, cv.INPAINT_NS)

    return dst


def inpaintDamage(img, rect):
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv.rectangle(mask, rect.getStart(), rect.getEnd(), 255, -1)
    kerneldi = np.ones((3, 3), np.uint8)  # this
    dilation = cv.dilate(mask, kerneldi, iterations=1)  # this
    dst = cv.inpaint(img, dilation, 3, cv.INPAINT_NS)

    return dst[rect.start.y: rect.end.y, rect.start.x: rect.end.x]


def colorize(img):
    net = cv.dnn.readNetFromCaffe("model/colorization_deploy_v2.prototxt", "model/colorization_release_v2.caffemodel")
    pts = np.load("model/pts_in_hull.npy")

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

    image = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
    scaled = image.astype("float32") / 255.0
    lab = cv.cvtColor(scaled, cv.COLOR_RGB2LAB)
    resized = cv.resize(lab, (224, 224))
    L = cv.split(resized)[0]
    L -= 50

    net.setInput(cv.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv.resize(ab, (image.shape[1], image.shape[0]))

    L = cv.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv.cvtColor(colorized, cv.COLOR_LAB2RGB)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    return colorized


def blurDamage(img):
    kb = data_singleton.instance.blur_value
    kernel = (kb, kb)  # this
    blured = cv.blur(img, kernel)  # this

    return blured