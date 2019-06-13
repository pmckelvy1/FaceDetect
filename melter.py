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

from cy.processor import threshold_fast, copy_vertical, melt, copy_image, colorize, static


class MelterFactory:
    def __init__(self, image, filename, res_dirname):
        self.all_melters = []
        self.active_melters = []
        self.filename = filename
        self.res_dirname = res_dirname
        self.step = 1000000
        self.image = image
        self.melter_id = 0
        self.print_image(self.image)

    def create_melter(self, face):
        self.melter_id += 1
        m = Melter(face, str(self.melter_id))
        self.all_melters.append(m)
        self.active_melters.append(m)

    def print_image(self, img):
        cv2.imwrite(self.res_dirname + '%s:glitch_%s' % (self.step, self.filename), img)

    def full_melt(self):
        print('FULL MELT...')
        print(self.active_melters)
        while len(self.active_melters) > 0:
            self.melt_step()
            self.active_melters = [m for m in self.active_melters if m.is_active]
        self.colorize(0)
        # self.colorize(128)

    def melt_step(self):
        self.step += 1
        melted_image = self.image
        for melter in self.active_melters:
            melted_image = melter.melt(self.image)
        self.print_image(melted_image)

    def colorize(self, color):
        self.step += 1
        for melter in self.all_melters:
            self.image = melter.colorize(self.image, color=color)
        self.print_image(self.image)

    def full_static(self):
        for i in range(200):
            self.step += 1
            for melter in self.all_melters:
                self.image = melter.static(self.image)
            self.print_image(self.image)


class Melter:
    def __init__(self, face, id):
        self.id = id
        print('creating melter: %s' % face)
        self.x = face[0]
        self.y = face[1]
        self.w = face[2]
        self.h = face[3]
        self.is_active = True

        # melt
        self.cur_y = self.y
        self.min_delta = 1
        self.delta = self.min_delta
        self.idelta = self.min_delta

        # static
        self.num_swaps = 1
        self.coarse = 30

    def colorize(self, image, color=0):
        colorize_image = colorize(image, self.x, self.y, self.w, self.h, color)
        return np.array(colorize_image)

    def melt(self, image):
        if self.is_active:
            img = image
            # for j in range(self.cur_y, self.cur_y + self.h, self.delta):
            img = melt(img, self.x, self.y, self.w, self.h, self.delta, self.cur_y)
            img = np.array(img)
            self.increment()
            return img
        return image

    def static(self, image):
        if self.is_active:
            img = image
            img = static(img, self.x, self.y, self.w, self.h, self.num_swaps, self.coarse)
            # self.coarse -= 1
            img = np.array(img)
            return img
        return image

    def increment(self):
        # self.idelta += 1
        # if self.idelta > self.delta:
        #     self.idelta = self.min_delta
        #     self.delta += 1
        self.cur_y += self.delta
        if self.cur_y > self.y + self.h:
            self.cur_y = self.y
            self.delta += 1
            print('%s | delta: %s , y: %s' % (self.id, self.delta, self.cur_y))
        if self.delta > self.h:
            self.delta = self.min_delta
            self.is_active = False
            print('delta: %s , idelta: %s' % (self.delta, self.idelta))
        if self.delta == 0:
            self.delta = self.min_delta
            self.is_active = False
            print('delta: %s , idelta: %s' % (self.delta, self.idelta))