import detectron2
import os
from detectron2.utils.logger import setup_logger

setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random

# import some common detectron2 utilities
from data_generation.real_data.detectron2 import model_zoo
from data_generation.real_data.detectron2.engine import DefaultPredictor
from data_generation.real_data.detectron2.config import get_cfg
from data_generation.real_data.detectron2.utils.visualizer import Visualizer
from data_generation.real_data.detectron2.data import MetadataCatalog, DatasetCatalog


class Detector():

    def __init__(self, config):
        self.config = config
        self.detector_cfg = get_cfg()
        # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
        self.detector_cfg.merge_from_file(
            os.path.join(config["DETECTOR"]["DETECTRON_ROOT"], config["DETECTOR"]["CONFIG_FILE"]))
        self.detector_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
        self.detector_cfg.MODEL.WEIGHTS = os.path.join(config["DETECTOR"]["DETECTRON_ROOT"],
                                                       config["DETECTOR"]["CHECK_POINT"])
        self.predictor = DefaultPredictor(self.detector_cfg)

    def detect(self, image):
        outputs = self.predictor(image)
        print(outputs)

        return outputs


if __name__ == '__main__':
    import cv2

    im = cv2.imread('..\\cmos\\frame_2.jpg')
    config = dict()
    # config for detector
    config["DETECTOR"] = dict()
    config["DETECTOR"]["DETECTRON_ROOT"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
    config["DETECTOR"]["CONFIG_FILE"] = "configs\\novel\\retinanet_R_50_FPN_1x.yaml"
    config["DETECTOR"]["CHECK_POINT"] = "output\\novel\\model_0004999.pth"
    do = Detector(config)
    outputs = do.detect(im)
    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(do.detector_cfg.DATASETS.TRAIN[0]), scale=1.2)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2.imwrite('output.png', out.get_image()[:, :, ::-1])
