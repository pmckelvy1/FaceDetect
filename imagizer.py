import cv2
import sys
import os
import numpy as np
from imutils import paths
import shutil
from PIL import Image
import math
from multiprocessing import Process
from melter import MelterFactory, Melter

import pyximport; pyximport.install()

from cy.processor import threshold_fast, copy_vertical

VALID_EXT = ['jpg', 'jpeg', 'png']


class Imagizer:
    def __init__(self):
        pass

    def detect(self, filename, dirname, res_dirname):
        # Get user supplied values
        imgpath = dirname + filename
        imagePath = imgpath
        cascPath = "haarcascade_frontalface_default.xml"

        # Create the haar cascade
        faceCascade = cv2.CascadeClassifier(cascPath)

        # Read the image
        image = cv2.imread(imagePath)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags = cv2.CV_HAAR_SCALE_IMAGE
        )

        print("Found {0} faces!".format(len(faces)))

        melter_factory = MelterFactory(image, filename, res_dirname)

        shutil.rmtree(res_dirname)
        if not os.path.exists(res_dirname):
            os.mkdir(res_dirname)

        for face in faces:
            melter_factory.create_melter(face)

        melter_factory.full_melt()

    def compress_image(self, filepath, filename, qual=75, resize=True):
        foo = Image.open(filepath + filename)
        new_filename = 'comp_' + str(qual) + filename
        foo.thumbnail((foo.size[0] / 2, foo.size[1] / 2), Image.ANTIALIAS)
        foo.save('./compressed/' + new_filename, optimize=True, quality=qual)
        return new_filename

    def show_image(self, image):
        while (1):
            cv2.imshow('img', image)
            k = cv2.waitKey(33)
            if k == 27:  # Esc key to stop
                break
            elif k == -1:  # normally -1 returned,so don't print it
                continue
            else:
                print(k)  # else print its value

    def full_loop(self):
        print(os.curdir)
        for filename in os.listdir(os.curdir + '/pics'):
            try:
                if filename.split('.')[1] in VALID_EXT:
                    print(filename)
                    self.detect(filename, './pics/', './res/')
            except Exception as e:
                print(e)
                continue

    def create_gif(self, inputPath, outputPath, delay, first_delay, final_delay, loop):
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

    def tester(self):
        filename = 'abba.png'
        # filename = 'Final_414_1.jpg'
        res_dirname = './res/'
        dirname = './pics/'
        # compress_image(dirname, filename)
        compd_filename = self.compress_image(dirname, filename)
        self.detect(compd_filename, './compressed/', res_dirname)
        self.create_gif(res_dirname, './testgif.gif', 2, 50, 50, 0)


if __name__ == '__main__':
    imgz = Imagizer()
    imgz.tester()