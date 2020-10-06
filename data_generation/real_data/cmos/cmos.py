
import numpy as np

class CMOS():

    def __init__(self, config):

        self.config = config

    def get_gt_image(self):

        image = np.zeros(dtype=np.uint8, shape=(224, 224, 3))

        return image

    def get_reflection_images(self):

        # get images from multiple cameras
        images = [np.zeros(dtype=np.uint8, shape=(224, 224, 3)), np.zeros(dtype=np.uint8, shape=(224, 224, 3))]

        return images