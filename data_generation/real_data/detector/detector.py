import detectron2
import os
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
 
# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

class Detector():

    def __init__(self, config):

        self.config = config
        self.detector_cfg = get_cfg()
        # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
        self.detector_cfg.merge_from_file(os.path.join(config.DETECTOR.DETECTRON_ROOT,config.DETECTOR.CONFIG_FILE))
        self.detector_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
        self.detector_cfg.MODEL.WEIGHTS = os.path.join(config.DETECTOR.DETECTRON_ROOT, config.DETECTOR.CHECK_POINT)
        self.predictor = DefaultPredictor(self.detector_cfg)


    def detect(self, image):
        
        outputs = predictor(image)
        outputs["instances"].pred_boxes = outputs["instances"].pred_boxes.tensor()

        return outputs