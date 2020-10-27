import cv2
from data_generation.real_data.cmos.vimba import *
from data_generation.real_data.cmos.vimba.c_binding import *
import numpy as np
import sys
from typing import Optional

class CMOS():
    def __init__(self, config=None):

        self.config = config
        self.PIXEL_FORMATS_CONVERSIONS = {
            'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
            'PixelFormat.BayerRG8': cv2.COLOR_BAYER_RG2RGB
        }

        self.camera_ids = ["DEV_000F310382EB", "DEV_000F310382ED"]
    #### Camera ID #####
    # DEV_000F310382ED (Reflection Low) #
    # DEV_000F310382EC (GT)#
    # DEV_000F310382EB (Reflection High #
    ####################
    def setup_camera(self,cam: Camera):
        with cam:
            # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
            try:
                cam.GVSPAdjustPacketSize.run()

                while not cam.GVSPAdjustPacketSize.is_done():
                    pass

            except (AttributeError, VimbaFeatureError):
                pass

    def get_gt_image(self, cam_id): ## cam id string type
        image = self.take_pic(cam_id)
        return image

    def get_reflection_images(self): ## cam_id array with 2 strings
        # image_list = []
        # for i in range(len(self.camera_ids)):
        #     image_list.append(self.get_gt_image(self.camera_ids[i]))
        # return image_list

        frame_list = []

        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            count = len(cams)

            for i in range(count):
                with cams[i] as cam:
                    self.setup_camera(cam)
                    while True:
                        frame = cam.get_frame()
                        frame.convert_pixel_format(PixelFormat.Bgr8)
                        frame = frame.as_numpy_ndarray()
                        print(np.count_nonzero(frame))
                        if np.count_nonzero(frame) > 7000000:
                            break
                    frame_list.append(frame)
                    # print(np.count_nonzero(frame))
                    # frame.convert_pixel_format(PixelFormat.Bgr8)
                    # frame_list.append(frame.as_opencv_image())
        return frame_list


    def take_pic(self, cam_id=None): ## if want to take images from all cameras, leave the cam_id param blank.
        with Vimba.get_instance() as vimba:
            print(cam_id)
            if cam_id == None:
                cams = vimba.get_all_cameras()
                count = len(cams)
                print(count)

                for i in range(count):
                    with cams[i] as cam:
                        print(cam.get_id())
                        self.setup_camera(cam)
                        frame = cam.get_frame()
                        frame.convert_pixel_format(PixelFormat.Bgra8)
                        # print(frame.get_pixel_format().get_convertible_formats())
                        # image = cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[str(frame.get_pixel_format())])
                        fr2 = frame.as_numpy_ndarray()
                        print(fr2.shape)
                        print(fr2.dtype)
                        # frame.convert_pixel_format(PixelFormat.Mono8)
                        cv2.imwrite('./frame_%d.jpg' % i, frame.as_opencv_image())
            else:
                cam = vimba.get_camera_by_id('DEV_000F310382ED')
                with cam as cam:
                    self.setup_camera(cam)
                    frame = cam.get_frame()
                    frame.convert_pixel_format(PixelFormat.Rgba8)
                    # frame.convert_pixel_format(PixelFormat.Bgra8)
                    # print(frame.get_pixel_format().get_convertible_formats())
                    # image = cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[str(frame.get_pixel_format())])
                    fr2 = frame.as_numpy_ndarray()
                    print(fr2.shape)
                    print(fr2.dtype)
                    # frame.convert_pixel_format(PixelFormat.Mono8)
                    cv2.imwrite('./frame_%d.jpg' % 4, frame.as_opencv_image())
                return fr2

# cmos = CMOS()
# cmos.take_pic()

if __name__=="__main__":
    cmos =CMOS()
    image_list = cmos.get_reflection_images()
    for i in range(len(image_list)):
        # print(image_list[i].shape)
        # image = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2RGB)
        image = image_list[i]
        # print(image.shape)
        cv2.imwrite("image_%d.jpg" % i, image)
