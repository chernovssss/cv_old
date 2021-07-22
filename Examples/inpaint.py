"""
Implementation of texture based inpainting from Criminisi et al 2004

This script requires that 'opencv' and 'numpy' are installed within the
environment you are running the script in.

"""

import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt
from numba import jit

np.set_printoptions(threshold=0.2)

# The patch size should be a square of equivalent size to the smallest
# distinguishable texture element (texel).
# It must be an odd number
PATCH_SIZE = 9


def remove_mask(img, mask):
    for x in range(img.shape[1]):
        for y in range(img.shape[0]):
            if mask[y, x] == 255:
                img[y, x] = (0, 0, 0)


def mask_as_None(img, mask):
    img[mask == 255] = np.nan


def is_omega_empty(mask):
    """
    Returns 1 if there are no pixel left to be inpainted
    """
    return not np.isin(255, mask)


def calculate_fill_front(mask):
    """
    Calculate fill front, i.e the border of the area to be inpainted
    """
    fill_front = []
    for x in range(mask.shape[1]):
        for y in range(mask.shape[0]):
            if mask[y, x] == 255 and np.isin(0, mask[y - 1:y + 2, x - 1:x + 2]):
                fill_front.append((y, x))
    return fill_front


def calculate_priority(point, img_gray, mask, c):
    """
        Calculate the priority of a given patch given it's central point
    """
    a = calculate_c(point, mask, c)
    b = calculate_d(point, img_gray, mask)
    # print("Point:",point,"C:",a,"D:",b)

    return a * b
    # return calculate_c(point, mask, c)*calculate_d(point, img_gray, mask)


@jit(nopython=True)
def calculate_c(point, mask, c):
    """
        Calculate the confidence value of a given patch givent it's central point
    """
    delta = PATCH_SIZE // 2
    confidences_sum = 0

    for y in range(point[0] - delta, point[0] + delta + 1):
        for x in range(point[1] - delta, point[1] + delta + 1):
            if mask[y, x] == 0:
                confidences_sum += c[y, x]
    c[point] = confidences_sum / (PATCH_SIZE ** 2)
    return c[point]


@jit
def calculate_d(point, img_gray, mask):
    """
        Calculate the 'data' at a given point, using alpha as a regularization
        factor.
        Here we will use Scharr kernel to evaluate the derivative at a given
        point
    """

    kernel_x = np.array([[-3, 0, 3],
                         [-10, 0, 10],
                         [-3, 0, 3]])
    kernel_y = np.array([[-3, -10, -3],
                         [0, 0, 0],
                         [3, 10, 3]])

    alpha = 1

    # for gradient :
    # np.gradient

    # print("=======================================================")
    gray_patch = img_gray[point[0] - 1:point[0] + 2, point[1] - 1:point[1] + 2]
    # isophote_x = np.sum(np.multiply(gray_patch, kernel_x))
    # isophote_y = np.sum(np.multiply(gray_patch, kernel_y))
    # isophote = np.array([isophote_x, isophote_y])
    isophote = np.nan_to_num(np.array(np.gradient(gray_patch)))
    isophote = np.array([np.max(isophote[0]), np.max(isophote[1])])

    normal_x = np.sum(np.multiply(mask[point[0] - 1:point[0] + 2, point[1] - 1:point[1] + 2], kernel_x))
    normal_y = np.sum(np.multiply(mask[point[0] - 1:point[0] + 2, point[1] - 1:point[1] + 2], kernel_y))
    normal = np.array([normal_x, normal_y])
    normal = normal / np.linalg.norm(normal)
    # if np.count_nonzero(isophote) > 0  :
    #   print("isophote :",isophote)
    #  print("patch:",gray_patch)
    # print("normal:",normal)
    return abs(np.dot(isophote, normal)) / alpha + 0.001


def most_similar_patch(point, img, mask):
    """
        Find the point with the most similar patch to our patch with the
        biggest priority
    """

    delta = PATCH_SIZE // 2
    q = (0, 0)
    min_patch_difference = float("inf")
    for q_x in range(delta + 1, img.shape[1] - delta):
        for q_y in range(delta + 1, img.shape[0] - delta):
            if not np.isin(255, mask[q_y - delta:q_y + delta + 1, q_x - delta:q_x + delta + 1]):
                difference = calculate_difference(point, (q_y, q_x), img, mask)
                if difference < min_patch_difference:
                    min_patch_difference = difference
                    q = (q_y, q_x)
    return q, min_patch_difference


