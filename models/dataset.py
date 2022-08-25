import os
import numpy as np
import torch
import cv2
import glob
from torch.utils.data import Dataset


class NlosDataset(Dataset):

    def __init__(self, config, dataset_type="training"):
        self.config = config
        self.dataset_type = dataset_type

        self.folders = sorted(glob.glob(os.path.join(config["data_folder"], dataset_type, "*D*")))
        print("Making Train Dataset Object ... {} Instances".format(len(self.folders)))

    def __len__(self):
        return len(self.folders)

    def __getitem__(self, index):
        data_folder = self.folders[index]

        '''
        Read Laser Images
        '''
        laser_images_01 = sorted(glob.glob(os.path.join(data_folder, "reflection_image_*_C01.png")))
        laser_images_02 = sorted(glob.glob(os.path.join(data_folder, "reflection_image_*_C02.png")))

        W, H = self.config["laser_input_size"] # target laser image size for input

        one_frame = cv2.imread(laser_images_01[0]) # to get original laser image size
        l_H, l_W, _ = one_frame.shape
        h = int(round(l_H / 3))
        laser_images_01 = [np.transpose(cv2.imread(path)[:-h], (1, 0, 2))[:, ::-1] for path in laser_images_01]
        laser_images_02 = [np.transpose(cv2.imread(path)[:-h], (1, 0, 2))[:, ::-1] for path in laser_images_02]

        laser_images_01 = [cv2.resize(image, (W, H)) for image in laser_images_01]
        laser_images_02 = [cv2.resize(image, (W, H)) for image in laser_images_02]

        # Grid_H, Grid_W, Image_H, Image_W, 3
        laser_images_01 = np.transpose(np.reshape(laser_images_01, (5, 5, H, W, 3)), (1, 0, 2, 3, 4))
        laser_images_02 = np.transpose(np.reshape(laser_images_02, (5, 5, H, W, 3)), (1, 0, 2, 3, 4))

        laser_images = np.stack([laser_images_01, laser_images_02], axis=0)

        '''
        Read RGB & Depth Images and Dection Annotions for GT
        '''

        rgb_image = cv2.imread(os.path.join(data_folder, "gt_rgb_image.png"))
        depth_image = cv2.imread(os.path.join(data_folder, "gt_depth_gray_image.png"), cv2.IMREAD_GRAYSCALE)

        laser_images = ((np.array(laser_images, dtype=np.float32) / 255.0) - 0.5) * 2.0
        rgb_image = np.array(rgb_image, dtype=np.float32) / 255.0
        depth_image = np.array(depth_image, dtype=np.float32) / 255.0

        detection_gt = np.zeros(dtype=np.float32, shape=(2, 6))
        rgb_h, rgb_w, _ = rgb_image.shape
        depth_h, depth_w = depth_image.shape
        gt_annos = self.dataset.detection_meta_dict[os.path.basename(data_folder)]
        for a_i, anno in enumerate(gt_annos):
            bbox = anno["bbox"]
            bbox = [bbox[0] / rgb_w, bbox[1] / rgb_h,
                    bbox[0] / rgb_w + bbox[2] / rgb_w,
                    bbox[1] / rgb_h + bbox[3] / rgb_h]
            class_id = float(anno["category_id"]) - 1.0
            detection_gt[a_i] = np.array([1.0] + bbox + [class_id], dtype=np.float32)

            ratio = 0.1
            t_l = [np.minimum(bbox[0] * depth_w * (1.0 - ratio), depth_w),
                   np.minimum(bbox[1] * depth_h * (1.0 - ratio), depth_h)]
            t_l = np.array(np.round(t_l), dtype=np.int32)
            b_r = [np.minimum(bbox[2] * depth_w * (1.0 + ratio), depth_w),
                   np.minimum(bbox[3] * depth_h * (1.0 + ratio), depth_h)]
            b_r = np.array(np.round(b_r), dtype=np.int32)

        return laser_images, rgb_image, depth_image, detection_gt


if __name__ == "__main__":
    dataset_config = dict()
    # original laser input full size: 1936 x 1216
    dataset_config["laser_size"] = (64, 128)  # W, H
    dataset_config["rgb_size"] = (1280, 720)  # W, H
    dataset_config["depth_size"] = (1280, 720)  # W, H

    dataset_config["num_classes"] = 3
    dataset_config["class_labels"] = ("Person", "Fire Extinguisher", "Dog")
    dataset_config["class_colors"] = ((0, 255, 0), (0, 0, 255), (255, 0, 0))

    dataset_config["dataset_folder"] = os.path.join("/mnt/hdd1/nlos/aligned")

    # dataset_type = {"training", "validation"}
    dataset = NlosDataset(dataset_config, dataset_type="training")