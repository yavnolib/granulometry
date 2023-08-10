import numpy as np
import math
import skimage
from skimage import exposure
import scipy.misc as misc
import rawpy
import imageio
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import os

def convert(full_path, filename, target_path, save_linear):
    data16 = np.fromfile(full_path, np.uint16)
    data16 = data16.reshape((400, 600)) # max : 2**16

    debayer = np.zeros((200, 300, 3))

    for i in range(0, data16.shape[0], 2):
        for k in range(0, data16.shape[1], 2):
            M = data16[i:i+2, k:k+2]
            r_pix = M[0, 0]
            g_pix = (M[0, 1] + M[1, 0])/2
            b_pix = M[1, 1]
            debayer[i//2, k//2, 0] = r_pix
            debayer[i//2, k//2, 1] = g_pix
            debayer[i//2, k//2, 2] = b_pix
    old_debayer = np.copy(debayer)
    # linear
    if save_linear:
        debayer = (debayer/(debayer.max())*(255)).astype(np.uint8)
        R = debayer[:, :, 0]
        G = debayer[:, :, 1]
        B = debayer[:, :, 2]
        img_deb = Image.fromarray(debayer.astype(np.uint8))
        img_deb.save(f'{target_path}/{filename}_linear.png')

    #gamma
    scaling = old_debayer.max()
    old_debayer_scaled = old_debayer/scaling
    srgb_scaled = np.where(old_debayer_scaled<=0.0031308, 
                       old_debayer_scaled*12.92, 
                     1.055*(old_debayer_scaled**(1/2.4))-0.055)
    srgb = srgb_scaled*255
    img_gamma = Image.fromarray(srgb.astype(np.uint8))
    img_gamma.save(f'{target_path}/{filename}_srgb.png')
    return img_gamma

if __name__ == '__main__':
    folder_path = input('Enter path to target folder with raw images:')
    target_path = input('Enter path to save converted images:')
    i = 0
    for dirname, _, filenames in os.walk(folder_path):
        for filename in filenames:
            i += 1
            if i<6907:
                pass
            else:
                fname, ext = filename.split('.')
                convert(os.path.join(dirname, filename), fname, target_path, 0) 
                print(f'Converted {i}/{len(filenames)} images', end='\r')