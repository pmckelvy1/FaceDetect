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

VALID_EXT = ['jpg', 'jpeg', 'png']


class Imagizer:
    def __init__(self):
        casc_path = "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(casc_path)

    def detect_faces(self, file_path, file_name):
        # Read the image
        img_path = file_path + file_name
        image = cv2.imread(img_path)

        # Detect faces in the image
        faces = self.face_cascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags = cv2.CV_HAAR_SCALE_IMAGE
        )

        print("{0} :: Found {1} faces!".format(file_name, len(faces)))

        return image, faces

    def get_num_faces(self, file_path, file_name):
        _, faces = self.detect_faces(file_path, file_name)
        return len(faces)

    @staticmethod
    def melt(image, faces, file_name, out_dir):
        # clean out dir
        shutil.rmtree(out_dir)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        melter_factory = MelterFactory(image, file_name, out_dir)
        for face in faces:
            melter_factory.create_melter(face)

        # melter_factory.full_melt()
        # melter_factory.colorize(50)
        melter_factory.full_static()

    @staticmethod
    def compress_image(file_path, file_name, qual=75, resize=True):
        foo = Image.open(file_path + file_name)
        new_file_name = 'comp_' + str(qual) + file_name
        foo.thumbnail((foo.size[0] / 2, foo.size[1] / 2), Image.ANTIALIAS)
        foo.save('./compressed/' + new_file_name, optimize=True, quality=qual)
        return new_file_name

    @staticmethod
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

    @staticmethod
    def create_gif(in_path, out_path, frame_delay, first_delay, final_delay, loop):
        # grab all image paths in the input directory
        image_paths = sorted(list(paths.list_images(in_path)))

        # remove the last image path in the list
        first_path = image_paths[0]
        last_path = image_paths[-1]
        image_paths = image_paths[:-1]

        # construct the image magick 'convert' command that will be used
        # generate our output GIF, giving a larger delay to the final
        # frame (if so desired)
        cmd = "convert -delay {} {} -delay {} {} -delay {} {} -loop {} {}".format(
            first_delay, first_path,
            frame_delay, " ".join(image_paths),
            final_delay, last_path,
            loop, out_path)
        os.system(cmd)

    def tester(self):
        file_name = 'abba.png'
        # file_name = 'Final_414_1.jpg'
        out_path = './res/'
        in_path = './pics/'

        compd_file_name = self.compress_image(in_path, file_name)
        image, faces = self.detect_faces('./compressed/', compd_file_name)
        self.melt(image, faces, compd_file_name, out_path)
        self.create_gif(out_path, './testgif.gif', 2, 100, 100, 0)

    def full_loop(self):
        print(os.curdir)
        for file_name in os.listdir(os.curdir + '/pics'):
            try:
                if file_name.split('.')[1] in VALID_EXT:
                    print(file_name)
                    image, faces = self.detect_faces('./pics/', file_name)
                    self.melt(image, faces, file_name, './res/')
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    imgz = Imagizer()
    imgz.tester()