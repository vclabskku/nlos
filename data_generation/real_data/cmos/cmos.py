import cv2
from data_generation.real_data.cmos.vimba import *
import time
# from data_generation.real_data.cmos.vimba.c_binding import *
import numpy as np


# from typing import Optional

# class CMOS():
#
#     def __init__(self, config=None):
#
#         self.config = config
#         self.PIXEL_FORMATS_CONVERSIONS = {
#             'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
#             'PixelFormat.BayerRG8': cv2.COLOR_BAYER_RG2RGB
#         }
#
#         #### Camera ID #####
#         # DEV_000F310382ED (Reflection Low) #
#         # DEV_000F310382EC (GT)#
#         # DEV_000F310382EB (Reflection High #
#         ####################
#         self.camera_ids = self.config["cam_ids"]
#         self.iterations = self.config["iterations"]
#         self.exposure_time = self.config["exposure_time"]
#         self.timeout_time = self.config["timeout_time"]
#
#         # TODO: we have to initialize cams only ones here!
#         with Vimba.get_instance() as vimba:
#             for cam_id in self.camera_ids:
#                 try:
#                     with vimba.get_camera_by_id(cam_id) as cam:
#                         self.setup_camera(cam)
#                 except VimbaCameraError:
#                     print('Failed to access Camera {}. Abort.'.format(cam_id))
#
#     def setup_camera(self, cam: Camera):
#         # with cam:
#         # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
#         try:
#             cam.GVSPAdjustPacketSize.run()
#
#             while not cam.GVSPAdjustPacketSize.is_done():
#                 pass
#         except (AttributeError, VimbaFeatureError):
#             print("GVSP Adjust Packet Size Error!")
#             pass
#
#         exposure_time = cam.ExposureTimeAbs
#         # time = exposure_time.get()
#         # inc = exposure_time.get_increment()
#         # exposure_time.set(time + inc)
#         exposure_time.set(self.exposure_time)
#
#     def get_reflection_images(self):
#         ## cam_id array with 2 strings
#         frame_list = []
#
#         with Vimba.get_instance() as vimba:
#             # cams = vimba.get_all_cameras()
#             # count = len(cams)
#             #
#             # for i in range(count):
#             for cam_id in self.camera_ids:
#                 start_time = time.time()
#                 with vimba.get_camera_by_id(cam_id) as cam:
#                     self.setup_camera(cam)
#
#                     # for feature in cam.get_all_features():
#                     #     try:
#                     #         value = feature.get()
#                     #
#                     #     except (AttributeError, VimbaFeatureError):
#                     #         value = None
#                     #
#                     #     if "exposure" in feature.get_name().lower():
#                     #         print('/// Feature name   : {}'.format(feature.get_name()))
#                     #         print('/// Display name   : {}'.format(feature.get_display_name()))
#                     #         print('/// Tooltip        : {}'.format(feature.get_tooltip()))
#                     #         print('/// Description    : {}'.format(feature.get_description()))
#                     #         print('/// SFNC Namespace : {}'.format(feature.get_sfnc_namespace()))
#                     #         print('/// Unit           : {}'.format(feature.get_unit()))
#                     #         print('/// Value          : {}\n'.format(str(value)))
#                     while True:
#                         frame = cam.get_frame(self.timeout_time)
#                         if frame.get_status() == FrameStatus.Complete:
#                             frame.convert_pixel_format(PixelFormat.Bgr8)
#                             # frame.convert_pixel_format(PixelFormat.BayerBG16)
#                             frame = frame.as_numpy_ndarray()
#                             break
#                     # frame = frame[:530]
#                     frame_list.append(frame)
#                     end_time = time.time() - start_time
#                     print("taking a picture ... {:.5f} secs".format(end_time))
#
#         # for cam in self.cams:
#         #     while True:
#         #         frame = cam.get_frame(self.timeout_time)
#         #         if frame.get_status() == FrameStatus.Complete:
#         #             frame.convert_pixel_format(PixelFormat.Bgr8)
#         #             # frame.convert_pixel_format(PixelFormat.BayerBG16)
#         #             frame = frame.as_numpy_ndarray()
#         #             break
#         #     # frame = frame[:530]
#         #     frame_list.append(frame)
#
#         return frame_list

