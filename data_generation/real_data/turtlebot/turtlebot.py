import numpy as np
import os

class Turtlebot():

    def __init__(self, config):

        self.config = config

        x_min = self.config["area_range"][0][0]
        y_min = self.config["area_range"][0][1]
        x_max = self.config["area_range"][1][0]
        y_max = self.config["area_range"][1][1]
        x_num_cells = self.config["spatial_grid"][0]
        y_num_cells = self.config["spatial_grid"][1]

        self.x_coords = np.linspace(x_min, x_max, x_num_cells)
        self.y_coords = np.linspace(y_min, y_max, y_num_cells)
        self.angles = self.config["angles"]

        self.x_i = 0
        self.y_i = 0
        self.a_i = 0

    def move(self):
        x = self.x_coords[self.x_i]
        y = self.y_coords[self.y_i]
        a = self.angles[self.a_i]
        cmd = \
            "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
            "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals " \
            "&& simple_navigation_goals.exe {} {} {}".format(x, y, a)
        os.system(cmd)

        done = (self.x_i >= len(self.x_coords) - 1) and \
               (self.y_i >= len(self.y_coords) - 1) and \
               (self.a_i >= len(self.angles))
        return done, [x, y, a]