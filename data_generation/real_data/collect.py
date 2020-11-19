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
import numpy as np


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
        # current_datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.data_folder = os.path.join(dst_folder)
        try:
            os.mkdir(self.data_folder)
        except OSError:
            pass

    def collect(self):

        whole_time = 0.0
        data_count = self.config["turtlebot_config"]["initial_index"]
        turtlebot_done = False

        # avg_image_paths = [os.path.join(self.data_folder, "initialization",
        #                                 "Avg_X{:02d}_Y{:02d}_C{:02d}.png".format(x + 1, y + 1, c + 1))
        #                    for x in range(self.config["galvanometer_config"]["num_grid"])
        #                    for y in range(self.config["galvanometer_config"]["num_grid"])
        #                    for c in range(len(self.config["cmos_config"]["cam_ids"]))]
        # exist_flags = [os.path.exists(path) for path in avg_image_paths]
        # if False not in exist_flags:
        #     self.avg_images = list()
        #     for x in range(self.config["galvanometer_config"]["num_grid"]):
        #         for y in range(self.config["galvanometer_config"]["num_grid"]):
        #             images = list()
        #             for c in range(len(self.config["cmos_config"]["cam_ids"])):
        #                 path = os.path.join(self.data_folder, "initialization",
        #                                     "Avg_X{:02d}_Y{:02d}_C{:02d}.png".format(x + 1, y + 1, c + 1))
        #                 image = cv2.imread(path)
        #                 images.append(image)
        #             self.avg_images.append(images)
        #     self.avg_images = np.array(self.avg_images)
        # else:
        #     print("Initialization ...")
        #     self.initialize()

        while not turtlebot_done:
            start_time = time.time()
            ###
            ### Set light for gt
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for ground truth".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                1, "Light"))
            self.laser.turn_off()
            self.light.light_for_gt()

            ###
            ### Move the object to a point
            ###

            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Move".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                2, "Turtlebot"))
            turtlebot_done, turtlebot_position = self.turtlebot.step()

            ###
            ### Get gt rgb image
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT rgb image".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                3, "Depth"))
            # gt_rgb_image = self.cmos.get_gt_image()
            gt_rgb_image = self.depth.get_rgb()

            ###
            ### Get gt depth image
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT depth image".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                4, "Depth"))
            gt_depth_image = self.depth.get_depth_image()

            ###
            ### Get 2D object detection bboxes
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT detection bboxes".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                5, "Detector"))
            gt_bboxes = self.detector.detect(gt_rgb_image)

            ###
            ### Set light for laser
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                6, "Light"))
            self.light.light_for_laser()

            ###
            ### Turn on laser
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn on the laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                7, "Laser"))
            self.laser.turn_on()

            ###
            ### Step on galvanometer for grid scanning
            ###
            galvanometer_done = False
            reflection_items = list()
            while not galvanometer_done:
                galvanometer_done, galvanometer_position = self.galvanometer.step()
                print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Move mirrors".format(
                    data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                    8, "Galvanometer", self.galvanometer.count, self.galvanometer.num_grid ** 2, ))

                # get reflection image
                print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Get reflection rgb images".format(
                    data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                    9, "CMOS", self.galvanometer.count, self.galvanometer.num_grid ** 2, ))
                reflection_images = self.cmos.get_reflection_images()
                # diff_images = np.array(reflection_images, dtype=np.float32) - \
                #               np.array(self.avg_images[
                #                            galvanometer_position[0] //
                #                            self.config["galvanometer_config"]["num_grid"] +
                #                            galvanometer_position[1] %
                #                            self.config["galvanometer_config"]["num_grid"]], dtype=np.float32)
                # # diff_images -= np.min(diff_images, axis=(2, 3), keepdims=True)
                # diff_images_01 = np.abs(np.array(diff_images))
                # diff_images_02 = np.array(np.array(diff_images)) - \
                #                  np.min(np.array(diff_images), axis=(2, 3), keepdims=True)
                # diff_images_03 = np.array(np.array(diff_images)) + 255.0
                # # diff_images += 255.0
                # diff_images_01 = diff_images_01 / np.max(diff_images_01, axis=(2, 3), keepdims=True)
                # diff_images_02 = diff_images_02 / np.max(diff_images_02, axis=(2, 3), keepdims=True)
                # diff_images_03 = diff_images_03 / (255.0 * 2)
                # # diff_images /= (255.0 * 2)
                # diff_images_01 = np.array(np.clip(diff_images_01 * 255.0, 0.0, 255.0), dtype=np.uint8)
                # diff_images_02 = np.array(np.clip(diff_images_02 * 255.0, 0.0, 255.0), dtype=np.uint8)
                # diff_images_03 = np.array(np.clip(diff_images_03 * 255.0, 0.0, 255.0), dtype=np.uint8)
                reflection_items.append([galvanometer_position, reflection_images,
                                         # diff_images_01, diff_images_02, diff_images_03
                                         ])

            ###
            ### Turn off laser
            ###
            print("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn off the laser".format(
                data_count + 1, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                10, "Laser"))
            self.laser.turn_off()

            ###
            ### save data
            ###
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
                # diff_images_01 = items[2]
                # diff_images_02 = items[3]
                # diff_images_03 = items[4]
                for cmos_index, reflection_image in enumerate(reflection_images):
                    reflection_image_path = \
                        os.path.join(this_data_folder, "reflection_image_Gx{:02d}_Gy{:02d}_C{:02d}.png".format(
                            galvanometer_position[0] + 1, galvanometer_position[1] + 1, cmos_index + 1))
                    cv2.imwrite(reflection_image_path, reflection_image)

                # for cmos_index, diff_image in enumerate(diff_images_01):
                #     diff_image_path = \
                #         os.path.join(this_data_folder, "diff_image_Gx{:02d}_Gy{:02d}_C{:02d}_abs.png".format(
                #             galvanometer_position[0] + 1, galvanometer_position[1] + 1, cmos_index + 1))
                #     cv2.imwrite(diff_image_path, diff_image)
                #
                # for cmos_index, diff_image in enumerate(diff_images_02):
                #     diff_image_path = \
                #         os.path.join(this_data_folder, "diff_image_Gx{:02d}_Gy{:02d}_C{:02d}_max.png".format(
                #             galvanometer_position[0] + 1, galvanometer_position[1] + 1, cmos_index + 1))
                #     cv2.imwrite(diff_image_path, diff_image)
                #
                # for cmos_index, diff_image in enumerate(diff_images_03):
                #     diff_image_path = \
                #         os.path.join(this_data_folder, "diff_image_Gx{:02d}_Gy{:02d}_C{:02d}_normal.png".format(
                #             galvanometer_position[0] + 1, galvanometer_position[1] + 1, cmos_index + 1))
                #     cv2.imwrite(diff_image_path, diff_image)

            data_json = dict()
            data_json["object_type"] = self.config["data_config"]["object_type"]
            data_json["gt_brightness"] = self.config["light_config"]["gt_brightness"]
            data_json["gt_bboxes"] = gt_bboxes
            data_json["turtlebot_position"] = turtlebot_position
            data_json_path = os.path.join(this_data_folder, "gt_data.json")

            with open(data_json_path, "w") as fp:
                json.dump(data_json, fp, indent=4, sort_keys=True)
            data_count += 1
            whole_time += time.time() - start_time
            print("T{:4d}/{:4d}|Average Iteration Time: {:.5f} seconds".format(
                data_count, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
                whole_time / data_count))

    def initialize(self):
        dir = os.path.join(self.data_folder, "initialization")
        try:
            os.mkdir(dir)
        except OSError:
            pass
        self.laser.turn_on()
        self.light.light_for_laser()
        cmos = CMOS(config=self.config["cmos_config"])

        # init turtlebot
        turtlebot = Turtlebot(config=self.config["turtlebot_config"])

        # init galvanometer
        galvanometer = Galvanometer(config=self.config["galvanometer_config"])

        import nidaqmx
        task = nidaqmx.Task()
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1")

        # move turtlebot to the outside of RoI
        print("Move turtlebot outside")
        x, y, a = 2.5, 0.0, 0.0
        turtlebot.command(x, y, a)

        # scan with galvanometer for average images
        done = False
        self.avg_images = list()
        while not done:
            done, position = galvanometer.step()
            print("Take average images X{:2d}/{:2d} Y{:2d}/{:2d}".format(
                position[0] + 1, self.config["galvanometer_config"]["num_grid"],
                position[1] + 1, self.config["galvanometer_config"]["num_grid"]
            ))
            images = np.array(cmos.get_reflection_images(), dtype=np.float32)
            for _ in range(3):
                images += np.array(cmos.get_reflection_images(), dtype=np.float32)
            images /= float(3.0)
            images = np.array(np.clip(images, 0.0, 255.0), dtype=np.uint8)
            self.avg_images.append(images)
            for i, image in enumerate(images):
                image_name = "Avg_X{:02d}_Y{:02d}_C{:02d}.png".format(position[0] + 1, position[1] + 1, i + 1)
                image_path = os.path.join(dir, image_name)
                cv2.imwrite(image_path, image)

        # move turtlebot to the outside of RoI
        print("Move turtlebot to the initial point")
        x, y, a = 0.6, -0.6, 0.0
        turtlebot.command(x, y, a)
        self.laser.turn_off()
        self.light.light_for_gt()
