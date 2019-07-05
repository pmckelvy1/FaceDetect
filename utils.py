import shutil
import cv2


def print_image(out_path, out_file_name, img):
    cv2.imwrite(out_path + out_file_name, img)


def copy_image(out_path, copy_from, copy_to):
    shutil.copyfile(out_path + copy_from, out_path + copy_to)


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
