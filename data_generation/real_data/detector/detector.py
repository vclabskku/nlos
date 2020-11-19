import detectron2
import os
from detectron2.utils.logger import setup_logger

setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
import sys

# import some common detectron2 utilities
# from data_generation.real_data.detectron2 import model_zoo
sys.path.append("C:\\Users\\vclab\\PycharmProjects\\detectron2")
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.data.generator import pascalVOCGenerator


class Detector():

    def __init__(self, config):
        self.config = config
        self.detector_cfg = get_cfg()
        # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
        self.detector_cfg.merge_from_file(
            os.path.join(config["detectron_root"], config["config_file"]))
        self.detector_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
        self.detector_cfg.MODEL.WEIGHTS = os.path.join(config["detectron_root"],
                                                       config["check_point"])
        self.predictor = DefaultPredictor(self.detector_cfg)
        self.dataset_generator = pascalVOCGenerator(self.detector_cfg)

    def detect(self, image):

        outputs = self.predictor(image)
        instances = outputs["instances"]
        boxes = instances.pred_boxes.tensor.detach().cpu().numpy()
        scores = instances.scores.detach().cpu().numpy()
        classes = instances.pred_classes.detach().cpu().numpy()

        results = np.concatenate([boxes,
                                  np.expand_dims(scores, axis=-1),
                                  np.expand_dims(classes, axis=-1)], axis=-1)
        results = np.array(results, dtype=np.float32).tolist()


        return results
    

    def extractResult(self, image, output, path):
        results = self.predictor(image)
        out_filename = os.path.join(output, os.path.basename(path))
        out_predname = os.path.join(output, (os.path.splitext(os.path.basename(path))[0] + '.xml'))
        self.dataset_generator.genFromPred(results, out_predname, out_filename)

if __name__ == '__main__':
    import cv2

    im = cv2.imread('image.jpg')
    config = dict()
    # config for detector
    config["detector_config"] = dict()
    config["detector_config"]["detectron_root"] = "C:\\Users\\vclab\\PycharmProjects\\detectron2"
    config["detector_config"]["config_file"] = "configs/novel/retinanet_R_50_FPN_1x.yaml"
    config["detector_config"]["check_point"] = "output/novel/model_0004999.pth"
    do = Detector(config["detector_config"])
    outputs = do.detect(im)
    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(do.detector_cfg.DATASETS.TRAIN[0]), scale=1.2)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2.imwrite('output.png', out.get_image()[:, :, ::-1])
