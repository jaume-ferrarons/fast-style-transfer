import scipy.misc
import numpy as np
import os
import sys
import random
import subprocess
import shutil


def save_img(out_path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    scipy.misc.imsave(out_path, img)


def scale_img(style_path, style_scale):
    scale = float(style_scale)
    o0, o1, o2 = scipy.misc.imread(style_path, mode='RGB').shape
    scale = float(style_scale)
    new_shape = (int(o0 * scale), int(o1 * scale), o2)
    style_target = get_img(style_path, img_size=new_shape)
    return style_target


def get_media(src):
    if src[-4:] == ".mp4":
        return sample_video(src)
    else:
        print "Reading image"
        return [get_img(src)]


def get_img(src, img_size=False):
    img = scipy.misc.imread(src, mode='RGB')  # misc.imresize(, (256, 256, 3))
    if not (len(img.shape) == 3 and img.shape[2] == 3):
        img = np.dstack((img, img, img))
    if img_size != False:
        img = scipy.misc.imresize(img, img_size)
    return img


def exists(p, msg):
    assert os.path.exists(p), msg


def list_files(in_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        files.extend(filenames)
        break

    return files


def duration_to_seconds(duration):
    """Duration is of the form 00:21:19.50"""
    (hms, millis) = duration.split('.')
    (h, m, s) = map(lambda x: int(x), hms.split(':'))
    return h * 3600 + m * 60 + s


def sample_video(in_path, n_samples=10):
    TMP_VIDEO_DIR = '.tmp/'
    DURATION_FILE = TMP_VIDEO_DIR + 'duration'
    # Create TMP_VIDEO_DIR if doesn't exsist
    if not os.path.exists(TMP_VIDEO_DIR):
        os.makedirs(TMP_VIDEO_DIR)
    # Get the duration of the video
    cmd = ' '.join(["ffmpeg -i", in_path,
                    "2>&1 | grep Duration | awk '{print $2}' | tr -d , >", DURATION_FILE])
    subprocess.call(cmd, shell=True)
    duration = open(DURATION_FILE, 'r').readline().strip()
    print "Video duration: ", duration
    seconds = duration_to_seconds(duration)
    sample_cmd = ' '.join(["ffmpeg -i", in_path, '-vf fps=%d/%d' %
                           (n_samples, seconds), TMP_VIDEO_DIR + "out%d.png"])
    print "Taking sample"
    subprocess.call(sample_cmd, shell=True)
    images_path = [
        TMP_VIDEO_DIR + fname for fname in list_files(TMP_VIDEO_DIR) if fname[-4:] == ".png"]
    print images_path
    return map(get_img, images_path)
