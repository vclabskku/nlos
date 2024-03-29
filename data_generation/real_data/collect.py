from data_generation.real_data.light.light import Light
from data_generation.real_data.turtlebot.turtlebot import Turtlebot
from data_generation.real_data.cmos.cmos import CMOS
from data_generation.real_data.depth.depth import Depth
from data_generation.real_data.detector.detector import Detector
from data_generation.real_data.laser.laser import Laser
from data_generation.real_data.galvanometer.galvanometer import Galvanometer
from data_generation.real_data.client.client import Client

#from data_generation.real_data.sound.Echo import Echo
#from data_generation.real_data.sound.Arduino import Arduino

import cv2
import os
import time
import json
import numpy as np
import paramiko
from multiprocessing import Process, Manager
from subprocess import Popen, PIPE
import logging

class Collector():

    def __init__(self, config):

        self.config = config

        self.processes_list = self.initialize_roscore_set()
        print('initialize_finish')

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
        self.log_folder = self.config["data_config"]["log_folder"]
        try:
            os.mkdir(self.data_folder)
        except OSError:
            pass

        if self.config["sensor_config"]["use_rf"] or self.config["sensor_config"]["use_sound"]:
            self.client = Client(self.config['server']['ip'], self.config['server']['port'], self.data_folder)

        self.set_logger()

    def set_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(self.log_folder + f'/main_computer_{time.strftime("%m%d-%H%M")}.log')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logging.info(f"LOG DIR SET :{self.log_folder}")

    def execute(self, command):
        process = Popen(command, stdout=PIPE, shell=True)
        while True:
            line = process.stdout.readline().rstrip()
            if not line:
                continue
            yield line

    def initialize_roscore(self, turtlebot_num, manager):
        for path in self.execute(self.config["roscore"][turtlebot_num]["terminal_1"]["operation"]):
            print(path.decode('utf-8'))
            if "started core service [/rosout]" in path.decode('utf-8'):
                manager[0] = True

    def initialize_turtlebot(self, turtlebot_num, manager):
        retries = 10
        turtlebot = paramiko.SSHClient()
        turtlebot.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        for x in range(retries):
            try:
                turtlebot.connect(self.config["turtlebot_config"][turtlebot_num]["ip"], port='22',
                                  username=self.config["turtlebot_config"][turtlebot_num]["username"],
                                  password=self.config["turtlebot_config"][turtlebot_num]["password"],
                                  timeout=5)
                break
            except:
                pass

        for x in range(retries):
            try:
                stdin, stdout, stderr = turtlebot.exec_command(
                    self.config["turtlebot_config"][turtlebot_num]["roslanuch"], get_pty=True)
                for line in iter(stdout.readline, ""):
                    print(line, end="")
                    if 'Calibration End' in line:
                        manager[1] = True
                break
            except:
                pass

    def initialize_map(self, turtlebot_num, manager):
        for path in self.execute(self.config["roscore"][turtlebot_num]["terminal_2"]["operation"]):
            print(path.decode('utf-8'))
            if "process[rviz-5]: started with pid" in path.decode('utf-8'):
                manager[2] = True

    def initialize_roscore_set(self):
        manager_list = []
        for _ in self.config["turtlebot_config"]["using_list"]:
            manager_list.append(Manager().list([False, False, False]))
        process_list = []
        for i in self.config["turtlebot_config"]["using_list"]:
            manager = Manager().list([False, False, False])

            roscore = Process(target=self.initialize_roscore, args=(i, manager))
            turtlebot = Process(target=self.initialize_turtlebot, args=(i, manager))
            map = Process(target=self.initialize_map, args=(i, manager))

            roscore.start()
            while (True):
                time.sleep(0.2)
                if manager[0] == True:
                    break
            turtlebot.start()
            while (True):
                time.sleep(0.2)
                if manager[1] == True:
                    break
            map.start()
            while (True):
                time.sleep(0.2)
                if manager[2] == True:
                    break

            process_list.append(roscore)
            process_list.append(turtlebot)
            process_list.append(map)
        return process_list

    def collect(self):
        whole_time = 0.0
        time_count = 0
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

        if self.config["sensor_config"]["use_laser"]:
            self.laser.turn_off()
        self.light.light_for_gt()
        while not turtlebot_done:
            start_time = time.time()
            task_index = 1
            ###
            ### Set light for gt
            ###
            if self.config["sensor_config"]["use_laser"]:
                turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                       for l_i, t_i in enumerate(self.turtlebot.indices)])
                logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for ground truth".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                    task_index, "Light"))
                self.light.light_for_gt()
                task_index += 1

            ###
            ### Move the object to a point
            ###
            turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                   for l_i, t_i in enumerate(self.turtlebot.indices)])
            logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Move".format(
                turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                task_index, "Turtlebot"))
            turtlebot_done, turtlebot_position = self.turtlebot.step()
            task_index += 1

            ###
            ### Get gt rgb & depth images
            ###
            turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                   for l_i, t_i in enumerate(self.turtlebot.indices)])
            logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Get GT rgb image".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                task_index, "Depth"))
            gt_rgb_image, gt_depth_gray_image, gt_depth_color_image = self.depth.get_aligned_images()
            task_index += 1

            ###
            ### Get 2D object detection bboxes
            ###
            # logging.info("T{}/{:4d}|S{:2d}:{:12s}|Get GT detection bboxes".format(
            #     self.turtlebot.indices, self.turtlebot.l_x * self.turtlebot.l_y * self.turtlebot.l_a,
            #     5, "Detector"))
            # gt_bboxes = self.detector.detect(gt_rgb_image)

            ###
            ### Set light for laser
            ###
            if self.config["sensor_config"]["use_laser"]:
                turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                       for l_i, t_i in enumerate(self.turtlebot.indices)])
                logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Set light for laser".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                    task_index, "Light"))
                self.light.light_for_laser()
                task_index += 1

            ###
            ### Turn on laser
            ###
            if self.config["sensor_config"]["use_laser"]:
                turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                       for l_i, t_i in enumerate(self.turtlebot.indices)])
                logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn on the laser".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                task_index, "Laser"))
                self.laser.turn_on()
                task_index += 1

            ###
            ### Step on galvanometer for grid scanning
            ###
            if self.config["sensor_config"]["use_laser"]:
                galvanometer_done = False
                reflection_items = list()
                turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                       for l_i, t_i in enumerate(self.turtlebot.indices)])
                while not galvanometer_done:
                    galvanometer_done, galvanometer_position = self.galvanometer.step()
                    print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Move mirrors".format(
                        turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                        task_index, "Galvanometer", self.galvanometer.count, self.galvanometer.num_grid ** 2, ))

                    # get reflection image
                    print("T{:4d}/{:4d}|S{:2d}:{:12s}|G{:2d}/{:2d}:Get reflection rgb images".format(
                        turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                        task_index, "CMOS", self.galvanometer.count, self.galvanometer.num_grid ** 2, ))

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
                task_index += 1

            ###
            ### Turn off laser
            ###
            if self.config["sensor_config"]["use_laser"]:
                turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                       for l_i, t_i in enumerate(self.turtlebot.indices)])
                logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Turn off the laser".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                    task_index, "Laser"))
                self.laser.turn_off()
                task_index += 1

            ###
            ### save data
            ###
            turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                   for l_i, t_i in enumerate(self.turtlebot.indices)])
            logging.info("T{:4d}/{:4d}|S{:2d}:{:12s}|Save the data".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                task_index, "Data"))
            # indices_str = "_".join(["{:08d}".format(index) for index in self.turtlebot.indices])
            this_data_folder = os.path.join(self.data_folder, "D{:08d}".format(turtlebot_index))
            try:
                os.mkdir(this_data_folder)
            except OSError:
                pass
            task_index += 1

            gt_rgb_image_path = os.path.join(this_data_folder, "gt_rgb_image.png")
            cv2.imwrite(gt_rgb_image_path, gt_rgb_image)

            gt_depth_gray_image_path = os.path.join(this_data_folder, "gt_depth_gray_image.png")
            cv2.imwrite(gt_depth_gray_image_path, gt_depth_gray_image)

            gt_depth_color_image_path = os.path.join(this_data_folder, "gt_depth_color_image.png")
            cv2.imwrite(gt_depth_color_image_path, gt_depth_color_image)

            if self.config["sensor_config"]["use_laser"]:
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


            '''
                rf 및 음장 데이서 수집 명령 전송
            '''
            parent_folder = os.path.basename(self.data_folder)
            child_folder = os.path.basename(this_data_folder)

            if self.config["sensor_config"]["use_rf"]:
                logging.info("sending RF command")
                recvData = self.client.send_command(f'rf-{parent_folder}/{child_folder}')
                logging.info("recieved from RF operation >> {}".format(recvData))

            if self.config["sensor_config"]["use_sound"]:
                logging.info("sending WAVE command")
                recvData = self.client.send_command(f'wave-{parent_folder}/{child_folder}')
                logging.info("recieved from WAVE operation >>  {}".format(recvData))

            """
                rf 및 음장 끝
            """

            data_json = dict()
            data_json["gt_brightness"] = self.config["light_config"]["gt_brightness"]
            # data_json["gt_bboxes"] = gt_bboxes
            data_json["turtlebot_position"] = turtlebot_position
            data_json_path = os.path.join(this_data_folder, "gt_data.json")

            with open(data_json_path, "w") as fp:
                json.dump(data_json, fp, indent=4, sort_keys=True)
            time_count += 1
            whole_time += time.time() - start_time
            turtlebot_index = sum([t_i * (self.turtlebot.l ** l_i)
                                   for l_i, t_i in enumerate(self.turtlebot.indices)])
            print("T{:4d}/{:4d}|Average Iteration Time: {:.5f} seconds".format(
                    turtlebot_index, self.turtlebot.l ** len(self.turtlebot.indices),
                whole_time / time_count))

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
        logging.info("Move turtlebot outside")
        x, y, a = 2.5, 0.0, 0.0
        # turtlebot.command(x, y, a)

        # scan with galvanometer for average images
        done = False
        self.avg_images = list()
        while not done:
            done, position = galvanometer.step()
            logging.info("Take average images X{:2d}/{:2d} Y{:2d}/{:2d}".format(
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
        logging.info("Move turtlebot to the initial point")
        x, y, a = 0.6, -0.6, 0.0
        # turtlebot.command(x, y, a)
        self.laser.turn_off()
        self.light.light_for_gt()
