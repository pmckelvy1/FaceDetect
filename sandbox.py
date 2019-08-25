from imagizer import Imagizer
from videoizer import Videoizer
from sequencer import Sequencer
import os


def videosize():
    imgz = Imagizer()
    # imgz.init('./pics/', 'billie_cry.jpeg', './frames/')
    # imgz.init('./pics/', 'abba.png', './frames/')
    # frame_path = './frames/'
    frame_path = '/Users/patrickmckelvy/technocracy/frames/'
    imgz.init('/Users/patrickmckelvy/technocracy/instapics/', '2115817698241053766.jpg', frame_path)
    #
    gif_codex = []
    gif_codex.append(imgz.face_static(1, reverse=True, full_frame=True, num_frames=150))
    gif_codex.append(imgz.reload_image())
    gif_codex.append(imgz.zoom_face())
    imgz.pause(num_frames=80)
    gif_codex.append(imgz.face_flash())
    gif_codex.append(imgz.face_melt())
    gif_codex.append(imgz.face_static(5, override=True, num_frames=50))
    imgz.add_text()
    imgz.pause(num_frames=10)

    gif_codex.append(imgz.face_flip())
    imgz.add_text()
    gif_codex.append(imgz.face_flash())
    gif_codex.append(imgz.full_flash())
    clean=False
    vidz = Videoizer('test', frame_path=frame_path, out_path='/Users/patrickmckelvy/technocracy/vids/', clean=clean, config_name='full', gif_codex=None)
    vidz.videoize()


def face_sequence():
    codex = [
        ['0', 'fo', 'ho', 'fc', 'hc'],
        ['_'],
        ['0', 'fo', 'ho', 'fc', 'hc'],
        ['_'],
        ['0', 'fo', 'ho', 'fc', 'hc'],
        ['-'],
        ['0', 'a', 's', 'p'],
        ['_'],
        ['0', 'a', 's', 'p'],
        ['_'],
        ['0'],
        ['.png']
    ]
    seq = Sequencer(codex, './seq_test')
    gif_seq = seq.gen_sequence()
    vidz = Videoizer('seq_test', clean=True, config_name='full', gif_codex=None)
    vidz.create_gif_from_sequence('./seq_test', gif_seq)
    print('done')


def collect_faces(dir):
    imgz = Imagizer()
    # imgz.init(dir, '', '')
    face_dir = {}
    for filename in os.listdir(dir):
        if filename.endswith(".png"):
            print('checking %s' % filename)
            face_dir[filename] = imgz.get_num_faces(dir, filename)
        else:
            continue

    print(face_dir)


if __name__ == '__main__':
    videosize()
    # face_sequence()
    # collect_faces('./seq_test/')
