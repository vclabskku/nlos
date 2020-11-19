import os
from glob import glob
from shutil import copyfile
from ..data_generation.real_data.detector.detector import Detector

import cv2

#src_folder = "d:\\human_03"
src_folder = "/media/pjh3974/dataset/nlos/*"
#dst_folder = "d:\\nlosGTImage"
dst_folder = "/media/pjh3974/dataset/nlosGTImage"
start_id = 0

config = dict()
#config["detectron_root"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
config["detectron_root"] = "/home/appuser/detectron2_repo"
config["config_file"] = "configs/novel/retinanet_R_50_FPN_1x.yaml"
#config["check_point"] = "output/novel/model_0004999.pth"
config["check_point"] = "output/novel/retinanet_R_50_FPN_1x/model_0004999.pth"

nlosGTDetector = Detector(config)

for image_dir in glob(src_folder):
    #copy gt image to dst folder
    src_rgb_image_path = os.path.join(image_dir, 'gt_rgb_image.png')
    image_id = src_rgb_image_path.split('/')[-2]
    dst_rgb_image_path = os.path.join(dst_folder,image_id+'.png')
    copyfile(src_rgb_image_path, dst_rgb_image_path)

    #save detection result to xml format
    nlosGTDetector.extractResult(
        image=cv2.imread(dst_rgb_image_path), 
        output=dst_folder,
        path=dst_rgb_image_path)