@jit
def calculate_difference(p, q, img, mask):
    """
        Calculate the sum of squared differences between two patches using
        their center point
    """
    delta = PATCH_SIZE // 2
    rgb_mask = 1 - mask[p[0] - delta:p[0] + delta + 1, p[1] - delta:p[1] + delta + 1] / 255
    rgb_mask = np.repeat(rgb_mask[..., None], 3, axis=2)
    difference = img[p[0] - delta:p[0] + delta + 1, p[1] - delta:p[1] + delta + 1] - img[q[0] - delta:q[0] + delta + 1,
                                                                                     q[1] - delta:q[1] + delta + 1]
    square_difference = np.square(np.multiply(difference, rgb_mask))
    sum_squared_diff = np.sum(square_difference)

    return sum_squared_diff


def copy_data(p, q, img, mask):
    """
        Copy data from donor patch q to our patch p of max priority

    """
    delta = PATCH_SIZE // 2

    for d_y in range(-delta, delta + 1):
        for d_x in range(-delta, delta + 1):
            if mask[p[0] - d_y, p[1] - d_x] == 255:
                img[p[0] - d_y, p[1] - d_x] = img[q[0] - d_y, q[1] - d_x]


def update_c_mask(p, mask, c):
    """
    Update confidence values and our mask
    """
    delta = PATCH_SIZE // 2

    for d_y in range(-delta, delta + 1):
        for d_x in range(-delta, delta + 1):
            if mask[p[0] - d_y, p[1] - d_x] == 255:
                c[p[0] - d_y, p[1] - d_x] = c[p]
                mask[p[0] - d_y, p[1] - d_x] = 0


def color_points(image, points):
    """
        Color points in red in rgb image
    """
    for point in points:
        image[point] = (0, 0, 255)


def main():
    """
    Main function that will do the inpainting
    """


    # Preprocessing, creating the necessary data for our algorithm
    img = cv2.imread(r'C:\Users\Andrey\PycharmProjects\cv_old\Examples\photo.jpg')
    if img is None:
        sys.exit("Image not found")

    mask = cv2.imread(r'C:\Users\Andrey\PycharmProjects\cv_old\Examples\maskphoto.jpg', 0)
    if mask is None:
        sys.exit("Mask not found")

    print(img.shape[:2], mask.shape[:2])
    if img.shape[:2] != mask.shape[:2]:
        sys.exit("Image and mask are of different size")

    mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
    remove_mask(img, mask)

    # c will be our confidence array C(p)
    c = 1 - np.float64(mask)
    p = np.zeros(c.shape)

    i = 0
    # Main loop
    while not is_omega_empty(mask):
        img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        img_gray = np.array(cv2.cvtColor(img,
                                         cv2.COLOR_BGR2GRAY), dtype=np.float64)
        mask_as_None(img_gray, mask)
        fill_front = calculate_fill_front(mask)
        point_max_priority = (0, 0)
        max_priority = 0
        for point in fill_front:
            p[point] = calculate_priority(point, img_gray, mask, c)

            # finding arg max(priority)
            if p[point] > max_priority:
                max_priority = p[point]
                point_max_priority = point
        q, diff = most_similar_patch(point_max_priority, img_lab, mask)
        print("Step:", i, "Point of max prio :", point_max_priority, "Most similar patch found in :", q,
              " with a difference of :", diff)
        # print("Most similar patch :\n", img[q[0]-4:q[0]+5,q[1]-4:q[1]+5])
        # print("Our patch to fill :\n",
        #         img[point_max_priority[0]-4:point_max_priority[0]+5,point_max_priority[1]-4:point_max_priority[1]+5])
        # print("=================================================")
        copy_data(point_max_priority, q, img, mask)
        # plt.imshow(c*255, cmap="gray")
        # plt.show()

        update_c_mask(point_max_priority, mask, c)
        cv2.imwrite("results/img-{}.png".format(i), img)
        cv2.imwrite("results/gray-{}.png".format(i), img_gray)
        # cv2.imwrite("results/c-{}.png".format(i), c*255)
        # cv2.imwrite("results/p-{}.png".format(i), p*255/np.max(p))

        i += 1
    cv2.imwrite("result.png", img)


if __name__ == "__main__":
    main()
