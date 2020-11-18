import os
from glob import glob
from shutil import copyfile

#src_folder = "d:\\human_03"
src_folder = "/media/pjh3974/dataset/nlos/*"
#dst_folder = "d:\\nlosGTImage"
dst_folder = "/media/pjh3974/dataset/nlosGTImage"
start_id = 0

for image_dir in glob(src_folder):
    src_rgb_image_path = os.path.join(image_dir, 'gt_rgb_image.png')
    image_id = src_rgb_image_path.split('/')[-2]
    dst_rgb_image_path = os.path.join(dst_folder,image_id+'.png')
    copyfile(src_rgb_image_path, dst_rgb_image_path)