class CMOS():

    def __init__(self, config=None):

        self.config = config
        self.PIXEL_FORMATS_CONVERSIONS = {
            'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
            'PixelFormat.BayerRG8': cv2.COLOR_BAYER_RG2RGB
        }

        #### Camera ID #####
        # DEV_000F310382ED (Reflection Low) #
        # DEV_000F310382EC (GT)#
        # DEV_000F310382EB (Reflection High #
        ####################
        self.camera_ids = self.config["cam_ids"]
        self.iterations = self.config["iterations"]
        self.exposure_time = self.config["exposure_time"]
        self.timeout_time = self.config["timeout_time"]

        # TODO: we have to initialize cams only ones here!
        self.vimba = Vimba.get_instance()
        self.vimba.__enter__()
        self.cam_list = []
        for cam_id in self.camera_ids:
            self.cam = self.vimba.get_camera_by_id(cam_id)
            self.cam.__enter__()
            self.setup_camera(self.cam)
            self.cam_list.append(self.cam)

    def __del__(self):
        for i in range(len(self.camera_ids)):
            pass
        self.cam_list[i].__exit__(None, None, None)
        self.vimba.__exit__(None, None, None)

    def setup_camera(self, cam: Camera):
        # with cam:
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.GVSPAdjustPacketSize.run()

            while not cam.GVSPAdjustPacketSize.is_done():
                pass
        except (AttributeError, VimbaFeatureError):
            print("GVSP Adjust Packet Size Error!")
            pass

        exposure_time = cam.ExposureTimeAbs
        # time = exposure_time.get()
        # inc = exposure_time.get_increment()
        # exposure_time.set(time + inc)
        exposure_time.set(self.exposure_time)

    def get_reflection_images(self):
        frame_list = []

        for i in range(len(self.camera_ids)):
            start_time = time.time()
            while True:
                try:
                    frame = self.cam_list[i].get_frame(self.timeout_time)
                except:
                    continue

                if frame.get_status() == FrameStatus.Complete:
                    frame.convert_pixel_format(PixelFormat.Bgr8)
                    frame = frame.as_numpy_ndarray()
                    break
            frame_list.append(frame)
            end_time = time.time() - start_time
            # print("taking a picture ... {:.5f} secs".format(end_time))

        return frame_list


