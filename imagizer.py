import cv2
import os
import shutil
from PIL import Image, ImageFont, ImageDraw
from melter import MeltMaster
from constants import *
from utils import print_image
import numpy as np


class Imagizer:
    def __init__(self):
        casc_path = os.path.dirname(os.path.realpath(__file__)) + "/haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(casc_path)
        self.img_path = None
        self.img_name = None
        self.out_path = None
        self.image = None
        self.original_image = None
        self.melt_master = None

    def init(self, img_path, img_name, out_path, compress=True):
        self.out_path = out_path
        self.load_image(img_path, img_name, compress=compress)
        self.create_melters()

    def load_image(self, img_path, img_name, compress=True):
        self.img_path = img_path
        self.img_name = img_name
        self.compress = compress
        self.reload_image()

    def reload_image(self):
        if self.compress:
            self.img_name = self.compress_image(self.img_path, self.img_name)
        self.original_image = cv2.imread(self.img_path + self.img_name)
        self.image = cv2.imread(self.img_path + self.img_name)
        if self.melt_master:
            return self.melt_master.image_reset(self.image)

    def detect_faces(self):
        try:
            faces = self.face_cascade.detectMultiScale(
                self.image,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
                # flags = cv2.CV_HAAR_SCALE_IMAGE
            )

            print("{0} :: Found {1} faces!".format(self.img_name, len(faces)))
            return faces
        except Exception as e:
            print('woops detect_faces: %s' % self.img_path + self.img_name)
            print(e)
            raise

    def get_num_faces(self, file_path, file_name):
        self.load_image(file_path, file_name)
        faces = self.detect_faces()
        self.show_image(self.image)
        return len(faces)

    def create_melters(self):
        self.clear_dir(self.out_path)

        self.melt_master = MeltMaster(self.image, self.img_name, self.out_path, 1)

        faces = self.detect_faces()
        for face in faces:
            self.melt_master.create_melter(face)

    def face_melt(self):
        print('applying melt')
        self.melt_master.set_frame_rate(2)
        return self.melt_master.melt_method('melt', 1)

    def pause(self, num_frames=10):
        print('applying pause')
        return self.melt_master.melt_method('pause', 100, num_frames=num_frames)

    def face_static(self, frame_rate, override=False, full_frame=False, reverse=False, num_frames=130):
        print('applying static')
        self.melt_master.set_frame_rate(frame_rate)
        if override:
            return self.melt_master.melt_method('static', 1, target_coarse=num_frames, img_override=self.original_image, full_frame=full_frame, reverse=reverse)
        else:
            return self.melt_master.melt_method('static', 1, target_coarse=num_frames, full_frame=full_frame, reverse=reverse)

    def face_flash(self):
        print('applying face color glitch')
        self.melt_master.set_frame_rate(1)
        return self.melt_master.melt_method('flash', 1)

    def full_flash(self):
        print('applying full color glitch')
        self.melt_master.set_frame_rate(1)
        return self.melt_master.melt_method('flash', 1, full_frame=True)

    def face_flip(self):
        return self.melt_master.melt_method('flip', 1, horizontal=1)

    def zoom_face(self):
        gif_codex = self.melt_master.melt_method('zoom_face', 1)
        # self.show_image(self.image)
        return gif_codex

    def add_text(self):
        org = (int(self.image.shape[0]/8), int(2 * self.image.shape[1]/3))
        print(org)
        top_left = org
        bottom_right = (org[0] + 220, org[1] + 20)
        img_name = self.melt_master.get_last_frame()
        img = Image.open(img_name)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./fonts/Courier-BoldRegular.ttf", 20)
        draw.rectangle((top_left, bottom_right), fill=0, width=100)
        draw.text(org, "the technocratic", font=font)
        img.save(self.melt_master.get_next_frame())
        img = np.array(img)
        # self.show_image(img)
        return self.melt_master.image_reset(img)

        # cv2.addText(self.original_image, "the technocratic", org, cv2.FONT_HERSHEY_DUPLEX)

    def full_loop(self):
        print(os.curdir)
        for file_name in os.listdir(os.curdir + '/pics'):
            try:
                if file_name.split('.')[1] in VALID_EXT:
                    print(file_name)
                    self.face_melt()
            except Exception as e:
                print(e)
                continue

    def create_colormap_samples(self, image, file_name):
        for cmt in COLOR_MAP_TYPES:
            image = cv2.applyColorMap(image, cmt['value'])
            print_image('./colormap_samples/', cmt['name'] + '_' + file_name, image)

    @staticmethod
    def clear_dir(dirname):
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    @staticmethod
    def compress_image(file_path, file_name, qual=50, resize=True):
        foo = Image.open(file_path + file_name)
        new_file_name = 'comp_' + str(qual) + file_name
        if resize:
            divisor = 1
            while foo.size[0] / divisor > 300 and foo.size[1] / divisor > 300:
                divisor += 1
            print('divisor %s' % divisor)
            foo = foo.resize((int(foo.size[0] / divisor), int(foo.size[1] / divisor)))
        # foo.thumbnail((foo.size[0] / 4, foo.size[1] / 4), Image.ANTIALIAS)
        foo.save(file_path + new_file_name, optimize=True, quality=qual)
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
