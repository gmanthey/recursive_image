"""
This file is part of Recursive Image.

Recursive Image is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Recursive Image is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Recursive Image.  If not, see <http://www.gnu.org/licenses/>.
"""

from os import listdir
import numpy as np
import cv2
from scipy.spatial.distance import cdist
from math import floor, ceil
import sys


def make_image(path, ref_img_path, out, res_width = None, res_height = None, mini_width = None, mini_height = None, color_from_orig = False, color_diff = 30):
    """
        Generates a image using a number of images as pixels.

        Assigns all the images in the ``path``-variable to pixels of the resulting image. If res_width/res_height is not 
        specified, the minimum width/height needed to include all the images in ``path`` is used. If one of the Variables is given,
        the other one is chosen so that the width/height ratio of the reference image is still intact.
        If mini_width/mini_height is not specified, the average width/height ratio and the average size of all the images in 
        ``path`` is used. If only one is given, the other one is chosen, so that the average width/height ratio of the images 
        stays intact.

        Parameters
        ----------
        path : String  
            Path to images used as pixels. The folder should contain only the images and all the images should be in png or jpg 
            format.  
        ref_img_path : String  
            Path to the image used as reference for the resulting image. The image should be in png or jpg format.  
        out : String
            The name of the output file. The result will be saved in <out>.png
        res_width : int, optional  
            The number of images that make up the width of the resulting pictures.
        res_height : int, optional
            The number of images that make up the height of the resulting pictures.
        mini_width : int, optional
            The number of pixels one of the pixel-images is wide.
        mini_height : int, optional
            The number of pixels one of the pixel-images is high.
        color_from_orig : bool, optional
            If true, the color used for the background of the pixel-images is taken from the reference image, if false, the 
            average color of the pixel-image is used as background.
        color_diff : float, optional
            The maximum difference allowed between the color of the reference image and the average color of the pixel image when
            randomly assigning images.

        Notes
        -----
        It is advised to give one of res_width/res_height and one of mini_width/mini_height, so that the overall size of the 
        resulting image can be specified, but the program can calculate the best fitting ratios.  

        If color_from_orig is False, color_diff should be kept relatively low, so that the reference image can still be 
        identified. 30 seems to be a good value to still have some variation in the resulting images. If color_diff is very small,
        so that there are no images available that are that close, a random image is taken from the best fitting 20 images.

        If color_from_orig is True, color_diff may be chosen higher, so that there is a larger variation in the pixel-images. Then 
        the reference image will always be visible due to the background of the pixel-images. 

        The program might generate a lot of libpng warnings. This is not a problem, as long as the program keeps running.
    """
    try:
        files = np.array(listdir(path))
    except FileNotFoundError:
        print('Path {} not found.'.format(path))
        sys.exit(2)

    
    ref_img = cv2.imread(ref_img_path)

    if ref_img is None:
        print('Reference image {} not found.'.format(ref_img_path))
        sys.exit(2)
    
    avg_rgb = np.zeros([len(files), 3])
    heights = np.zeros(len(files), dtype=int)
    wh_ratios = np.zeros(len(files))

    for i in range(len(files)):
        img = cv2.imread(path + files[i])
        if img is None:
            print('{}{} is not a supported image.'.format(path, files[i]))
            sys.exit(2)

        avg_rgb[i] = np.mean(img, (0, 1))
        wh_ratios[i] = np.size(img, 1) / np.size(img, 0)
        heights[i] = np.size(img, 0)

    if mini_height == None and mini_width == None:
        wh_ratio = np.mean(wh_ratios)
        re_wh_ratio = np.size(ref_img, 1) / (np.size(ref_img, 0) * wh_ratio)
        avg_height = int(np.mean(heights))
    elif mini_height == None:
        wh_ratio = np.mean(wh_ratios)
        re_wh_ratio = np.size(ref_img, 1) / (np.size(ref_img, 0) * wh_ratio)
        avg_width = mini_width
        avg_height = int(avg_width / wh_ratio)
    elif mini_width == None:
        wh_ratio = np.mean(wh_ratios)
        re_wh_ratio = np.size(ref_img, 1) / (np.size(ref_img, 0) * wh_ratio)
        avg_height = mini_height
    else:
        avg_height = mini_height
        avg_width = mini_width
        wh_ratio = avg_width / avg_height
        re_wh_ratio = np.size(ref_img, 1) / (np.size(ref_img, 0) * wh_ratio)

    if res_height == None and res_width == None:
        width = np.sqrt(len(files) * re_wh_ratio)
        height = len(files) / width

        width = int(width)
        height = int(height) + 1

        if width * height < len(files):
            height = height - 1
            width = width + 1

        if width * height < len(files):
            height = height + 1
    elif res_height == None:
        width = res_width
        height = int(width / re_wh_ratio)
    elif res_width == None:
        height = res_height
        width = int(height * re_wh_ratio)
    else:
        width = res_width
        height = res_height


    wh_ratio = np.size(ref_img, 1) / np.size(ref_img, 0) * height / width

    if mini_width == None:
        avg_width = int(avg_height * wh_ratio)
    else:
        avg_width = mini_width

    res_pixels = cv2.resize(ref_img, dsize = (width, height), interpolation=cv2.INTER_AREA)

    pixel_list = np.reshape(res_pixels, [-1, 3])
    indices_img = np.random.permutation(width*height)

    pixel_list = pixel_list[indices_img]

    img_pos = np.zeros([height, width], dtype = int)

    diffs = cdist(avg_rgb, pixel_list)

    indices_avg = np.arange(len(files))
    
    for i in range(len(files)):
        minimum = np.argmin(np.min(diffs, axis = 1))
        index = np.argmin(diffs[minimum])
        x = indices_img[index] % width
        y = indices_img[index] // width
        img_pos[y, x] = indices_avg[minimum]
        diffs = np.delete(diffs, minimum, axis = 0)
        diffs = np.delete(diffs, index, axis = 1)
        indices_avg = np.delete(indices_avg, minimum)
        indices_img = np.delete(indices_img, index)

    diffs = cdist(avg_rgb, np.reshape(res_pixels, [-1, 3])[indices_img])

    for i in range(width*height - len(files)):
        mins = np.where(diffs[:, i] < color_diff)[0]
        if len(mins) == 0:
            mins = np.argsort(diffs[:, i])[:20] # Change the 20 here if the resulting image is not recognisable as the
        minimum = np.random.choice(mins)        # reference image and changing color_diff doesn't give better results
        x = indices_img[i] % width
        y = indices_img[i] // width
        img_pos[y, x] = minimum

    res_img = np.zeros([height*avg_height, width*avg_width, 3], dtype="uint8")

    for x in range(width):
        for y in range(height):
            img = cv2.imread(path + files[img_pos[y, x]])
            if wh_ratios[img_pos[y, x]] > wh_ratio:
                new_width = avg_width
                new_height = int(new_width / wh_ratios[img_pos[y, x]])
                padding_up = floor((avg_height - new_height) / 2)
                padding_down = ceil((avg_height - new_height) / 2)
                padding_left = 0
                padding_right = 0
            else:
                new_height = avg_height
                new_width = int(new_height * wh_ratios[img_pos[y, x]]) 
                padding_up = 0
                padding_down = 0
                padding_left = floor((avg_width - new_width) / 2)
                padding_right = ceil((avg_width - new_width) / 2)

            img = cv2.resize(img, (new_width, new_height))
            if color_from_orig:
                color = [int(res_pixels[y, x, 0]), int(res_pixels[y, x, 1]), int(res_pixels[y, x, 2])]
            else:
                color = [int(avg_rgb[img_pos[y, x], 0]), int(avg_rgb[img_pos[y, x], 1]), int(avg_rgb[img_pos[y, x], 2])]
            img = cv2.copyMakeBorder(img, padding_up, padding_down, padding_left, padding_right, borderType=cv2.BORDER_CONSTANT, value = color)
            res_img[y*avg_height:(y+1)*avg_height, x*avg_width:(x+1)*avg_width] = img


    cv2.imwrite(out, res_img)

if __name__ == '__main__':
    print('Please execute the recursive_image.py file for using this program.')