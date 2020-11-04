# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
from PIL import Image
import os


class Depth():

    def __init__(self, config):
        self.config = config

    def get_depth_image(self):
        # Create a pipeline
        pipeline = rs.pipeline()
        # Create a config and configure the pipeline to stream
        #  different resolutions of color and depth streams
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # if not os.path.exists('./frame'):
        #    os.mkdir('./frame')
        # count = len(os.walk('C:/Users/vclab/PycharmProjects/nlos/data_generation/real_data/depth').__next__()[1])
        # filename = './frame/depth_{}'.format(count)
        # os.mkdir(filename)
        # config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 6)
        # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 6)

        # Start streaming
        profile = pipeline.start(config)
        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        # print("Depth Scale is: ", depth_scale)

        # We will be removing the background of objects more than
        #  clipping_distance_in_meters meters away
        clipping_distance_in_meters = 5  # 1 meter
        clipping_distance = clipping_distance_in_meters / depth_scale
        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        # Streaming loop
        try:
            # Get frameset of color and depthprint('4')

            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame

            # Get aligned frames
            depth_frame = frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            # Validate that both frames are valid
            if not depth_frame:
                print("ERROR : NO FRAME")
                return
            colorizer = rs.colorizer()
            depth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())

            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 153
            # depth_image_3d = np.dstack(
            #    (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
            # bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

            # Render images
            # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # images = np.hstack((bg_removed, depth_colormap))

            ### DEPTH ARRAY TO IMAGE ###

            filename = "C:/Users/vclab/PycharmProjects/nlos/data_generation/real_data/depth"
            cv2.imwrite('{}/DEPTH.png'.format(filename), depth_image)
            # print("success")
            # cv2.imwrite('{}/DEPTH.png'p.format(filename), images)
            # cv2.imwrite('{}/DEPTH.png'.format(filename), depth_colormap)

            return depth_image
        except:
            print('Exception Error')


        finally:
            pipeline.stop()

    def get_rgb(self):
        # Create a pipeline
        pipeline = rs.pipeline()

        # Create a config and configure the pipeline to stream
        #  different resolutions of color and depth streams
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        profile = pipeline.start(config)

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        # Streaming loop
        try:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame

            # Get aligned frames
            color_frame = frames.get_color_frame()

            # Validate that both frames are valid
            if not color_frame:
                print("ERROR : NO FRAME")
                return
            colorizer = rs.colorizer()
            color_image = np.asanyarray(color_frame.get_data())
            # print(color_image)
            return color_image

        finally:
            pipeline.stop()


if __name__ == "__main__":
    depth = Depth(config=None)
    depth.get_depth_image()
