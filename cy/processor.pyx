import numpy as np
import random

cpdef unsigned char[:, :, :] threshold_fast(int T, unsigned char[:, :, :] image):
    # set the variable extension types
    cdef int x, y, w, h

    # grab the image dimensions
    h = image.shape[0]
    w = image.shape[1]

    # loop over the image
    for y in range(0, h):
        for x in range(0, w):
            # threshold the pixel
            image[y, x, 0] = 255 if image[y, x, 0] >= T else 0

    # return the thresholded image
    return image


cpdef unsigned char[:, :, :] copy_image(unsigned char[:, :, :] image):
    return np.copy(image)

cpdef unsigned char[:, :, :] copy_vertical(unsigned char[:, :, :] image, int x, int y, int w, int h, int delta, int idelta):
    # set the variable extension types
    cdef int i, j, k, img_w, img_h

    # grab the image dimensions
    img_h = image.shape[0]
    img_w = image.shape[1]

    # loop over the image
    # for k in range(y, y + h, delta):
    #     for j in range(k, k + delta):
    #         if j > y + h:
    #             break
    #         for i in range(x, x + w):
    #             # copy the pixel
    #             image[j, i] = image[j - delta, i]

    for j in range(y, h, delta):
        # stay w/in the detected range
        if j + idelta > y + h:
            break
        for i in range(x, x + w):
            image[j + idelta, i] = image[j, i]

    # return the thresholded image
    return image

cpdef unsigned char[:, :, :] melt(unsigned char[:, :, :] image, int x, int y, int w, int h, int delta, int starty):
    # set the variable extension types
    cdef int i, j, k, img_w, img_h

    # grab the image dimensions
    img_h = image.shape[0]
    img_w = image.shape[1]

    for d in range(starty, starty + delta):
        if d > y + h:
            break
        for i in range(x, x + w):
            image[d, i] = image[starty, i]

    # return the thresholded image
    return image

cpdef unsigned char[:, :, :] colorize(unsigned char[:, :, :] image, int x, int y, int w, int h, unsigned char color):
    # set the variable extension types
    cdef int i, j, k, img_w, img_h

    # grab the image dimensions
    img_h = image.shape[0]
    img_w = image.shape[1]

    for i in range(y, y + h):
        for j in range(x, x + w):
            image[i, j] = color

    # return the thresholded image
    return image

cpdef unsigned char[:, :, :] static(unsigned char[:, :, :] image, int x, int y, int w, int h, int n, int coarse):
    # set the variable extension types
    cdef int i, j, k, x1, x2, y1, y2, img_w, img_h

    # grab the image dimensions
    img_h = image.shape[0]
    img_w = image.shape[1]

    for i in range(n):
        x1 = random.randrange(x, x + w)
        x2 = random.randrange(x, x + w)
        y1 = random.randrange(y, y + h)
        y2 = random.randrange(y, y + h)
        for j in range(coarse):
            if y1 + j >= y + h or y2 + j >= y + h:
                break
            for k in range(coarse):
                if x1 + k >= x + w or x2 + k >= x + w:
                    break
                image[y1 + j, x1 + k] = image[y2 + j, x2 + k]

    # return the thresholded image
    return image

cpdef unsigned char[:, :, :] apply_colored_faces(unsigned char[:, :, :] image, unsigned char[:, :, :] cimage, int x, int y, int w, int h):
    # set the variable extension types
    cdef int i, j, k, x1, x2, y1, y2, img_w, img_h

    for i in range(y, y + h):
        for j in range(x, x + w):
            image[i, j] = cimage[i, j]

    return image