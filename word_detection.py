from typing import List

import cv2
import matplotlib.pyplot as plt
from path import Path

from PIL import ImageTk, Image

from image_processor import detection_process, recognition_process, resize_img

import pandas as pd
from tqdm import tqdm
from mltu.configs import BaseModelConfigs

# Repository: https://github.com/githubharald/WordDetector

# python main.py
# python main.py --data ../images --img_height 1000

from word_detector import detect, prepare_img, sort_multiline

from inferenceModel import ImageToWordModel

root = None
img = None
panel = None

resized = None
detection_img = None
recognition_img = None

img_d = []
img_r = []

lines = []
lines_idx = -1
line = []
word_idx = -1

word_counter = 0
word_img = None

scale = 0

ended = False

output_text = ''

def open_file(fn_img):
    global lines_idx, lines, img_d, img_r, scale
    lines_idx = 0
    if fn_img == None:
        end()
        return

    print(f'Processing file {fn_img}')
    original = cv2.imread(fn_img)
    height, width, channels = original.shape
    scale = height/1300
    resized = resize_img(original, 1300)
    #resized = resize_img(cv2.imread(fn_img), parsed.img_height)
    detection_img = detection_process(resized)
    #recognition_img = recognition_process(resized)
    img_r = recognition_process(original)

    img_d = prepare_img(detection_img, 1300)
    #img_r = prepare_img(recognition_img, parsed.img_height)

    # Modified to avoid needing command line arguments
    detections = detect(img_d,
                        kernel_size=25,
                        sigma=11,
                        theta=7,
                        min_area=100)

    # sort detections: cluster into lines, then sort each line
    lines = sort_multiline(detections)

    next=False

def next_line():
    global lines_idx, line, word_idx, ended, output_text
    lines_idx += 1
    output_text=output_text+'\n'
    if lines_idx >= len(lines):
        end()   # Changed to accomodate only 1 page
        if ended:
            return
    
    if lines_idx >= len(lines):
        return
    line = lines[lines_idx]
    word_idx = 0

    return

def next_word():
    global word_idx, line, ended, word_img, scale
    word_idx += 1
        
    if word_idx >= len(line):
        next_line()
        if ended:
            return
    if word_idx >= len(line):
        return
        
    det = line[word_idx]
    xs = [det.bbox.x, det.bbox.x, det.bbox.x + det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
    ys = [det.bbox.y, det.bbox.y + det.bbox.h, det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]
    x1 = min(xs[0], xs[2]) - 0
    x2 = max(xs[0], xs[2]) + 0
    y1 = min(ys[0], ys[1]) - 0
    y2 = max(ys[0], ys[1]) + 0
    if (x1 < 0):
        x1 = 0
    if (y1 < 0):
        y1 = 0
    if (x2 > img_d.shape[1]):
        x2 = 1
    if (y2 > img_d.shape[0]):
        y2 = 1
    crop_img_d = img_d[y1:y2+1, x1:x2+1]
    #crop_img_r = img_r[y1:y2+1, x1:x2+1]
    crop_img_r = img_r[int(scale*y1):int(scale*y2)+1, int(scale*x1):int(scale*x2)+1]
    # cv2.imshow("word", crop_img_r)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    height, width = crop_img_d.shape
    if height == 0 or width == 0 or height > 75:    # words taller than 75 px are ignored (fine-tune or re-think later)
        return next_word()

    word_img = cv2.cvtColor(crop_img_r, cv2.COLOR_GRAY2BGR)

    return word_img


def end():
    global ended
    ended = True
    # root.destroy()  # If you want to run some code after tkinter.mainloop(), use quit() instead of destroy()

def main():    
    
    try: 
        open_file(next(img_iter))
    except StopIteration: 
        print('No input images! Please put the images in the \'images\' folder!')
        end()
    next_line()

    configs = BaseModelConfigs.load("Models/configs.yaml")

    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    while not ended:
        img = next_word()
        if ended:
            break
        prediction_text = model.predict(img)
        print(prediction_text, end=' ')

        
def convert_to_text(fname):    
    global output_text
    
    open_file(fname)      # Changed to accomodate only 1 page
    next_line()

    configs = BaseModelConfigs.load("Models/configs.yaml")

    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    output_text = ''

    while not ended:
        img = next_word()
        if ended:
            break
        prediction_text = model.predict(img)

        output_text = output_text+prediction_text+' '

    return output_text

# MAKE IT PRINT THE FILE NAME INTO THE words.txt    


if __name__ == '__main__':
    main()
