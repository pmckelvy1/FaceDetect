from imagizer import Imagizer
from videoizer import Videoizer


if __name__ == '__main__':
    imgz = Imagizer()
    imgz.init('./pics/', 'billie_cry.jpeg', './frames/')
    # imgz.init('./pics/', 'abba.png', './frames/')
    imgz.face_static(1, reverse=True, full_frame=True)
    imgz.reload_image()
    imgz.face_flash()
    imgz.face_melt()
    imgz.face_static(5, override=True)
    imgz.face_flip()
    imgz.face_flash()
    vidz = Videoizer('test', clean=True, config_name='full')
    vidz.videoize()
