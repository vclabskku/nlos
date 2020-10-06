
from data_generation.real_data.light.light import Light
from data_generation.real_data.turtlebot.turtlebot import Turtlebot
from data_generation.real_data.cmos.cmos import CMOS
from data_generation.real_data.depth.depth import Depth
from data_generation.real_data.detector.detector import Detector
from data_generation.real_data.laser.laser import Laser
from data_generation.real_data.galvanometer.galvanometer import Galvanometer

import cv2
import os
import time
import json

class Collector():

    def __init__(self, config):

        self.config = config

        self.light = Light(self.config["light_config"])
        self.turtlebot = Turtlebot(self.config["turtlebot_config"])
        self.cmos = CMOS(self.config["cmos_config"])
        self.depth = Depth(self.config["depth_config"])
        self.detector = Detector(self.config["detector_config"])
        self.laser = Laser(self.config["laser_config"])
        self.galvanometer = Galvanometer(self.config["galvanometer_config"])

        dst_folder = self.config["data_config"]["dst_folder"]
        current_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.data_folder = os.path.join(dst_folder, current_datetime)
        try:
            os.mkdir(self.data_folder)
        except OSError:
            pass

    def collect(self):

        data_count = 0
        turtlebot_done = False

        while not turtlebot_done:
            # set light for gt
            self.light.light_for_gt()

            # move the object to a point
            turtlebot_done, turtlebot_position = self.turtlebot.move()

            # get gt rgb image
            gt_rgb_image = self.cmos.get_gt_image()

            # get gt depth image
            gt_depth_image = self.depth.get_depth_image()

            # get 2D object detection bboxes
            gt_bboxes = self.detector.detect(gt_rgb_image)

            # set light for laser
            self.light.light_for_laser()

            # turn on laser
            self.laser.turn_on()

            # step on galvanometer for grid scanning
            galvanometer_done = False
            reflection_items = list()
            while not galvanometer_done:
                galvanometer_done, galvanometer_position = self.galvanometer.step()

                # get reflection image
                reflection_images = self.cmos.get_reflection_images()
                reflection_items.append([galvanometer_position, reflection_images])

            # turn off laser
            self.laser.turn_off()

            # save data
            this_data_folder = os.path.join(self.data_folder, "D{:08d}".format(data_count + 1))
            try:
                os.mkdir(this_data_folder)
            except OSError:
                pass

            gt_rgb_image_path = os.path.join(this_data_folder, "gt_rgb_image.png")
            cv2.imwrite(gt_rgb_image_path, gt_rgb_image)

            gt_depth_image_path = os.path.join(this_data_folder, "gt_depth_image.png")
            cv2.imwrite(gt_depth_image_path, gt_depth_image)

            for galvanometer_index, items in enumerate(reflection_items):
                galvanometer_position = items[0]
                reflection_images = items[1]
                for cmos_index, reflection_image in enumerate(reflection_images):
                    reflection_image_path = \
                        os.path.join(this_data_folder, "reflection_image_Gx{:02d}_Gy{:02d}_C{:02d}.png".format(
                            galvanometer_position[0], galvanometer_position[1], cmos_index))
                    cv2.imwrite(reflection_image_path, reflection_image)

            data_json = dict()
            data_json["object_type"] = self.config["data_config"]["object_type"]
            data_json["gt_brightness"] = self.config["data_config"]["gt_brightness"]
            data_json["gt_bboxes"] = gt_bboxes
            data_json["turtlebot_position"] = turtlebot_position
            data_json_path = os.path.join(this_data_folder, "gt_data.json")

            with open(data_json_path, "w") as fp:
                json.dump(data_json, fp, indent=4, sort_keys=True)


