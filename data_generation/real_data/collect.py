
from data_generation.real_data.light.light import Light
from data_generation.real_data.turtlebot.turtlebot import Turtlebot
from data_generation.real_data.cmos.cmos import CMOS

class Collector():

    def __init__(self, config):

        self.config = config

        self.Light = Light(self.config["light_config"])
        self.Turtlebot = Turtlebot(self.config["turtlebot_config"])
        self.CMOS = CMOS(self.config["cmos_config"])

    def collect(self):

        turtlebot_done = False

        while turtlebot_done:
            # set light for gt
            self.Light.light_for_gt()

            # move the object to a point
            turtlebot_done = self.Turtlebot.move()

            # get gt rgb image
            gt_image = self.CMOS.get_gt_image()

            # get gt depth image

