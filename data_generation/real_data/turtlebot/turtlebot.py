import numpy as np
import subprocess

class Turtlebot():

    def __init__(self, config):

        self.config = config

        x_min = self.config["area_range"][0][0]
        y_min = self.config["area_range"][0][1]
        x_max = self.config["area_range"][1][0]
        y_max = self.config["area_range"][1][1]
        a_min = self.config["angle_range"][0]
        a_max = self.config["angle_range"][1]
        s_step = self.config["spatial_step"]
        a_step = self.config["angle_step"]

        self.x_coords = np.arange(x_min, x_max + 1, s_step)
        self.y_coords = np.arange(y_min, y_max + 1, s_step)
        self.angles = list()
        for angle in range(a_min, a_max, a_step):
            self.angles.append(angle)
            self.angles.append(angle + 180.0)

        self.index = 0
        self.l_x = len(self.x_coords)
        self.l_y = len(self.y_coords)
        self.l_a = len(self.angles)

    def move(self):
        x = self.x_coords[self.index // (self.l_y * self.l_a)]
        y = self.y_coords[(self.index // (self.l_a)) % self.l_y]
        a = self.angles[self.index % self.l_a]
        while True:
            cmd = \
                "cd C:\\ws\\turtlebot3\\devel && setup.bat && " \
                "cd C:\\ws\\turtlebot3\\devel\\lib\\simple_navigation_goals " \
                "&& simple_navigation_goals.exe {} {} {}".format(x, y, a)
            ok = subprocess.check_output(cmd.split())
            ok = bool(ok.decode().rstrip())
            if ok:
                break

        self.index += 1
        done = self.index >= self.l_x * self.l_y * self.l_a

        return done, [x, y, a]