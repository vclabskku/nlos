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

        s0o[NOelf.camera_ids = ["DEV_000F310382EB", "DEV_000F310382ED"]
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

    def get_reflection_images(self): ## cam_id array with 2 strings
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
                        # print(np.count_nonzero(frame))
                        if np.count_nonzero(frame) > 7000000:
                            break
                    frame_list.append(frame)
        return frame_list

if __name__=="__main__":
    cmos =CMOS()
    image_list = cmos.get_reflection_images()
    for i in range(len(image_list)):
        image = image_list[i]
        cv2.imwrite("image_%d.jpg" % i, image)
