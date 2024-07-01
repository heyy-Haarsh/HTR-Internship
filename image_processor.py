import argparse
from PIL import Image
from typing import List
import cv2
import matplotlib.pyplot as plt
from path import Path
import numpy as np
#from pyimgscan import preprocess, gethull, getcorners, reshape, perspective_transform

def get_img_files(data_dir: Path) -> List[Path]:
    """Return all image files contained in a folder."""
    res = []
    for ext in ['*.png', '*.jpg', '*.bmp']:
        res += Path(data_dir).files(ext)
    return res

def remove_horizontal_lines(img):
    # ref: https://stackoverflow.com/questions/71425968/remove-horizontal-lines-with-open-cv

    if len(img.shape) != 2:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    gray = cv2.bitwise_not(gray)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
    cv2.THRESH_BINARY, 15, -2)

    horizontal = np.copy(bw)

    cols = horizontal.shape[1]
    horizontal_size = cols // 30

    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))

    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    dst = cv2.inpaint(img,horizontal,3,cv2.INPAINT_TELEA)   # horizontal acts as a mask

    return dst

def detection_process(img):

    hor_lines_removed = remove_horizontal_lines(img)

    #blurred = cv2.GaussianBlur(hor_lines_removed,(1, 1),cv2.BORDER_CONSTANT)     # TRY: use the blur for word detection but not for word reading
    filtered =  cv2.bilateralFilter(hor_lines_removed,10,100,75)   # EVEN FOR BILATERAL FILTER try two diff. variations for detection & reading
    
    grayscale = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)

    result = cv2.adaptiveThreshold(grayscale,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    return result

def recognition_process(img):

    # For now, detection and recognition use the same processing
    # Comment out the following line to change that:
    return detection_process(img)

    hor_lines_removed = remove_horizontal_lines(img)

    #blurred = cv2.GaussianBlur(img,(3, 3),0)
    blurred = cv2.GaussianBlur(hor_lines_removed,(3, 3),0)
    filtered =  cv2.bilateralFilter(blurred,9,75,75)
    
    grayscale = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)

    result = cv2.adaptiveThreshold(grayscale,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('images'))
    parser.add_argument('--kernel_size', type=int, default=25)
    parser.add_argument('--sigma', type=float, default=11)
    parser.add_argument('--theta', type=float, default=7)
    parser.add_argument('--min_area', type=int, default=100)
    parser.add_argument('--img_height', type=int, default=1200)
    parsed = parser.parse_args()

    for fn_img in get_img_files('images'):
        print(f'Processing file {fn_img}')

        img = resize_img(cv2.imread(fn_img), parsed.img_height)
        
        cv2.imshow("original", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        processed_d = detection_process(img)

        cv2.imshow("processed for detection", processed_d)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        processed_r = recognition_process(img)

        cv2.imshow("processed for recognition", processed_r)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



def resize_img(img: np.ndarray,
                height: int) -> np.ndarray:
    """Convert image to grayscale image (if needed) and resize to given height."""
    # copied from the WordDetector source code but with removing the conversion to grayscale
    assert img.ndim in (2, 3)
    assert height > 0
    assert img.dtype == np.uint8
    #if img.ndim == 3:
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h = img.shape[0]
    factor = height / h
    return cv2.resize(img, dsize=None, fx=factor, fy=factor)

def scan_img(img: np.ndarray):
    
    # obtain the adjusted image, scaled image along with its scale factor, and the
    # Canny edge image
    img_adj, scale, img_scaled, img_edge = preprocess(img)

    # perform convex hull on edge image to prevent imcomplete outline
    img_hull = gethull(img_edge)

    # obtain 4 corner points of the convex hull image
    corners = getcorners(img_hull)

    # scale the corner points back to the original size of the image using the scale
    # calculated previously
    corners = corners.reshape(4, 2) * scale

    # finally correct the perspective of the image by applying four-point
    # perspective transform
    img_corrected = perspective_transform(img_adj, corners)

    return img_corrected

if __name__ == '__main__':
    main()

def resize_img_square(path: str, length: int):
    im = Image.open(path)
    sqrWidth = np.ceil(np.sqrt(im.size[0]*im.size[1])).astype(int)
    im_resize = im.resize((sqrWidth, sqrWidth))
    print(path)
    im_resize.save(path)