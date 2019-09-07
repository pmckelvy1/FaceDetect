import os
from imutils import paths
import shutil
import moviepy.editor as mp
from ffmpy import FFmpeg
from constants import *
import cv2
import numpy as np


class Videoizer:
    def __init__(
            self,
            title,
            gif_codex=None,
            out_path=os.path.dirname(os.path.realpath(__file__))+'/vids/',
            frame_path= os.path.dirname(os.path.realpath(__file__))+'/frames/',
            gif_path=os.path.dirname(os.path.realpath(__file__)) + '/gifs/',
            audio_path=os.path.dirname(os.path.realpath(__file__)) + '/audio/',
            audio_name='punkout_clip.wav',
            config_name='default',
            clean=False
    ):
        self.gif_path = gif_path
        self.audio_path = audio_path
        self.audio_name = audio_name
        self.frame_path = frame_path
        self.out_path = out_path
        self.title = title
        self.gif_name = title + '.gif'
        self.vid_name = title + '.mp4'
        self.config = VIDEO_CONFIGS[config_name]
        self.clean = clean
        self.gif_codex = gif_codex

    def cleanup(self):
        shutil.rmtree(self.frame_path)
        os.mkdir(self.frame_path)

        shutil.rmtree(self.gif_path)
        os.mkdir(self.gif_path)

    def clean_dir(self):
        if self.clean:
            shutil.rmtree(self.out_path)
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

    def videoize(self):
        print('videoizing')
        print('clean_dir')
        self.clean_dir()
        print('create_gif')
        self.create_gif()
        print('create_video')
        self.create_video()
        print('cleanups')
        self.cleanup()

    def create_gif(self):
        # grab all image paths in the input directory
        image_paths = sorted(list(paths.list_images(self.frame_path)))

        # remove the last image path in the list
        first_path = image_paths[0]
        last_path = image_paths[-1]
        # image_paths = [ip for i, ip in enumerate(image_paths[:-1]) if i % 10 == 0]
        image_paths = image_paths[:-1]

        first_img = image_paths[0]
        first_img_pieces = first_img.split(':')
        frame_name = first_img_pieces[1]
        print(self.gif_codex)

        # construct the image magick 'convert' command that will be used
        # generate our output GIF, giving a larger delay to the final
        # frame (if so desired)
        if self.gif_codex:
            cmd = "convert "
            for scene in self.gif_codex:
                cmd += "-delay " + str(scene['delay']) + " "
                cmd += " ".join(image_paths[scene['start']:scene['end']]) + " "
            cmd += "-loop 0 "

        else:
            cmd = "convert -delay {} {} -delay {} {} -delay {} {} -loop {} ".format(
                self.config[FIRST_DELAY], first_path,
                self.config[FRAME_DELAY], " ".join(image_paths),
                self.config[LAST_DELAY], last_path,
                self.config[LOOP])
        cmd += self.gif_path + self.title + '.gif'
        print(cmd)
        os.system(cmd)

    def create_gif_from_sequence(self, frame_dir, seq):
        imgs = ' '.join([frame_dir + '/' + s for s in seq])
        cmd = "convert -delay {} {} -loop {} ".format(
            self.config[FRAME_DELAY], imgs,
            self.config[LOOP])
        cmd += self.gif_path + self.title + '.gif'
        print(cmd)
        os.system(cmd)

    def gif_to_video(self):
        clip = mp.VideoFileClip(self.gif_path + self.gif_name)
        clip.write_videofile(self.out_path + self.vid_name)

    def create_video(self):
        in_gif = self.gif_path + self.gif_name
        in_audio = self.audio_path + self.audio_name
        # TODO check if video name exists, if so, version bump
        out_video = self.out_path + self.vid_name
        ff = FFmpeg(
            inputs={in_gif: None, in_audio: None},
            outputs={out_video: '-movflags faststart -t 28 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"'}
        )
        ff.run()

    def play_video(self, video_file):
        # Create a VideoCapture object and read from input file
        cap = cv2.VideoCapture(video_file)

        # Check if camera opened successfully
        if (cap.isOpened() == False):
            print("Error opening %s" % video_file)

        # Read until video is completed
        while (cap.isOpened()):

            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:

                # Display the resulting frame
                cv2.imshow('Frame', frame)

                # Press Q on keyboard to  exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break

        # release the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()
