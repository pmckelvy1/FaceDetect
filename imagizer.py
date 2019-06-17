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

from cy.processor import apply_colored_faces

VALID_EXT = ['jpg', 'jpeg', 'png']

COLORMAP_AUTUMN = {'name': 'COLORMAP_AUTUMN', 'value': 0}
COLORMAP_BONE = {'name': 'COLORMAP_BONE', 'value': 1}
COLORMAP_CIVIDIS = {'name': 'COLORMAP_CIVIDIS', 'value': 17}
COLORMAP_COOL = {'name': 'COLORMAP_COOL', 'value': 8}
COLORMAP_HOT = {'name': 'COLORMAP_HOT', 'value': 11}
COLORMAP_HSV = {'name': 'COLORMAP_HSV', 'value': 9}
COLORMAP_INFERNO = {'name': 'COLORMAP_INFERNO', 'value': 14}
COLORMAP_JET = {'name': 'COLORMAP_JET', 'value': 2}
COLORMAP_MAGMA = {'name': 'COLORMAP_MAGMA', 'value': 13}
COLORMAP_OCEAN = {'name': 'COLORMAP_OCEAN', 'value': 5}
COLORMAP_PARULA = {'name': 'COLORMAP_PARULA', 'value': 12}
COLORMAP_PINK = {'name': 'COLORMAP_PINK', 'value': 10}
COLORMAP_PLASMA = {'name': 'COLORMAP_PLASMA', 'value': 15}
COLORMAP_RAINBOW = {'name': 'COLORMAP_RAINBOW', 'value': 4}
COLORMAP_SPRING = {'name': 'COLORMAP_SPRING', 'value': 7}
COLORMAP_SUMMER = {'name': 'COLORMAP_SUMMER', 'value': 6}
COLORMAP_TWILIGHT = {'name': 'COLORMAP_TWILIGHT', 'value': 18}

COLOR_MAP_TYPES = [
    COLORMAP_AUTUMN,
    COLORMAP_BONE,
    COLORMAP_CIVIDIS,
    COLORMAP_COOL,
    COLORMAP_HOT,
    COLORMAP_HSV,
    COLORMAP_INFERNO,
    COLORMAP_JET,
    COLORMAP_MAGMA,
    COLORMAP_OCEAN,
    COLORMAP_PARULA,
    COLORMAP_PINK,
    COLORMAP_PLASMA,
    COLORMAP_RAINBOW,
    COLORMAP_SPRING,
    COLORMAP_SUMMER,
    COLORMAP_TWILIGHT
]


class Imagizer():
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

    def melt(self, image, faces, file_name, out_path):
        # clean out dir
        self.clear_dir(out_path)

        melter_factory = MelterFactory(image, file_name, out_path)
        for face in faces:
            melter_factory.create_melter(face)

        # melter_factory.full_melt()
        melter_factory.colorize(100)
        # melter_factory.full_static()

    def generate_face_flash(self, image, faces, file_name, out_path):
        self.clear_dir(out_path)

        self.print_image(out_path, '%s_face_flash_%s' % (str(0), file_name), image)
        colored_image = image
        colored_image = cv2.applyColorMap(colored_image, COLORMAP_RAINBOW['value'])
        colored_image = np.array(colored_image)
        colored_faces_image = self.apply_colored_faces(image, colored_image, faces)
        colored_faces_image = np.array(colored_faces_image)
        self.print_image(out_path, '%s_face_flash_%s' % (str(1), file_name), colored_faces_image)

        for i in range(2, 100):
            copy_from = '%s_face_flash_%s' % (str(i - 2), file_name)
            copy_to = '%s_face_flash_%s' % (str(i), file_name)
            self.copy_image(out_path, copy_from, copy_to)

        self.create_gif(out_path, './testgif.gif', 2, 100, 100, 0)

    def tester(self):
        file_name = 'abba.png'
        # file_name = 'Final_414_1.jpg'
        out_path = './res/'
        in_path = './pics/'

        compd_file_name = self.compress_image(in_path, file_name)
        image, faces = self.detect_faces('./compressed/', compd_file_name)
        self.generate_face_flash(image, faces, compd_file_name, out_path)
        # self.melt(image, faces, compd_file_name, out_path)
        # self.create_gif(out_path, './testgif.gif', 2, 100, 100, 0)
        # self.create_colormap_samples(image, file_name)

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

    def create_colormap_samples(self, image, file_name):
        for cmt in COLOR_MAP_TYPES:
            image = cv2.applyColorMap(image, cmt['value'])
            self.print_image('./colormap_samples/', cmt['name'] + '_' + file_name, image)

    @staticmethod
    def clear_dir(dirname):
        shutil.rmtree(dirname)
        if not os.path.exists(dirname):
            os.mkdir(dirname)


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
    def print_image(out_path, out_file_name, img):
        cv2.imwrite(out_path + out_file_name, img)


    @staticmethod
    def copy_image(out_path, copy_from, copy_to):
        shutil.copyfile(out_path + copy_from, out_path + copy_to)

    @staticmethod
    def apply_colored_faces(image, colored_image, faces):
        mixed_image = image
        for face in faces:
            mixed_image = apply_colored_faces(image, colored_image, face[0], face[1], face[2], face[3])
        return mixed_image

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

if __name__ == '__main__':
    imgz = Imagizer()
    imgz.tester()