import cv2
import sys
import os
import numpy as np
from imutils import paths
import shutil
from PIL import Image
import math
from multiprocessing import Process

import pyximport; pyximport.install()

from cy.processor import threshold_fast, copy_vertical

def detect(filename, dirname, res_dirname):
    # Get user supplied values

    imgpath = dirname + filename
    imagePath = imgpath
    cascPath = "haarcascade_frontalface_default.xml"

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    # Read the image
    image = cv2.imread(imagePath)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
        #flags = cv2.CV_HAAR_SCALE_IMAGE
    )

    print("Found {0} faces!".format(len(faces)))

    shutil.rmtree(res_dirname)
    if not os.path.exists(res_dirname):
        os.mkdir(res_dirname)

    # def melt_face(face):
    #     # create worker thread from melter
    #     # each worker thread processes 1 tick for its face
    #     # then the melter prints that frame
    #     # melter melts until all workers have finished
    #     pass

    for (x, y, w, h) in faces:
        # p = Process(target=melt_face, args=(x, y, w, h))
        for delta in range(1, h):
            for idelta in range(1, delta):
                print('x: %s , y: %s , w: %s , h: %s , delta: %s , idelta: %s' % (x, y, w, h, delta, idelta))
                img = copy_vertical(image, x, y, w, h, delta, idelta)
                img = np.array(img)

                cv2.imwrite(res_dirname + '%s:glitch_%s' % (delta + 1000000, filename), img)

    # show_image(imwhole)

    # cv2.imshow("Faces found", imwhole)
    # cv2.waitKey(10000)



VALID_EXT = ['jpg', 'jpeg', 'png']

def compress_image(filepath, filename, qual=35, resize=True):
    foo = Image.open(filepath + filename)
    new_filename = 'comp_' + str(qual) + filename
    foo.thumbnail((foo.size[0] / 2, foo.size[1] / 2), Image.ANTIALIAS)
    foo.save('./compressed/' + new_filename, optimize=True, quality=qual)
    return new_filename

def show_image(image):
    while (1):
        cv2.imshow('img', image)
        k = cv2.waitKey(33)
        if k == 27:  # Esc key to stop
            break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(k)  # else print its value

# detect('abba.png')
def full_loop():
    print(os.curdir)
    for filename in os.listdir(os.curdir + '/pics'):
        try:
            if filename.split('.')[1] in VALID_EXT:
                print(filename)
                detect(filename)
        except Exception as e:
            print(e)
            continue


def create_gif(inputPath, outputPath, delay, first_delay, final_delay, loop):
    # grab all image paths in the input directory
    image_paths = sorted(list(paths.list_images(inputPath)))

    # remove the last image path in the list
    first_path = image_paths[0]
    last_path = image_paths[-1]
    image_paths = image_paths[:-1]

    # construct the image magick 'convert' command that will be used
    # generate our output GIF, giving a larger delay to the final
    # frame (if so desired)
    cmd = "convert -delay {} {} -delay {} {} -delay {} {} -loop {} {}".format(
        first_delay, first_path, delay, " ".join(image_paths), final_delay, last_path, loop,
        outputPath)
    os.system(cmd)

def tester():
    # filename = 'abba.png'
    filename = 'Final_414_1.jpg'
    # dirname = './pics/'
    # compress_image(dirname, filename)
    compd_filename = compress_image('./pics/', filename)
    res_dirname = './res/'
    detect(compd_filename, './compressed/', res_dirname)
    create_gif(res_dirname, './something.gif', 2, 500, 500, 0)

tester()