if __name__ == "__main__":
    ###
    ### basic example
    ###
    config = dict()
    config["cmos_config"] = dict()
    config["cmos_config"]["cam_ids"] = ["DEV_000F310382EB", "DEV_000F310382ED"]
    config["cmos_config"]["iterations"] = 3
    config["cmos_config"]["exposure_time"] = 5.0e+5  # micro seconds
    config["cmos_config"]["timeout_time"] = int(5.0e+3)  # milli seconds

    cmos = CMOS(config=config["cmos_config"])
    image_list = cmos.get_reflection_images()
    for i in range(len(image_list)):
        image = image_list[i]
        cv2.imwrite("image_%d.jpg" % i, image)


    ###
    ### galvanometer setting
    ###
    # import os
    # import numpy as np
    # import sys
    #
    # print(os.path.abspath(".."))
    # sys.path.append(os.path.join(os.path.abspath(".."), "turtlebot"))
    # from turtlebot import Turtlebot
    #
    # # from ..galvanometer import Galvanometer
    # dir = os.path.join("c:\\users\\vclab\\Desktop", "galvanometer_setting2")
    # try:
    #     os.mkdir(dir)
    # except OSError:
    #     pass
    # cmos = CMOS()
    #
    # # init turtlebot
    # config = dict()
    # config["area_range"] = [[0.9, 0.0], [2.0, -2.0]]
    # config["angle_range"] = [0.0, 180.0]
    # config["spatial_step"] = 0.1
    # config["angle_step"] = 20.0
    # turtlebot = Turtlebot(config=config)
    #
    # # # init galvanometer
    # # # config = dict()
    # # # config["num_grid"] = 10
    # # # config["voltage_range"] = [-10.0, 10.0]
    # # # galvanometer = Galvanometer(config=config)
    # #
    # # import nidaqmx
    # # task = nidaqmx.Task()
    # # task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
    # # task.ao_channels.add_ao_voltage_chan("Dev1/ao1")
    # # voltages = [[-1.8, -4.0], [-1.8, 0.0], [-1.8, 4.0], [0.0, 0.0], [4.0, -4.0], [4.0, 0.0], [4.0, 4.0]]
    # # # voltages = [[-1.8, 0.0]]
    # #
    # # # move turtlebot to the outside of RoI
    # # x, y, a = 2.3, -0.6, 0.0
    # # turtlebot.command(x, y, a)
    # #
    # # # scan with galvanometer for average images
    # # done = False
    # # avg_images = list()
    # # for v_i, voltage_pair in enumerate(voltages):
    # # # while not done:
    # # #     done, position = galvanometer.step()
    # #     task.write([voltage_pair[0], voltage_pair[1]], auto_start=True)
    # #     images = np.array(cmos.get_reflection_images(), dtype=np.float32)
    # #     for _ in range(2):
    # #         images += np.array(cmos.get_reflection_images(), dtype=np.float32)
    # #     images /= float(10.0)
    # #     images = np.array(np.clip(images, 0.0, 255.0), dtype=np.uint8)
    # #     avg_images.append(images)
    # #     for i, image in enumerate(images):
    # #         image_name = "Avg_G{:02d}_C{:02d}.png".format(v_i + 1, i + 1)
    # #         image_path = os.path.join(dir, image_name)
    # #         cv2.imwrite(image_path, image)
    # #
    # # # init galvanometer
    # # # galvanometer = Galvanometer(config=config)
    # #
    # # # move turtlebot to the outside of RoI
    # # x, y, a = 0.6, -0.6, 0.0
    # # turtlebot.command(x, y, a)
    #
    # # # scan with galvanometer for object images
    # # done = False
    # # obj_images = list()
    # # for v_i, voltage_pair in enumerate(voltages):
    # #     # while not done:
    # #     #     done, position = galvanometer.step()
    # #     task.write([voltage_pair[0], voltage_pair[1]], auto_start=True)
    # #     images = np.array(cmos.get_reflection_images(), dtype=np.float32)
    # #     for _ in range(2):
    # #         images += np.array(cmos.get_reflection_images(), dtype=np.float32)
    # #     images /= float(10.0)
    # #     images = np.array(np.clip(images, 0.0, 255.0), dtype=np.uint8)
    # #     obj_images.append(images)
    # #     for i, image in enumerate(images):
    # #         image_name = "Obj_G{:02d}_C{:02d}.png".format(v_i + 1, i + 1)
    # #         image_path = os.path.join(dir, image_name)
    # #         cv2.imwrite(image_path, image)
    #
    # # analysis
    # # avg_images = list()
    # # obj_images = list()
    # # for i in range(1):
    # #     this_avg_images = list()
    # #     this_obj_images = list()
    # #     for j in range(2):
    # #         avg_path = os.path.join("C:/Users/vclab/Desktop/galvanometer_setting2",
    # #                                 "Avg_G{:02d}_C{:02d}.png".format(i + 1, j + 1))
    # #         obj_path = os.path.join("C:/Users/vclab/Desktop/galvanometer_setting2",
    # #                                 "Obj_G{:02d}_C{:02d}.png".format(i + 1, j + 1))
    # #         this_avg_images.append(cv2.imread(avg_path))
    # #         this_obj_images.append(cv2.imread(obj_path))
    # #     avg_images.append(np.array(this_avg_images))
    # #     obj_images.append(np.array(this_obj_images))
    # # diff_images = np.array(obj_images, dtype=np.float32) - np.array(avg_images, dtype=np.float32)
    # # diff_images -= np.min(diff_images, axis=(2, 3), keepdims=True)
    # # # diff_images += 255.0
    # # diff_images = diff_images / np.max(diff_images, axis=(2, 3), keepdims=True)
    # # # diff_images /= (255.0 * 2)
    # # diff_images = np.array(np.clip(diff_images * 255.0, 0.0, 255.0), dtype=np.uint8)
    # # for i, images in enumerate(diff_images):
    # #     for j, image in enumerate(images):
    # #         image_name = "Diff_G{:02d}_C{:02d}.png".format(i + 1, j + 1)
    # #         image_path = os.path.join(dir, image_name)
    # #         cv2.imwrite(image_path, image)
    # # task.close()
    #
    # # x, y, a = 2.3, -0.6, 0.0
    # # turtlebot.command(x, y, a)
    #
    # # images_01 = cmos.get_reflection_images()
    # # images_02 = cmos.get_reflection_images()
    # images_01 = list()
    # images_02 = list()
    # for j in range(2):
    #     avg_path = os.path.join("C:/Users/vclab/Desktop/galvanometer_setting2",
    #                             "Test_C{:02d}.png".format(j + 1))
    #     obj_path = os.path.join("C:/Users/vclab/Desktop/galvanometer_setting2",
    #                             "Test2_C{:02d}.png".format(j + 1))
    #     images_01.append(cv2.imread(avg_path))
    #     images_02.append(cv2.imread(obj_path))
    #
    # diff_images = np.array(images_01, dtype=np.float32) - np.array(images_02, dtype=np.float32)
    # diff_images -= np.min(diff_images, axis=(1, 2), keepdims=True)
    # # diff_images += 255.0
    # diff_images = diff_images / np.max(diff_images, axis=(1, 2), keepdims=True)
    # # diff_images /= (255.0 * 2)
    # diff_images = np.array(np.clip(diff_images * 255.0, 0.0, 255.0), dtype=np.uint8)
    # for j, image in enumerate(diff_images):
    #     image_name = "TestDiff_C{:02d}.png".format(j + 1)
    #     image_path = os.path.join(dir, image_name)
    #     cv2.imwrite(image_path, image)
