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

from cy.processor import threshold_fast, copy_vertical, melt


class MelterFactory:
    def __init__(self, image, filename, res_dirname):
        self.melters = []
        self.filename = filename
        self.res_dirname = res_dirname
        self.step = 0
        self.image = image
        self.melter_id = 0

    def create_melter(self, face):
        self.melter_id += 1
        m = Melter(face, str(self.melter_id))
        self.melters.append(m)

    def full_melt(self):
        print('FULL MELT...')
        print(self.melters)
        while len(self.melters) > 0:
            self.melt_step()
            self.melters = [m for m in self.melters if m.is_active]

    def melt_step(self):
        self.step += 1
        melted_image = self.image
        for melter in self.melters:
            melted_image = melter.melt(self.image)
        cv2.imwrite(self.res_dirname + '%s:glitch_%s' % (self.step + 1000000, self.filename), melted_image)


class Melter:
    def __init__(self, face, id):
        self.id = id
        self.min_delta = 3
        print('creating melter: %s' % face)
        self.x = face[0]
        self.y = face[1]
        self.w = face[2]
        self.h = face[3]
        self.cur_y = self.y
        self.delta = self.min_delta
        self.idelta = self.min_delta
        self.is_active = True

    def melt(self, image):
        if self.is_active:
            img = image
            # for j in range(self.cur_y, self.cur_y + self.h, self.delta):
            img = melt(img, self.x, self.y, self.w, self.h, self.delta, self.cur_y)
            img = np.array(img)
            self.increment()
            return img
        return image

    def increment(self):
        # self.idelta += 1
        # if self.idelta > self.delta:
        #     self.idelta = self.min_delta
        #     self.delta += 1
        self.cur_y += self.delta
        if self.cur_y > self.h:
            self.cur_y = self.y
            self.delta += 1
            print('%s | delta: %s , y: %s' % (self.id, self.delta, self.cur_y))
        if self.delta > self.h:
            self.delta = self.min_delta
            self.is_active = False
            print('delta: %s , idelta: %s' % (self.delta, self.idelta))