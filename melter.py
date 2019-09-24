import cv2
import sys
import os
import numpy as np
from imutils import paths
import shutil
import cv2
from PIL import Image
import math
from multiprocessing import Process
from constants import *
from utils import copy_image, print_image, show_image
import imutils
import random

import pyximport; pyximport.install()

from cy.processor import threshold_fast, copy_vertical, melt, cy_copy_image, colorize, static, apply_colored_faces, flip, static_virus, get_face_img


class MeltMaster:
    def __init__(self, image, file_name, out_path, frame_rate, inverse_frame_rate=False):
        self.melt_type = 'melt'
        self.all_melters = []
        self.active_melters = []
        self.file_name = file_name
        self.out_path = out_path
        self.step_base = 1000000
        self.step = 1000000
        self.image = image
        self.melter_id = 0
        self.print_image(self.image)
        self.frame_rate = frame_rate
        self.inverse_frame_rate = inverse_frame_rate
        self.start_codex = 0

    def get_last_frame(self):
        return self.out_path + self.img_name(self.step)

    def get_next_frame(self):
        self.step += 1
        return self.out_path + self.img_name(self.step)

    def melt_method(self, method, delay, *args, **kwargs):
        self.record_codex()
        if method == 'melt':
            self.full_melt()
        if method == 'static':
            self.full_static(*args, **kwargs)
        if method == 'flash':
            self.full_face_color_glitch(**kwargs)
        if method == 'flip':
            self.flip(**kwargs)
        if method == 'pause':
            self.print_frames(**kwargs)
        if method == 'zoom_face':
            self.zoom_face()
        if method == 'shake':
            self.shake_face(**kwargs)

        return self.return_codex(delay)

    def record_codex(self):
        self.start_codex = self.step

    def return_codex(self, delay):
        return {'start': self.start_codex - self.step_base, 'end': self.step - self.step_base, 'delay': delay}

    def create_melter(self, face):
        self.melter_id += 1
        m = Melter(face, str(self.melter_id))
        self.all_melters.append(m)
        self.active_melters.append(m)

    def set_frame_rate(self, frame_rate, inverse_frame_rate):
        print('setting frame rate %s' % frame_rate)
        self.frame_rate = frame_rate,
        self.inverse_frame_rate = inverse_frame_rate

    def image_reset(self, image):
        self.image = image
        self.start_codex = self.step
        return self.return_codex(5)

    def reset_melters(self):
        print('resettting melters')
        for m in self.all_melters:
            m.reset()

    def img_name(self, num):
        return '%s-%s_%s' % (str(num), self.melt_type, self.file_name)

    def print_image(self, img):
        print_image(self.out_path, self.img_name(self.step), img)

    def print_frames(self, num_frames=10):
        for i in range(num_frames):
            self.step += 1
            self.print_image(self.image)

    def full_melt(self):
        print('FULL MELT...')
        print(self.active_melters)
        print('start step %s' % self.step)
        while len(self.active_melters) > 0:
            self.melt_step()
            self.active_melters = [m for m in self.active_melters if m.is_active]
        print('end step %s' % self.step)
        self.colorize(0)
        # self.colorize(128)

    def melt_step(self):
        self.step += 1
        melted_image = self.image
        for melter in self.active_melters:
            melted_image = melter.melt(self.image)
        if (self.step % self.frame_rate[0] == 0) != self.inverse_frame_rate:
            self.print_image(melted_image)

    def colorize(self, color):
        self.step += 1
        for melter in self.all_melters:
            self.image = melter.colorize(self.image, color=color)
        self.print_image(self.image)

    def full_static(self, target_coarse=1, img_override=None, full_frame=False, reverse=False):
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

    def full_face_color_glitch(self, img_override=None, full_frame=False):
        img = self.image
        if img_override is not None:
            img = img_override
        self.step += 1
        self.print_image(self.image)
        colored_image = img
        colored_image = cv2.applyColorMap(colored_image, COLORMAP_RAINBOW['value'])
        colored_image = np.array(colored_image)
        if not full_frame:
            colored_faces_image = self.apply_colored_faces(img, colored_image)
            colored_faces_image = np.array(colored_faces_image)
            self.step += 1
            self.print_image(colored_faces_image)
        else:
            self.step += 1
            self.print_image(colored_image)

        for i in range(2, 120):
            self.step += 1
            copy_from = self.img_name(self.step - 2)
            copy_to = self.img_name(self.step)
            copy_image(self.out_path, copy_from, copy_to)

    def apply_colored_faces(self, image, colored_image):
        mixed_image = image
        for melter in self.all_melters:
            mixed_image = melter.apply_face_mask(self.image, colored_image)
        return mixed_image

    def flip(self, horizontal=0):
        rot_image = self.image
        for melter in self.all_melters:
            print(' master horiz: %s' % horizontal)
            rot_image = melter.flip(rot_image, horizontal)
        self.print_image(rot_image)

    def zoom_face(self):
        for m in self.active_melters:
            m.zoom_face(self.get_last_frame(), self.get_next_frame())
            # show_image(self.image)
            self.print_image(self.image)

    def shake_face(self, num_shakes):
        original_height, original_width = self.image.shape[:2]
        factor = 1.5
        y = round((int(original_height * factor) - original_height) / 2)
        x = round((int(original_width * factor) - original_width) / 2)
        resized_image = cv2.resize(self.image, (int(original_width * factor), int(original_height * factor)),
                                   interpolation=cv2.INTER_CUBIC)
        crop_img = resized_image[y:y + original_height, x:x + original_width]
        max_face_dim = 0
        max_melter = None
        for m in self.all_melters:
            if m.x > max_face_dim:
                max_face_dim = m.x
                max_melter = m
            if m.y > max_face_dim:
                max_face_dim = m.y
                max_melter = m

        print('num shakes %s' % str(num_shakes))
        for s in range(num_shakes):
            self.step += 1
            rot_image = max_melter.shake(crop_img)
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
            print('horizontal %s' % horizontal)
            img = flip(img, self.x, self.y, self.w, self.h, horizontal, img2)
            img = np.array(img)
            return img
        return image

    def zoom_face(self, img_path, new_img_path):
        img = cv2.imread(img_path)
        original_height, original_width = img.shape[:2]
        factor = 2
        resized_image = cv2.resize(img, (int(original_width * factor), int(original_height * factor)),
                                   interpolation=cv2.INTER_CUBIC)
        print('show zoom face')
        show_image(resized_image)
        import sys
        sys.exit(1)
        # face_img = self.cut_out_face(img)
        print_image(new_img_path, '', img)
        foo = Image.open(new_img_path)
        # need to resize face image here
        multiplier = 1
        while (self.x + self.w) * multiplier < 300 and (self.y + self.h) * multiplier < 300:
            multiplier += 1
        print('multiplier %s' % multiplier)
        size_tuple = (int(foo.size[0] * multiplier), int(foo.size[1] * multiplier))
        # foo.resize(size_tuple)
        foo.transform(size_tuple, Image.EXTENT, (self.x, self.y, self.x + self.w, self.y + self.h))

        # foo.thumbnail((foo.size[0] / 4, foo.size[1] / 4), Image.ANTIALIAS)
        foo.save(new_img_path, optimize=True, quality=100)
        return new_img_path

    def cut_out_face(self, image):
        # img2 = self.colorize(image.copy(), 0)
        img2 = image.copy()
        face_img = get_face_img(image, self.x, self.y, self.w, self.h, img2)
        return np.array(face_img)

    def shake(self, image):
        angle = random.randrange(-10, 10, 1)
        rotated = imutils.rotate(image, angle)
        rows, cols, _ = image.shape

        randx = random.randrange(-10, 10, 1)
        randy = random.randrange(-10, 10, 1)
        M = np.float32([[1, 0, randx], [0, 1, randy]])
        dst = cv2.warpAffine(rotated, M, (cols, rows))
        # cv2.imshow("Rotated (Problematic)", rotated)
        # cv2.waitKey(0)
        return dst
