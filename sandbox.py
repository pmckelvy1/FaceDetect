from imagizer import Imagizer
from videoizer import Videoizer


if __name__ == '__main__':
    imgz = Imagizer()
    # imgz.init('./pics/', 'billie_cry.jpeg', './frames/')
    imgz.init('./pics/', 'abba.png', './frames/')
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
    gif_codex.append(imgz.face_flash())
    gif_codex.append(imgz.full_flash())
    vidz = Videoizer('test', clean=True, config_name='full', gif_codex=None)
    vidz.videoize()
