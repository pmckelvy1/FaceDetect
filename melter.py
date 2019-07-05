import cv2
import sys
import os
import numpy as np
from imutils import paths
import shutil
from PIL import Image
import math
from multiprocessing import Process
from constants import *
from utils import copy_image, print_image, show_image

import pyximport; pyximport.install()

from cy.processor import threshold_fast, copy_vertical, melt, cy_copy_image, colorize, static, apply_colored_faces, flip, static_virus


class MeltMaster:
    def __init__(self, image, file_name, out_path, frame_rate):
        self.melt_type = 'melt'
        self.all_melters = []
        self.active_melters = []
        self.file_name = file_name
        self.out_path = out_path
        self.step = 1000000
        self.image = image
        self.melter_id = 0
        self.print_image(self.image)
        self.frame_rate = frame_rate

    def create_melter(self, face):
        self.melter_id += 1
        m = Melter(face, str(self.melter_id))
        self.all_melters.append(m)
        self.active_melters.append(m)

    def set_frame_rate(self, frame_rate):
        self.frame_rate = frame_rate

    def image_reset(self, image):
        self.image = image

    def reset_melters(self):
        print('resettting melters')
        for m in self.all_melters:
            m.reset()

    def img_name(self, num):
        return '%s:%s_%s' % (str(num), self.melt_type, self.file_name)

    def print_image(self, img):
        print_image(self.out_path, self.img_name(self.step), img)

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
        if self.step % self.frame_rate == 0:
            self.print_image(melted_image)

    def colorize(self, color):
        self.step += 1
        for melter in self.all_melters:
            self.image = melter.colorize(self.image, color=color)
        self.print_image(self.image)

    def full_static(self, target_coarse, img_override=None, full_frame=False, reverse=False):
        self.reset_melters()
        rev = 1
        self.print_image(self.image)
        if reverse:
            self.step += target_coarse
            self.print_image(self.image)
            rev = -1
        for i in range(target_coarse):
            self.step += 1 * rev
            for melter in self.all_melters:
                # show_image(self.image)
                # show_image(img_override)
                self.image = melter.static(self.image, img_virus=img_override, coarse=i, full_frame=full_frame)
            self.print_image(self.image)
        if reverse:
            self.step += target_coarse

    def full_color_face_glitch(self, img_override=None):
        img = self.image
        if img_override is not None:
            img = img_override
        self.step += 1
        self.print_image(self.image)
        colored_image = img
        colored_image = cv2.applyColorMap(colored_image, COLORMAP_RAINBOW['value'])
        colored_image = np.array(colored_image)
        colored_faces_image = self.apply_colored_faces(img, colored_image)
        colored_faces_image = np.array(colored_faces_image)
        self.step += 1
        self.print_image(colored_faces_image)

        for i in range(2, 100):
            self.step += 1
            copy_from = self.img_name(self.step - 2)
            copy_to = self.img_name(self.step)
            copy_image(self.out_path, copy_from, copy_to)

    def apply_colored_faces(self, image, colored_image):
        mixed_image = image
        for melter in self.all_melters:
            mixed_image = melter.apply_face_mask(self.image, colored_image)
        return mixed_image

    def flip(self, horizontal):
        rot_image = self.image
        for melter in self.all_melters:
            rot_image = melter.flip(rot_image, 1)
        self.print_image(rot_image)


class Melter:
    def __init__(self, face, id, coarse=30):
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
        self.coarse = coarse

    def reset(self):
        self.is_active = True

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

    def static(self, image, img_virus=None, coarse=30, num_swaps=1, full_frame=False):
        self.coarse = coarse
        if self.is_active:
            img = image
            x, y, w, h = self.x, self.y, self.w, self.h
            if full_frame:
                x, y, w, h = 0, 0, img.shape[1], img.shape[0]
            if img_virus is None:
                img = static(img, x, y, w, h, num_swaps, self.coarse, full_frame)
            else:
                img = static_virus(img, x, y, w, h, num_swaps, self.coarse, full_frame, img_virus)
            # self.coarse -= 1
            img = np.array(img)
            return img
        return image

    def increment(self):
        self.cur_y += self.delta
        if self.cur_y >= self.y + self.h:
            self.cur_y = self.y + self.delta - 1
            self.delta += 1
            # print('%s | delta: %s , cur_y: %s, cur_y + h: %s' % (self.id, self.delta, self.cur_y, self.cur_y + self.h))
        if self.delta > self.h:
            self.delta = self.min_delta
            self.is_active = False
            # print('delta: %s , idelta: %s' % (self.delta, self.idelta))
        if self.delta == 0:
            self.delta = self.min_delta
            self.is_active = False
            # print('delta: %s , idelta: %s' % (self.delta, self.idelta))

    def apply_face_mask(self, image, mask_image):
        return apply_colored_faces(image, mask_image, self.x, self.y, self.w, self.h)

    def flip(self, image, horizontal):
        if self.is_active:
            img = image
            img2 = image.copy()
            img = flip(img, self.x, self.y, self.w, self.h, horizontal, img2)
            img = np.array(img)
            return img
        return image