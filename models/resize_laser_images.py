import cv2
import os
import glob
import numpy as np

root_folder = os.path.join("/mnt/hdd0", "NLOS", "2022")
folders = glob.glob(os.path.join(root_folder, "*/*D*"))

W, H = 64, 128

for i, folder in enumerate(folders):
    print("Resizing ... {}/{}".format(i + 1, len(folders)))
    dst_path = os.path.join(folder, "reflection_images.npy")
    laser_images_01 = sorted(glob.glob(os.path.join(folder, "reflection_image_*_C01.png")))
    laser_images_02 = sorted(glob.glob(os.path.join(folder, "reflection_image_*_C02.png")))
    one_frame = cv2.imread(laser_images_01[0])
    l_H, l_W, _ = one_frame.shape
    h = int(round(l_H / 3))  # Naive pre-processing for cropping background
    laser_images_01 = [np.transpose(cv2.imread(path)[:-h], (1, 0, 2))[:, ::-1] for path in laser_images_01]
    laser_images_02 = [np.transpose(cv2.imread(path)[:-h], (1, 0, 2))[:, ::-1] for path in laser_images_02]
    # Grid_H, Grid_W, Image_H, Image_W, 3
    laser_images_01 = np.transpose(np.reshape(laser_images_01, (5, 5, H, W, 3)), (1, 0, 2, 3, 4))
    laser_images_02 = np.transpose(np.reshape(laser_images_02, (5, 5, H, W, 3)), (1, 0, 2, 3, 4))

    # 2, G_H, G_W, I_H, I_W, 3
    laser_images = np.stack([laser_images_01, laser_images_02], axis=0)
    with open(dst_path, "w") as fp:
        np.save(fp, laser_images)


