import os
from glob import glob
from shutil import copyfile
from ..data_generation.real_data.detector.detector import Detector

import cv2

#set options here

src_dir = "d:\\human_01"
dst_dir = "d:\\nlosGTImage\\human_01"
start_id = 142

#src_dir = "/media/pjh3974/dataset/nlos/*"
#dst_dir = "/media/pjh3974/dataset/nlosGTImage"


# config for detector
config = dict()
config["detectron_root"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
#config["detectron_root"] = "/home/appuser/detectron2_repo"
config["config_file"] = "configs/novel/retinanet_R_50_FPN_1x.yaml"
config["check_point"] = "output/novel/model_0004999.pth"
#config["check_point"] = "output/novel/retinanet_R_50_FPN_1x/model_0004999.pth"

nlosGTDetector = Detector(config)

for image_id in os.listdir(src_dir):
    #copy gt image to dst dir
    if int(image_id[1:]) < start_id:
        continue
    src_rgb_image_path = os.path.join(src_dir,image_id, 'gt_rgb_image.png')
    dst_rgb_image_path = os.path.join(dst_dir,image_id+'.png')
    copyfile(src_rgb_image_path, dst_rgb_image_path)

    #save detection result to xml format
    nlosGTDetector.extractResult(
        image=cv2.imread(dst_rgb_image_path), 
        output=dst_dir,
        path=dst_rgb_image_path)