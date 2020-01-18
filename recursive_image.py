#! /usr/bin/env python3

version = 'Recursive Image v1.0'

from sys import argv, exit
from getopt import getopt, GetoptError
from make_image import make_image

helptext = """
usage: {} -r <reference-image> -p <images-folder> -o <output-image>

This program generates a image using other images as pixels.

Arguments:
    -h, --help
        Prints out this text.
    -o, --out
        Specifies the output png-file.
    -p, --img-path
        The path containing the images used to make the reference image. This path should contain only images in png or jpg format.
    -r, --ref-img
        The image that is rebuilt with the other images.
    -v, --version
        Prints out the version of the program.

Other Arguments
    --color-diff
        The maximum difference allowed between the color of the reference image and the average color of the pixel image when randomly 
        assigning images.
    --mini-height
        The number of pixels one of the pixel-images is high.
    --mini-width
        The number of pixels one of the pixel-images is wide.
    --out-height
        The number of images that make up the height of the resulting pictures.
    --out-width
        The number of images that make up the width of the resulting pictures.
    --ref-background
        If 1, the color used for the background of the pixel-images is taken from the reference image, if 0, the average color of the 
        pixel-image is used as background.

Notes
    It is advised to give one of out_width/out_height and one of mini_width/mini_height, so that the overall size of the resulting
    image can be specified, but the program can calculate the best fitting ratios.  

    If ref-background is False, color-diff should be kept relatively low, so that the reference image can still be identified. 
    30 seems to be a good value to still have some variation in the resulting images. If color-diff is very small, so that there 
    are no images available that are that close, a random image is taken from the best fitting 20 images.

    If ref-background is True, color-diff may be chosen higher, so that there is a larger variation in the pixel-images. Then the
    reference image will always be visible due to the background of the pixel-images.

    The program might generate a lot of libpng warnings. This is not a problem, as long as the program keeps running.
""".format(argv[0])

wrong_argument = """
{} must be a positive Integer.
"""

args = argv[1:]

ref_img = ''
path = ''
out = ''
out_width = None
out_height = None
mini_width = None
mini_height = None
ref_background = False
color_diff = 30

if len(args) > 0:
    try:
        opts, args = getopt(args, 'hvr:p:o:', ['help', 'version', 'ref-img=', 'img-path=', 'out=', 'out-width=', 'out-height=', 'mini-widht=', 'mini-heigh=', 'ref-background=', 'color-diff='])
    except GetoptError:
        print(help_text)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(helptext)
            exit()
        if opt in ('-v', '--version'):
            print(version)
            exit()
        if opt in ('-r', '--ref-img'):
            ref_img = arg
        if opt in ('-p', '--img-path'):
            path = arg
        if opt in ('-o', '--out'):
            out = arg
        if opt == '--out-width':
            try:
                out_width = int(arg)
            except Exception:
                out_width = -1
            if out_width < 0:
                print(wrong_argument.format('out-width'))
                exit(2)
        if opt == '--out-height':
            try:
                out_height = int(arg)
            except Exception:
                out_height = -1
            if out_height < 0:
                print(wrong_argument.format('out-height'))
                exit(2)
        if opt == '--mini-width':
            try:
                mini_width = int(arg)
            except Exception:
                    mini_width = -1
            if mini_width < 0:
                print(wrong_argument.format('mini-width'))
                exit(2)
        if opt == '--mini-height':
            try:
                mini_height = int(arg)
            except Exception:
                mini_height = -1
            if mini_height < 0:
                print(wrong_argument.format('mini-height'))
                exit(2)
        if opt == '--ref-background':
            if arg in ('False', 'false', 'F', 'f', '0'):
                ref_background = False
            elif arg in ('True', 'true', 'T', 't', '1'):
                ref_background = True
            else:
                print('ref-background must be a boolean.')
                exit(2)
        if opt == '--color-diff':
            try:
                color_diff = float(arg)
            except:
                color_diff = -1
            if color_diff < 0:
                print('color-diff must be a positive number')
                exit(2)
    
    if ref_img == "" or path == "" or out == "":
        print(helptext)
        exit(2)

    make_image(path, ref_img, out, out_width, out_height, mini_width, mini_height, ref_background, color_diff)

else:
    print(helptext)