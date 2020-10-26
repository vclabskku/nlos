
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
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for ground truth".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                1, "Light"))
            self.light.light_for_gt()

            # move the object to a point

            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Move".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                2, "Turtlebot"))
            turtlebot_done, turtlebot_position = self.turtlebot.move()

            # get gt rgb image
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT rgb image".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                3, "Depth"))
            # gt_rgb_image = self.cmos.get_gt_image()
            gt_rgb_image = self.depth.get_rgb()

            # get gt depth image
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT depth image".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                4, "Depth"))
            gt_depth_image = self.depth.get_depth_image()

            # get 2D object detection bboxes
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT detection bboxes".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                5, "Detector"))
            gt_bboxes = self.detector.detect(gt_rgb_image)

            # set light for laser
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                6, "Light"))
            self.light.light_for_laser()

            # turn on laser
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn on the laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                7, "Laser"))
            self.laser.turn_on()

            # step on galvanometer for grid scanning
            galvanometer_done = False
            reflection_items = list()
            while not galvanometer_done:
                print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Move mirrors".format(
                    data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                    8, "Galvanometer", self.galvanometer.count + 1, self.galvanometer.num_grid ** 2,))
                galvanometer_done, galvanometer_position = self.galvanometer.step()

                # get reflection image
                print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Get reflection rgb images".format(
                    data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                    9, "CMOS", self.galvanometer.count + 1, self.galvanometer.num_grid ** 2,))
                reflection_images = self.cmos.get_reflection_images()
                reflection_items.append([galvanometer_position, reflection_images])

            # turn off laser
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn off the laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                10, "Laser"))
            self.laser.turn_off()

            # save data

            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Save the data".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                11, "Data"))
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
                            galvanometer_position[0] + 1, galvanometer_position[1] + 1, cmos_index + 1))
                    cv2.imwrite(reflection_image_path, reflection_image)

            data_json = dict()
            data_json["object_type"] = self.config["data_config"]["object_type"]
            data_json["gt_brightness"] = self.config["light_config"]["gt_brightness"]
            data_json["gt_bboxes"] = gt_bboxes
            data_json["turtlebot_position"] = turtlebot_position
            data_json_path = os.path.join(this_data_folder, "gt_data.json")

            with open(data_json_path, "w") as fp:
                json.dump(data_json, fp, indent=4, sort_keys=True)
            data_count += 1


